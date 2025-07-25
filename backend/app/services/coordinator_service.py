# app/services/coordinator_service.py

import httpx
import os
from dotenv import load_dotenv
from app.utils.prompt_manager import render_prompt
from app.services.gemini_client import call_gemini
# We will add the RAG tool here in Task 3
# from .rag_service import query_community_knowledge 

load_dotenv()

DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Tool 1: Get Weather Data
async def get_weather_data(lat: float, lon: float):
    """Fetches weather data from OpenWeatherMap."""
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

# Tool 2: Get Market Data
async def get_market_data(state: str, district: str, market: str, commodity: str):
    """Fetches market price data from data.gov.in."""
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": DATA_GOV_IN_API_KEY,
        "format": "json",
        "limit": 10, # Fetch recent records
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

# Main Orchestrator Logic
async def get_holistic_advisory(query: str, lat: float, lon: float, state: str, district: str, market: str, commodity: str) -> dict:
    """
    The main coordinator function. It calls tools and synthesizes a response.
    """
    # 1. Fetch data from all sources concurrently (or sequentially for simplicity first)
    weather_data = await get_weather_data(lat, lon)
    market_data = await get_market_data(state, district, market, commodity)

    # In Task 3, we will add the community knowledge tool call here
    # community_insights = await query_community_knowledge(query)

    # 2. Render the prompt with all the fetched data
    prompt = render_prompt(
        name="advisory_prompt",
        query=query,
        weather_data=str(weather_data),
        market_data=str(market_data),
        # community_insights=str(community_insights) # Add this in Task 3
    )

    # 3. Call Gemini to get the final synthesized response
    final_response = call_gemini(prompt)

    return {"response": final_response}