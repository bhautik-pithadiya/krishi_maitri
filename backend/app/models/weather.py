
from pydantic import BaseModel
from typing import Optional

class WeatherRequest(BaseModel):
    lat: float
    lon: float
    location: Optional[str] = None 

class WeatherResponse(BaseModel):
    location: str
    forecast: str
    temperature_celsius: float
    details: dict