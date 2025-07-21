from fastapi import APIRouter
from app.models.disease import DiseaseRequest, DiseaseResponse
from app.services.gemini_client import call_gemini

router = APIRouter()

@router.post("/predict", response_model=DiseaseResponse)
def predict_disease(request: DiseaseRequest):
    prompt = f"Diagnose disease for crop {request.crop_type} from image {request.image_url}"
    ai_result = call_gemini(prompt)
    # Dummy parse for demonstration
    return DiseaseResponse(
        disease="Blight",  # Replace with ai_result parsing
        confidence=0.92,
        recommendation="Apply recommended fungicide and monitor crops."
    )