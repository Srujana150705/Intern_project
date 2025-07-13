from pydantic import BaseModel, Field

# For crop recommendation
class RecommendRequest(BaseModel):
    district: str = Field(..., min_length=2, description="District name")
    season: str = Field(..., min_length=2, description="Season")
    soil_type: str = Field(..., min_length=2, description="Soil type")
    rainfall: float = Field(..., gt=0, description="Rainfall in mm")
    groundwater: float = Field(..., ge=0, description="Groundwater level")
    duration_days: int = Field(..., gt=0, description="Crop duration in days")

# For agri assistant (extended features)
class UnifiedRequest(RecommendRequest):
    yield_kg_per_ha: float = Field(..., gt=0, description="Expected yield in kg/ha")
    cost_of_cultivation: float = Field(..., gt=0, description="Cost of cultivation in Rs/ha")

