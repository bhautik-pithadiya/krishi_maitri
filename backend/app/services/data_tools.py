import httpx
import os
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def fetch_weather_data(lat: float, lon: float):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Weather API HTTP error: {e.response.text}")
            return {"error": "Could not fetch weather data."}
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return {"error": "An unexpected error occurred while fetching weather data."}

async def fetch_market_data(state: str, district: str, market: str, commodity: str):
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": DATA_GOV_IN_API_KEY,
        "format": "json",
        "limit": 10,
        "filters[state]": state,
        "filters[district]": district,
        "filters[market]": market,
        "filters[commodity]": commodity,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Market Data API HTTP error: {e.response.text}")
            return {"error": "Could not fetch market data."}
        except Exception as e:
            print(f"Market Data API error: {str(e)}")
            return {"error": "An unexpected error occurred while fetching market data."}
