from fastapi import APIRouter, HTTPException
from app.models.market import MarketRequest, MarketResponse
import httpx
import os

router = APIRouter()
DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")

@router.post("/prices", response_model=MarketResponse)
async def get_market_prices(request: MarketRequest):
    """
    Fetches real-time market prices for a given commodity and location.
    """
    if not DATA_GOV_IN_API_KEY:
        raise HTTPException(status_code=500, detail="Market data API key is not configured.")

    # CORRECTED URL: Removed markdown formatting
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": DATA_GOV_IN_API_KEY,
        "format": "json",
        "limit": 50, # Get more records to find the specific market
        "filters[state]": request.state,
        "filters[district]": request.district,
        "filters[commodity]": request.commodity,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # The API filters are sometimes broad, so we'll filter again for the specific market
            filtered_records = [
                record for record in data.get("records", []) 
                if record.get("market", "").lower() == request.market.lower()
            ]
            
            if not filtered_records:
                 return MarketResponse(records=[])

            return MarketResponse(records=filtered_records)

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from market data provider: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")