import pandas as pd
import numpy as np

class CropRecommender:
    def __init__(self):
        self.groundwater_df = None
        self.rainfall_df = None
        self.soil_df = None
        self.crop_df = None
        self.mixed_df = None
        self.rules = {}

    def load_data(self):
        self.groundwater_df = pd.read_csv("GW_Levels_1750139546761.csv")
        self.rainfall_df = pd.read_csv("Rainfall_Summary_1750141935618.csv")
        self.soil_df = pd.read_csv("Soil_Crop_Suitability_AP.csv")
        self.crop_df = pd.read_csv("AP_Crop_Dataset.csv")
        self.mixed_df = pd.read_csv("district_mixed_cropping_suggestions.csv")
        self._preprocess_data()

    def _preprocess_data(self):
        dataframes = [self.groundwater_df, self.rainfall_df, self.soil_df, self.crop_df, self.mixed_df]
        for df in dataframes:
            numeric_cols = df.select_dtypes(include=np.number).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        if 'Soil_Type' in self.soil_df.columns:
            self.soil_df['Soil_Type'] = self.soil_df['Soil_Type'].astype('category')

    def define_rules(self):
        self.rules = {
            'Paddy': {
                'soil_type': ['Clay', 'Loamy'],
                'districts': ['East Godavari', 'West Godavari', 'Krishna', 'Guntur', 'Srikakulam'],
                'min_rainfall': 1000, 'max_rainfall': 1500,
                'min_groundwater': 5, 'max_groundwater': 15,
                'seasons': ['kharif']
            },
            'Wheat': {
                'soil_type': ['Loamy', 'Sandy'],
                'districts': ['Anantapur', 'Kurnool'],
                'min_rainfall': 500, 'max_rainfall': 800,
                'min_groundwater': 3, 'max_groundwater': 10,
                'seasons': ['rabi']
            },
            'Maize': {
                'soil_type': ['Sandy', 'Loamy'],
                'districts': ['Prakasam', 'Chittoor', 'Kurnool'],
                'min_rainfall': 600, 'max_rainfall': 1200,
                'min_groundwater': 4, 'max_groundwater': 12,
                'seasons': ['kharif', 'rabi']
            },
            'Chillies': {
                'soil_type': ['Black', 'Sandy Loam'],
                'districts': ['Guntur', 'Prakasam'],
                'min_rainfall': 600, 'max_rainfall': 900,
                'min_groundwater': 4, 'max_groundwater': 10,
                'seasons': ['rabi']
            },
            'Sugarcane': {
                'soil_type': ['Loamy', 'Alluvial'],
                'districts': ['East Godavari', 'West Godavari', 'Krishna'],
                'min_rainfall': 1000, 'max_rainfall': 1600,
                'min_groundwater': 6, 'max_groundwater': 15,
                'seasons': ['kharif']
            },
            'Tomato': { 
                'soil_type': ['Sandy loam', 'Clay loam'], 
                'districts': ['Chittoor', 'Kurnool'], 
                'min_rainfall': 500, 'max_rainfall': 2125, 
                'min_groundwater': 5, 'max_groundwater': 15, 
                'seasons': ['kharif', 'rabi', 'zaid'] 
            },
            'Sunflower': {
                'soil_type': ['Sandy Loam', 'Black'],
                'districts': ['Kurnool', 'Anantapur'],
                'min_rainfall': 400, 'max_rainfall': 800,
                'min_groundwater': 3, 'max_groundwater': 10,
                'seasons': ['rabi']
            },
            'Jowar': {
                'soil_type': ['Black', 'Loamy'],
                'districts': ['Anantapur', 'Kurnool'],
                'min_rainfall': 450, 'max_rainfall': 800,
                'min_groundwater': 2, 'max_groundwater': 9,
                'seasons': ['rabi']
            },
            'Bajra': {
                'soil_type': ['Sandy', 'Loamy'],
                'districts': ['Chittoor', 'Anantapur'],
                'min_rainfall': 300, 'max_rainfall': 600,
                'min_groundwater': 2, 'max_groundwater': 8,
                'seasons': ['kharif']
            },
            'Greengram': {
                'soil_type': ['Sandy Loam', 'Loamy'],
                'districts': ['Kurnool', 'Anantapur'],
                'min_rainfall': 400, 'max_rainfall': 600,
                'min_groundwater': 3, 'max_groundwater': 8,
                'seasons': ['kharif', 'rabi']
            },
            'Bengalgram': {
                'soil_type': ['Black', 'Loamy'],
                'districts': ['Kurnool', 'Kadapa'],
                'min_rainfall': 450, 'max_rainfall': 700,
                'min_groundwater': 3, 'max_groundwater': 9,
                'seasons': ['rabi']
            },
            'Groundnut': {
                'soil_type': ['Red Sandy', 'Loamy'],
                'districts': ['Anantapur', 'Chittoor'],
                'min_rainfall': 500, 'max_rainfall': 800,
                'min_groundwater': 3, 'max_groundwater': 9,
                'seasons': ['kharif']
            },
            'Cotton': {
                'soil_type': ['Black', 'Sandy Loam'],
                'districts': ['Prakasam', 'Kurnool'],
                'min_rainfall': 600, 'max_rainfall': 1000,
                'min_groundwater': 4, 'max_groundwater': 12,
                'seasons': ['kharif']
            },
            'Mango': {
                'soil_type': ['Well-drained loamy', 'Red'],
                'districts': ['Chittoor', 'Vizianagaram'],
                'min_rainfall': 700, 'max_rainfall': 1200,
                'min_groundwater': 4, 'max_groundwater': 10,
                'seasons': ['annual']
            },
            'Banana': {
                'soil_type': ['Alluvial', 'Loamy'],
                'districts': ['Krishna', 'West Godavari'],
                'min_rainfall': 1000, 'max_rainfall': 1500,
                'min_groundwater': 5, 'max_groundwater': 14,
                'seasons': ['annual']
            },
            'Corn': {
                'soil_type': ['Loamy', 'Sandy'],
                'districts': ['Prakasam', 'Kurnool'],
                'min_rainfall': 500, 'max_rainfall': 900,
                'min_groundwater': 3, 'max_groundwater': 10,
                'seasons': ['kharif', 'rabi']
            }
        }

    def recommend(self, soil_type: str, rainfall: float, groundwater: float, season: str, district: str = None):
        recommendations = {}
        for crop, rules in self.rules.items():
            # ✅ Skip crop if it's not grown in the selected season
            if season.lower() not in [s.lower() for s in rules.get("seasons", [])] and "annual" not in rules.get("seasons", []):
                continue

            score = 0
            if soil_type in rules['soil_type']:
                score += 30
            if rules['min_rainfall'] <= rainfall <= rules['max_rainfall']:
                score += 30
            if rules['min_groundwater'] <= groundwater <= rules['max_groundwater']:
                score += 30
            if district and district in rules['districts']:
                score += 10

            if score > 0:
                recommendations[crop] = min(score, 100)

        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

__all__ = ['CropRecommender']

