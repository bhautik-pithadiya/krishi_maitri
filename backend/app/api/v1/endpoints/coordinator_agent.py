# app/api/v1/endpoints/coordinator_agent.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# Import the new service
from app.services.coordinator_service import get_holistic_advisory 

router = APIRouter()

class AdvisoryRequest(BaseModel):
    query: str
    lat: float
    lon: float
    state: str
    district: str
    market: str
    commodity: str

@router.post("/advisory", response_model=dict)
async def get_advisory_endpoint(request: AdvisoryRequest):
    """
    Single entry point for getting holistic agricultural advisory.
    """
    try:
        result = await get_holistic_advisory(**request.dict())
        return {"status": "success", "result": result}
    except Exception as e:
        # Add more specific error handling as needed
        raise HTTPException(status_code=500, detail=str(e))