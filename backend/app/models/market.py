from pydantic import BaseModel, Field
from typing import Optional, List

class MarketRequest(BaseModel):
    state: str
    district: str
    market: str
    commodity: str

class MarketPriceRecord(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    arrival_date: str
    min_price: str
    max_price: str
    modal_price: str

class MarketResponse(BaseModel):
    records: List[MarketPriceRecord]