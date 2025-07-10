from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from prophet import Prophet
from datetime import datetime
from mandi_locations import market_locations
import uvicorn

# Load rule-based crop data
try:
    soil_df = joblib.load("C:/Users/sruja/OneDrive/Documents/project_api/soil_data.pkl")
except Exception as e:
    raise RuntimeError(f" Failed to load soil_data.pkl: {e}")

# Load profit prediction model and columns
try:
    profit_model = joblib.load("C:/Users/sruja/OneDrive/Documents/project_api/profit_predictor_model.pkl")
    profit_features = joblib.load("C:/Users/sruja/OneDrive/Documents/project_api/profit_predictor_features.pkl")
    profit_target = joblib.load("C:/Users/sruja/OneDrive/Documents/project_api/profit_predictor_target.pkl")
except Exception as e:
    raise RuntimeError(f" Failed to load profit model files: {e}")

# Load synthetic mandi price dataset
try:
    mandi_df = pd.read_csv("ap_mandi_prices_synthetic.csv")
    mandi_df["Date"] = pd.to_datetime(mandi_df["Date"], format="%d-%m-%Y")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load mandi price data: {e}")

app = FastAPI(title="Smart Crop Planner API")

# -------------------- Request Models --------------------
class CropRecommendationRequest(BaseModel):
    soil_type: str
    rainfall: float
    groundwater: float

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

# -------------------- Endpoints --------------------

@app.get("/")
def home():
    return {"message": "✅ Smart Crop Planner API is running"}

# ✅ Rule-Based Crop Recommendation
@app.post("/recommend-crop")
def recommend_crop(request: CropRecommendationRequest):
    try:
        df = soil_df.copy()
        # Use correct column name: "Soil Type" not "Soil_Type"
        filtered = df[
            (df["Soil Type"] == request.soil_type) &
            (df["Rainfall"] >= request.rainfall - 100) &
            (df["Rainfall"] <= request.rainfall + 100) &
            (df["Groundwater"] >= request.groundwater - 1) &
            (df["Groundwater"] <= request.groundwater + 1)
        ]
        crops = filtered["Crop"].unique().tolist()
        return {"recommended_crops": crops or ["No suitable crop found"]}
    except Exception as e:
        raise HTTPException(500, detail=f"Recommendation failed: {e}")

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

# ✅ Price Forecast + Market Suggestions
@app.post("/forecast-price")
def forecast_price(request: ForecastRequest):
    try:
        crop_data = mandi_df[
            (mandi_df["District"] == request.district) &
            (mandi_df["Crop"] == request.crop)
        ]
        if len(crop_data) < 10:
            raise HTTPException(404, detail="Not enough data to forecast")

        df = crop_data[["Date", "Price"]].rename(columns={"Date": "ds", "Price": "y"})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=request.days_to_forecast)
        forecast = model.predict(future)

        forecast_out = forecast[["ds", "yhat"]].tail(request.days_to_forecast)
        output = [{"date": d.strftime('%Y-%m-%d'), "price": round(p, 2)} for d, p in zip(forecast_out.ds, forecast_out.yhat)]

        nearby_markets = market_locations.get(request.district, {}).get("mandis", [])
        return {
            "forecast": output,
            "markets": nearby_markets
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Forecast failed: {e}")


# -------------------- Run the app --------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


