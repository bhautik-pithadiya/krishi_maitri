from fastapi import APIRouter, HTTPException
from app.models.weather import WeatherRequest, WeatherResponse,WeatherAdviceResponse
from app.services.reasoning_agent import generate_farming_advice_gemini
import httpx
import os

router = APIRouter()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@router.post("/current", response_model=WeatherResponse)
async def get_weather_forecast(request: WeatherRequest):
    """
    Fetches the current weather for a given latitude and longitude.
    """
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key is not configured.")

    # Using the 'forecast' endpoint as you provided
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={request.lat}&lon={request.lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # The 'forecast' endpoint returns a 'list' of forecasts.
            # We will use the first item in the list for the main response,
            # but return the full list in 'details'.
            if data.get("list"):
                raise HTTPException(status_code=500, detail="Invalid response from weather provider.")

            first_forecast = data
            main_weather = first_forecast.get("weather", [{}])[0]
            
            # The location name is in the 'city' object for the forecast endpoint
            location_name = data.get("city", {}).get("name", "Unknown Location")

            return WeatherResponse(
                location=location_name,
                forecast=main_weather.get("description", "No forecast available."),
                temperature_celsius=first_forecast.get("main", {}).get("temp", 0.0),
                details=data # Return the full forecast data in the details field
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from weather provider: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@router.post("/forecast", response_model=WeatherResponse)
async def get_weather_forecast(request: WeatherRequest):
    """
    Fetches the 5-day weather forecast for a given latitude and longitude.
    """
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key is not configured.")

    # Using the 'forecast' endpoint as you provided
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={request.lat}&lon={request.lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # The 'forecast' endpoint returns a 'list' of forecasts.
            # We will use the first item in the list for the main response,
            # but return the full list in 'details'.
            if not data.get("list"):
                raise HTTPException(status_code=500, detail="Invalid response from weather provider.")

            first_forecast = data["list"][0]
            main_weather = first_forecast.get("weather", [{}])[0]
            
            # The location name is in the 'city' object for the forecast endpoint
            location_name = data.get("city", {}).get("name", "Unknown Location")

            return WeatherResponse(
                location=location_name,
                forecast=main_weather.get("description", "No forecast available."),
                temperature_celsius=first_forecast.get("main", {}).get("temp", 0.0),
                details=data # Return the full forecast data in the details field
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from weather provider: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@router.post("/forecast/advice", response_model=WeatherAdviceResponse)
async def get_weather_forecast_with_advice(request: WeatherRequest, language: str = "en"):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key is not configured.")
    
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={request.lat}&lon={request.lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        if not data.get("list"):
            raise HTTPException(status_code=500, detail="Invalid response from weather provider.")
        
        first_forecast = data["list"][0]
        main_weather = first_forecast.get("weather", [{}])[0]
        location_name = data.get("city", {}).get("name", "Unknown Location")

        # Get reasoning from Gemini
        advice = await generate_farming_advice_gemini(data, location_name, language)

        return WeatherAdviceResponse(
            location=location_name,
            forecast=main_weather.get("description", "No forecast available."),
            temperature_celsius=first_forecast.get("main", {}).get("temp", 0.0),
            # details=data,
            advice=advice
        )

