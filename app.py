import streamlit as st
import requests

st.set_page_config(page_title="Smart Crop Planner", layout="wide")

st.title("🌱 Smart Crop Planner and MarketPlace Assistant")

# --------------------------------------------
# Static Lists
# --------------------------------------------
districts = [
    "Srikakulam", "Vizianagaram", "Visakhapatnam", "Alluri Sitarama Raju",
    "Parvathipuram Manyam", "Anakapalli", "Kakinada", "East Godavari",
    "Konaseema", "West Godavari", "Eluru", "Krishna",
    "NTR", "Guntur", "Palnadu", "Bapatla",
    "Prakasam", "Nellore", "Chittoor", "Tirupati",
    "Annamayya", "Kadapa", "Anantapur", "Sri Sathya Sai",
    "Kurnool", "Nandyal"
]

soil_types = [
    "Loamy Soils", "Black Cotton Soils", "Shallow Red or Gravelly Soils",
    "Sandy Loam", "Alluvial Soils (Delta/Coastal)", "Clayey Deep Red Soils",
    "Gravelly Clayey/Loamy Red Soils", "Red Loamy Soils"
]

seasons = ["kharif", "rabi", "zaid"]

API_URL = "http://127.0.0.1:8000"  # Update if deployed

# --------------------------------------------
# Tabs for Features
# --------------------------------------------
tab1, tab2, tab3 = st.tabs(["🌾 Crop Recommendation", "💰 Profit Prediction", "📈 Price Forecast"])

# --------------------------------------------
# Crop Recommendation Tab
# --------------------------------------------
with tab1:
    st.subheader("🌾 Crop Recommendation")

    col1, col2 = st.columns(2)
    with col1:
        district = st.selectbox("District", districts)
        season = st.selectbox("Season", seasons)
        soil = st.selectbox("Soil Type", soil_types)
    with col2:
        rainfall = st.number_input("Rainfall (mm)", min_value=0.0)
        groundwater = st.number_input("Groundwater Level (m)", min_value=0.0)
        duration = st.number_input("Crop Duration (days)", min_value=30, max_value=400)

    if st.button("🚀 Recommend Crop"):
        payload = {
            "district": district,
            "season": season,
            "soil_type": soil,
            "rainfall": rainfall,
            "groundwater": groundwater,
            "duration_days": duration
        }

        try:
            response = requests.post(f"{API_URL}/recommend-crop", json=payload)
            if response.status_code == 200:
                crop = response.json()["recommended_crop"]
                st.success(f"✅ Recommended Crop: **{crop}**")
            else:
                st.error(f"❌ Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"❌ Could not connect to API: {e}")

# --------------------------------------------
# Profit Prediction Tab
# --------------------------------------------
with tab2:
    st.subheader("💰 Profit Prediction")

    col1, col2 = st.columns(2)
    with col1:
        crop = st.text_input("Crop Name (e.g. Paddy)")
        district2 = st.selectbox("District", districts, key="district2")
        season2 = st.selectbox("Season", seasons, key="season2")
        soil2 = st.selectbox("Soil Type", soil_types, key="soil2")
    with col2:
        rainfall2 = st.number_input("Rainfall (mm)", min_value=0.0, key="rainfall2")
        groundwater2 = st.number_input("Groundwater Level (m)", min_value=0.0, key="gw2")
        duration2 = st.number_input("Crop Duration (days)", min_value=30, max_value=400, key="duration2")
        yield_val = st.number_input("Yield (kg/ha)", min_value=0.0)
        cost = st.number_input("Cost of Cultivation (₹)", min_value=0.0)

    if st.button("📊 Predict Profit"):
        payload = {
            "crop": crop,
            "district": district2,
            "season": season2,
            "soil_type": soil2,
            "rainfall": rainfall2,
            "groundwater": groundwater2,
            "duration_days": duration2,
            "yield_kg_per_ha": yield_val,
            "cost_of_cultivation": cost
        }

        try:
            response = requests.post(f"{API_URL}/predict-profit", json=payload)
            if response.status_code == 200:
                profit = response.json()["predicted_profit"]
                st.success(f"✅ Predicted Profit: ₹{profit}")
            else:
                st.error(f"❌ Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"❌ Could not connect to API: {e}")

# --------------------------------------------
# Forecast Price Tab
# --------------------------------------------
with tab3:
    st.subheader("📈 Price Forecast")

    col1, col2 = st.columns(2)
    with col1:
        forecast_district = st.selectbox("District", districts, key="forecast_district")
    with col2:
        forecast_crop = st.text_input("Crop Name (e.g. Paddy)", key="forecast_crop")
        days = st.slider("Forecast Days", min_value=7, max_value=90, value=30)

    if st.button("🔮 Forecast Prices"):
        payload = {
            "district": forecast_district,
            "crop": forecast_crop,
            "days_to_forecast": days
        }

        try:
            response = requests.post(f"{API_URL}/forecast-price", json=payload)
            if response.status_code == 200:
                data = response.json()["forecast"]
                st.success("✅ Forecast generated!")

                # Plot
                import pandas as pd
                import matplotlib.pyplot as plt

                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)

                st.line_chart(df['price'])
            else:
                st.error(f"❌ Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"❌ Could not connect to API: {e}")

