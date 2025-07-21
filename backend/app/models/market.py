from pydantic import BaseModel

class MarketRequest(BaseModel):
    crop: str
    location: str

class MarketResponse(BaseModel):
    crop: str
    market: str
    price_per_kg: float
    trend: str