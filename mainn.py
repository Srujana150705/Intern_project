from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet
import joblib
from crop_recommender import CropRecommender
from mandi_locations import market_locations

app = FastAPI()

# --- Load Crop Recommender ---
recommender = CropRecommender()
recommender.load_data()
recommender.define_rules()

# --- Load Profit Prediction Model ---
profit_model = joblib.load("profit_predictor_model.pkl")  # Ensure this model is available
profit_features = joblib.load("profit_predictor_features.pkl")  # Load the features used for profit prediction

# --- Load and Preprocess Mandi Prices ---
forecast_df = pd.read_csv("ap_mandi_prices_synthetic.csv")
forecast_df = forecast_df.rename(columns={
    "Date": "ds",
    "Price": "y",
    "Crop": "crop",
    "District": "district"
})
forecast_df["ds"] = pd.to_datetime(forecast_df["ds"], dayfirst=True)

# --- Request Schemas ---
class CropRequest(BaseModel):
    soil_type: str
    rainfall: float
    groundwater: float
    district: str = None

class ProfitPredictionRequest(BaseModel):
    crop: str
    district: str
    season: str
    rainfall: float
    groundwater: float
    soil_type: str
    duration_days: int
    yield_kg_per_ha: float
    cost_of_cultivation: float

class ForecastRequest(BaseModel):
    district: str
    crop: str
    days_to_forecast: int = 30

# --- API Endpoints ---
@app.get("/")
def home():
    return {"message": "Welcome to the Smart Agri Assistant API!"}

@app.post("/recommend")
def recommend_crop(request: CropRequest):
    results = recommender.recommend(
        soil_type=request.soil_type,
        rainfall=request.rainfall,
        groundwater=request.groundwater,
        district=request.district
    )
    return {"recommendations": results}

# ✅ Profit Prediction
@app.post("/predict-profit")
def predict_profit(request: ProfitPredictionRequest):
    try:
        input_df = pd.DataFrame([{
            "Crop": request.crop,
            "District": request.district,
            "Season": request.season,
            "Rainfall": request.rainfall,
            "Groundwater": request.groundwater,
            "Soil_Type": request.soil_type,
            "Duration": request.duration_days,
            "Yield": request.yield_kg_per_ha,
            "Cost": request.cost_of_cultivation
        }])
        input_encoded = pd.get_dummies(input_df)
        input_encoded = input_encoded.reindex(columns=profit_features, fill_value=0)
        prediction = profit_model.predict(input_encoded)[0]
        return {"predicted_profit": round(float(prediction), 2)}
    except Exception as e:
        raise HTTPException(500, detail=f"Profit prediction failed: {e}")

@app.post("/forecast_price")
def forecast_price(request: ForecastRequest):
    crop_data = forecast_df[
        (forecast_df['crop'].str.lower() == request.crop.lower()) &
        (forecast_df['district'].str.lower() == request.district.lower())
    ][["ds", "y"]]

    if crop_data.empty:
        raise HTTPException(404, detail="No historical data found for selected crop and district.")

    model = Prophet()
    model.fit(crop_data)

    future = model.make_future_dataframe(periods=request.days_to_forecast)
    forecast = model.predict(future)
    forecast_result = forecast[["ds", "yhat"]].tail(request.days_to_forecast).to_dict(orient="records")

    return {"forecast": forecast_result}



