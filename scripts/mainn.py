from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet
import joblib
from crop_recommender import CropRecommender
from mandi_locations import market_locations
from schemas import RecommendRequest, UnifiedRequest  # ✅ use updated schemas

# Create FastAPI app
app = FastAPI()

# Load Crop Recommender
recommender = CropRecommender()
recommender.load_data()
recommender.define_rules()

# Load profit prediction model
model_bundle = joblib.load("profit_with_target.pkl")
profit_model = model_bundle["model"]
profit_model_columns = model_bundle["feature_columns"]

# Load and preprocess forecast dataset
forecast_df = pd.read_csv("ap_mandi_prices_for_prophet.csv")
forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

# Crop normalization mapping
CROP_ALIASES = {
    "chillies": "chilli",
    "brinjals": "brinjal",
    "tomatoes": "tomato",
    "groundnuts": "groundnut",
    "mangoes": "mango",
    "bananas": "banana"
}

# ----------------- Routes -----------------

@app.get("/")
def home():
    return {"message": "✅ Smart Agri Assistant API is running"}

@app.post("/recommend-crop")
def recommend_crop(req: RecommendRequest):
    results = recommender.recommend(
        soil_type=req.soil_type,
        rainfall=req.rainfall,
        groundwater=req.groundwater,
        season=req.season,
        district=req.district
    )

    if not results:
        raise HTTPException(status_code=404, detail="No suitable crop found.")

    top_crop = results[0][0]
    return {"recommended_crop": top_crop, "all_recommendations": results}

@app.post("/agri-assistant")
def agri_assistant(request: UnifiedRequest):
    try:
        # Step 1: Crop Recommendation
        crop_results = recommender.recommend(
            soil_type=request.soil_type,
            rainfall=request.rainfall,
            groundwater=request.groundwater,
            season=request.season,
            district=request.district
        )

        if not crop_results:
            raise HTTPException(status_code=404, detail="No suitable crop found.")

        top_crop = crop_results[0][0]
        normalized_crop = CROP_ALIASES.get(top_crop.strip().lower(), top_crop.strip().lower())

        # Step 2: Profit Prediction
        profit_input_df = pd.DataFrame([{
            "Crop": top_crop,
            "District": request.district,
            "Season": request.season,
            "Rainfall": request.rainfall,
            "Groundwater": request.groundwater,
            "Soil_Type": request.soil_type,
            "Duration": request.duration_days,
            "Yield": request.yield_kg_per_ha,
            "Cost": request.cost_of_cultivation
        }])

        profit_input_encoded = pd.get_dummies(profit_input_df)
        profit_input_encoded = profit_input_encoded.reindex(columns=profit_model_columns, fill_value=0)
        profit_prediction = profit_model.predict(profit_input_encoded)[0]

        # Step 3: Price Forecasting
        crop_data = forecast_df[
            (forecast_df['crop'].str.lower().str.strip() == normalized_crop) &
            (forecast_df['district'].str.lower().str.strip() == request.district.lower().strip())
        ][["ds", "y"]]

        if crop_data.empty:
            forecast_result = "No price data available for forecasting."
        else:
            model = Prophet()
            model.fit(crop_data)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            forecast_result = forecast[["ds", "yhat"]].tail(10).to_dict(orient="records")

        # Step 4: Mandi Suggestions
        mandis = market_locations.get(request.district, {}).get("mandis", [])
        mandi_recommendations = [{"name": mandi} for mandi in mandis]

        return {
            "recommended_crop": top_crop,
            "predicted_profit": round(float(profit_prediction), 2),
            "forecast_price": forecast_result,
            "nearby_mandis": mandi_recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in agri-assistant: {str(e)}")




