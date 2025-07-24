from fastapi import APIRouter, HTTPException
from app.models.advisory import AdvisoryRequest, AdvisoryResponse
from app.services.advisory_agent import get_advisory

router = APIRouter()

@router.post("/", response_model=AdvisoryResponse)
async def get_holistic_advisory(request: AdvisoryRequest):
    """
    Provides a holistic advisory response to a farmer's query by synthesizing
    weather data, market prices, and information about government schemes.
    """
    try:
        result = await get_advisory(
            query=request.query,
            lat=request.lat,
            lon=request.lon,
            state=request.state,
            district=request.district,
            market=request.market,
            commodity=request.commodity
        )
        return AdvisoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate advisory: {str(e)}")