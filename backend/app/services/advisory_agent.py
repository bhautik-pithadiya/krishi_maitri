import httpx
import os
from dotenv import load_dotenv
from app.utils.prompt_manager import render_prompt
from app.services.gemini_client import call_gemini

load_dotenv()

DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# In a real app, you would have a robust system to ingest and update documents.
# For now, we will leave it empty. A user could trigger ingestion via an endpoint.
# knowledge_agent.ingest_documents(urls=["https://agriwelfare.gov.in/en/MajorSchemes"])


async def get_weather_data(lat: float, lon: float):
    """Fetches weather data from OpenWeatherMap."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}


async def get_market_data(state: str, district: str, market: str, commodity: str):
    """Fetches market price data from data.gov.in."""
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
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}


async def get_advisory(query: str, lat: float, lon: float, state: str, district: str, market: str, commodity: str) -> dict:
    """
    Generates agricultural advisory by fetching and synthesizing data.
    """
    # 1. Fetch data from all sources concurrently
    weather_data = await get_weather_data(lat, lon)
    market_data = await get_market_data(state, district, market, commodity)

    # 3. Render the prompt with all the fetched data
    prompt = render_prompt(
        name="advisory_prompt",
        query=query,
        weather_data=str(weather_data),
        market_data=str(market_data),
    )

    # 4. Call Gemini to get the final advisory response
    final_response = call_gemini(prompt)

    return {"response": final_response}