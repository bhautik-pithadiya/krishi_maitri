from pydantic import BaseModel
from typing import Optional

class AdvisoryRequest(BaseModel):
    query: str
    lat: float
    lon: float
    state: str
    district: str
    market: str
    commodity: str

class AdvisoryResponse(BaseModel):
    response: str