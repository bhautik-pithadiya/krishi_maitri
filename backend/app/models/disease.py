from pydantic import BaseModel
from typing import Optional

class DiseaseRequest(BaseModel):
    image_url: str
    language: Optional[str] = "en"

class DiseaseResponse(BaseModel):
    status: str
    disease: Optional[str]
    recommendation: Optional[str]