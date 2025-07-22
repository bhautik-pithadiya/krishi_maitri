from fastapi import APIRouter
from app.models.disease import DiseaseRequest, DiseaseResponse
from app.services.gemini_client import call_gemini
import json
from app.utils.prompt_manager import render_prompt
router = APIRouter()

@router.post("/predict", response_model=DiseaseResponse)
def predict_disease(request: DiseaseRequest):
    prompt = render_prompt(
        name="disease_prompt",
        image_url=request.image_url,
        crop_type=request.crop_type
    )
    ai_result = call_gemini(prompt)
    ai_result = json.loads(ai_result)
    if "disease" in ai_result and "recommendation" in ai_result:
        return DiseaseResponse(**ai_result)
    