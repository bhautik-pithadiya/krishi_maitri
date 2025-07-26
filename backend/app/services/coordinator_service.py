"""Service to coordinate multiple Gemini-powered agents."""

from app.services.data_tools import fetch_weather_data, fetch_market_data
from app.agents.planner_agent import plan_tasks
from app.agents.weather_agent import analyze_weather
from app.agents.market_agent import analyze_market
from app.agents.summary_agent import summarize


async def get_holistic_advisory(
    query: str,
    lat: float,
    lon: float,
    state: str,
    district: str,
    market: str,
    commodity: str,
) -> dict:
    """Coordinate planner, weather and market agents to answer a farmer query."""

    tasks = plan_tasks(query)
    weather_text = ""
    market_text = ""

    if "weather" in tasks:
        weather_data = await fetch_weather_data(lat, lon)
        weather_text = analyze_weather(query, weather_data)

    if "market" in tasks:
        market_data = await fetch_market_data(state, district, market, commodity)
        market_text = analyze_market(query, market_data)

    final_response = summarize(query, weather_text, market_text)
    return {"response": final_response}
