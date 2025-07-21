from fastapi import APIRouter
from app.models.market import MarketRequest, MarketResponse

router = APIRouter()

@router.post("/prices", response_model=MarketResponse)
def get_market_prices(request: MarketRequest):
    # Dummy logic for demonstration
    return MarketResponse(
        crop=request.crop,
        market="Local Mandi",
        price_per_kg=24.5,
        trend="Rising"
    )