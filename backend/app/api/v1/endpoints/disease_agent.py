from app.models.disease import DiseaseRequest, DiseaseResponse
from app.services.gemini_client import call_gemini
from app.utils.prompt_manager import render_prompt
from app.services.gcs_service import upload_image_to_gcs
from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
import json
import os

load_dotenv()

BUCKET_NAME = os.environ["BUCKET_NAME"]
router = APIRouter()

@router.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    """
    Uploads an image to GCP and returns the public URL.
    """
    url = upload_image_to_gcs(file,BUCKET_NAME)
    return {"image_url": url}

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
    