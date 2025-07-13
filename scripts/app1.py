import streamlit as st
import requests
from gtts import gTTS
import pandas as pd

# --------------------------------------------
# Language Selection
# --------------------------------------------
language = st.selectbox("Select Language / భాషను ఎంచుకోండి", ["English", "తెలుగు"])

# Crop mapping
CROP_MAPPING = {
    "paddy": "వరి", "maize": "మొక్కజొన్న", "cotton": "పత్తి",
    "groundnut": "వేరుశెనగ", "chilli": "మిరప", "sugarcane": "చెరకు",
    "banana": "అరటి", "brinjal": "వంకాయ", "tomato": "టమోటా",
    "mango": "మామిడి", "jowar": "జొన్న", "wheat": "గోధుమలు",
    "soybean": "సోయాబీన్", "sunflower": "సూర్యకాంతి", "onion": "ఉల్లిపాయ",
    "bajra": "సజ్జలు", "turmeric": "పసుపు"
}

# --------------------------------------------
# Dynamic Labels
# --------------------------------------------
if language == "English":
    labels = {
        "title": "🌱 Smart Crop Planner and MarketPlace Assistant",
        "district": "District", "soil": "Soil Type(s)", "season": "Season",
        "rainfall": "Rainfall (mm)", "groundwater": "Groundwater Level (m)",
        "duration": "Crop Duration (days)", "yield": "Yield (kg/ha)",
        "cost": "Cost of Cultivation (₹)", "recommend": "🚀 Recommend Crop",
        "result": "✅ Recommended Crop:", "profit": "📈 Predicted Profit: ₹",
        "forecast": "✅ Forecast generated!", "tts_button": "▶️ Speak",
        "forecast_crop": "Crop Name", "forecast_days": "Forecast Days"
    }
    districts = [
        "Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool",
        "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram",
        "West Godavari", "YSR Kadapa", "Alluri Sitarama Raju", "Anakapalli",
        "Annamayya", "Bapatla", "Eluru", "Kakinada", "Konaseema", "Nandyal",
        "Palnadu", "Parvathipuram Manyam", "Sri Potti Sriramulu Nellore",
        "Sri Sathya Sai", "Tirupati"
    ]
    soil_types = {
        "Loamy Soils": "loamy_soil.jpg",
        "Black Cotton Soils": "black_soil.jpg",
        "Shallow Red or Gravelly Soils": "shallow_red_or_gravelly_soils.jpg",
        "Sandy Loam": "sandy_loam_soil.jpg",
        "Alluvial Soils (Delta/Coastal)": "alluvial_soil_delta.jpg",
        "Clayey Deep Red Soils": "clayey_deep_red_soil.jpg",
        "Gravelly Clayey/Loamy Red Soils": "gravelly_clayey_loamy_red.jpg",
        "Red Loamy Soils": "red_loamy.jpg"
    }
    seasons = ["kharif", "rabi", "zaid"]

else:
    labels = {
        "title": "🌾 స్మార్ట్ క్రాప్ ప్లానర్ మరియు మార్కెట్ అసిస్టెంట్",
        "district": "జిల్లా", "soil": "నేల రకం", "season": "రుతువు",
        "rainfall": "వర్షపాతం (mm)", "groundwater": "భూగర్భ జలాల స్థాయి (మీ.)",
        "duration": "పంట వ్యవధి (రోజులు)", "yield": "దిగుబడి (kg/ha)",
        "cost": "వ్యయాలు (₹)", "recommend": "🚀 పంటను సూచించండి",
        "result": "✅ సూచించిన పంట:", "profit": "📈 అంచనా లాభం: ₹",
        "forecast": "✅ ధరల అంచనా సిద్ధమైంది!", "tts_button": "▶️ వినిపించు",
        "forecast_crop": "పంట పేరు", "forecast_days": "అంచనా రోజులు"
    }
    districts = [
        "శ్రీకాకుళం", "విజయనగరం", "విశాఖపట్నం", "అల్లూరి సీతారామరాజు", "పార్వతీపురం మన్యం",
        "అనకాపల్లి", "కాకినాడ", "తూర్పు గోదావరి", "కోనసీమ", "పశ్చిమ గోదావరి", "ఏలూరు",
        "కృష్ణా", "ఎన్‌టిఆర్", "గుంటూరు", "పల్నాడు", "బాపట్ల", "ప్రకాశం", "నెల్లూరు",
        "చిత్తూరు", "తిరుపతి", "అన్నమయ్య", "కడప", "అనంతపురం", "శ్రీ సత్య సాయి",
        "కర్నూలు", "నంద్యాల"
    ]
    soil_types = {
        "లోమీ నేలలు": "loamy_soil.jpg",
        "నలుపు పత్తి నేలలు": "black_soil.jpg",
        "ఎరుపు లేదా రాళ్లతో కూడిన నేలలు": "shallow_red_or_gravelly_soils.jpg",
        "గరిటె రేగడి నేల": "sandy_loam_soil.jpg",
        "ఒచ్చిన నేలలు (డెల్టా/తీర ప్రాంతం)": "alluvial_soil_delta.jpg",
        "కట్టె గోధుమ ఎరుపు నేలలు": "clayey_deep_red_soil.jpg",
        "రాళ్లతో కూడిన ఎరుపు నేలలు": "gravelly_clayey_loamy_red.jpg",
        "ఎరుపు లోమీ నేలలు": "red_loamy.jpg"
    }
    seasons = ["ఖరీఫ్", "రబీ", "జైద"]

# --------------------------------------------
# Soil Selection
# --------------------------------------------
soils = list(soil_types.keys())
selected_soils = st.multiselect(labels["soil"], soils)

combined_soil = ""  # FIX: initialize before use

if selected_soils:
    for soil in selected_soils:
        try:
            st.image("soil_images/" + soil_types[soil], caption=soil, width=200)
        except:
            st.warning(f"Image not found for {soil}")
    combined_soil = "-".join(sorted(selected_soils)) if len(selected_soils) > 1 else selected_soils[0]
else:
    st.warning("⚠️ Please select at least one soil type." if language == "English" else "దయచేసి కనీసం ఒక నేల రకాన్ని ఎంచుకోండి.")

# --------------------------------------------
# Input Form
# --------------------------------------------
st.title(labels["title"])
col1, col2 = st.columns(2)
with col1:
    district = st.selectbox(labels["district"], districts)
    season = st.selectbox(labels["season"], seasons)
with col2:
    rainfall = st.number_input(labels["rainfall"], min_value=0.0)
    groundwater = st.number_input(labels["groundwater"], min_value=0.0)
    duration = st.number_input(labels["duration"], min_value=30, max_value=400)
    yield_val = st.number_input(labels["yield"], min_value=0.0)
    cost = st.number_input(labels["cost"], min_value=0.0)

# --------------------------------------------
# Telugu Mapping Fix
# --------------------------------------------
if language == "తెలుగు":
    telugu_to_english = {
        "districts": dict(zip(districts, [
            "Srikakulam", "Vizianagaram", "Visakhapatnam", "Alluri Sitarama Raju", "Parvathipuram Manyam",
            "Anakapalli", "Kakinada", "East Godavari", "Konaseema", "West Godavari", "Eluru", "Krishna",
            "NTR", "Guntur", "Palnadu", "Bapatla", "Prakasam", "Nellore", "Chittoor", "Tirupati",
            "Annamayya", "Kadapa", "Anantapur", "Sri Sathya Sai", "Kurnool", "Nandyal"
        ])),
        "soils": dict(zip(soils, [
            "Loamy Soils", "Black Cotton Soils", "Shallow Red or Gravelly Soils", "Sandy Loam",
            "Alluvial Soils (Delta/Coastal)", "Clayey Deep Red Soils", "Gravelly Clayey/Loamy Red Soils", "Red Loamy Soils"
        ])),
        "seasons": {"ఖరీఫ్": "kharif", "రబీ": "rabi", "జైద": "zaid"}
    }

    district = telugu_to_english["districts"].get(district, district)
    season = telugu_to_english["seasons"].get(season, season)
    if combined_soil:
        combined_soil = telugu_to_english["soils"].get(combined_soil, combined_soil)

# --------------------------------------------
# API Call
# --------------------------------------------
if st.button(labels["recommend"]):
    if not combined_soil:
        st.warning("Please select a soil type to continue." if language == "English" else "దయచేసి నేల రకాన్ని ఎంచుకోండి.")
    else:
        payload = {
            "district": district,
            "season": season,
            "soil_type": combined_soil,
            "rainfall": rainfall,
            "groundwater": groundwater,
            "duration_days": duration,
            "yield_kg_per_ha": yield_val,
            "cost_of_cultivation": cost
        }

        try:
            response = requests.post("http://127.0.0.1:8000/agri-assistant", json=payload)
            if response.status_code == 200:
                result = response.json()
                crop = result["recommended_crop"]
                crop_display = CROP_MAPPING.get(crop.lower(), crop)
        

                st.success(f"{labels['result']} **{crop_display}**")
                st.success(f"{labels['profit']} {result['predicted_profit']} per hectare")

                if isinstance(result["forecast_price"], list):
                    df = pd.DataFrame(result["forecast_price"])
                    df["ds"] = pd.to_datetime(df["ds"])
                    st.line_chart(df.set_index("ds")["yhat"])
                    st.success(labels["forecast"])
                else:
                    st.info(result["forecast_price"])

                st.markdown("### 🏬 Nearest Market Locations")
                for mandi in result.get("nearby_mandis", []):
                    st.write("- ", mandi["name"])

                # Text to speech
                text = f"{labels['result']} {crop_display}, {labels['profit']} {result['predicted_profit']}"
                tts = gTTS(text=text, lang='te' if language == "తెలుగు" else 'en')
                tts.save("speak.mp3")
                st.audio("speak.mp3", format="audio/mp3")

            else:
                st.error(f"API Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"❌ Could not connect to API: {e}")



