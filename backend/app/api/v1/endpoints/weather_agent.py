from fastapi import APIRouter
from app.models.weather import WeatherRequest, WeatherResponse

router = APIRouter()

@router.post("/forecast", response_model=WeatherResponse)
def get_weather_forecast(request: WeatherRequest):
    # Dummy logic for demonstration
    return WeatherResponse(
        location=request.location,
        forecast="Rain expected in 2 days. Prepare drainage.",
        temperature=28.5
    )