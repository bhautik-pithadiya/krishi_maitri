from pydantic import BaseModel

class DiseaseRequest(BaseModel):
    image_url: str
    crop_type: str

class DiseaseResponse(BaseModel):
    disease: str
    confidence: float
    recommendation: str