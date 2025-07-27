from app.models.disease import DiseaseRequest, DiseaseResponse
from app.services.gemini_client import call_gemini
from app.utils.prompt_manager import render_prompt
from app.services.gcs_service import upload_image_to_gcs
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import json
import re
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
        language =request.language or "en"
    )



    # Call the AI model and parse the result
    raw_result = call_gemini(prompt)
    # Extract the JSON block using regex
    print(f"Raw AI result: {raw_result}")
    match = re.search(r"(?:json)?\s*(\{.*?\})\s*", raw_result, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="No valid JSON block found in AI response.")

    json_str = match.group(1)

    print(f"Raw AI result: {json_str}")
    try:
        ai_result = json.loads(json_str)
        if isinstance(ai_result, dict) and "disease" in ai_result:
            # Ensure the response matches the DiseaseResponse model
            if ai_result["recommendation"] is None:
                return DiseaseResponse(**ai_result)
            else:
                return DiseaseResponse(**ai_result)
        else:
            raise HTTPException(status_code=422, detail="Incomplete AI response structure")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI response is not valid JSON: {str(e)}")
