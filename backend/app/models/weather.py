from pydantic import BaseModel

class WeatherRequest(BaseModel):
    location: str
    date: str

class WeatherResponse(BaseModel):
    location: str
    forecast: str
    temperature: float