
from pydantic import BaseModel
from typing import List, Dict, Optional

class WeatherRequest(BaseModel):
    lat: float
    lon: float
    location: Optional[str] = None 

class WeatherResponse(BaseModel):
    location: str
    forecast: str
    temperature_celsius: float
    details: dict

class AdviceResponse(BaseModel):
    summary: str
    reasoning: str
    recommended_actions: List[str]

class WeatherAdviceResponse(BaseModel):
    location: str
    forecast: str
    temperature_celsius: float
    details: Optional[dict] = None
    advice: AdviceResponse
