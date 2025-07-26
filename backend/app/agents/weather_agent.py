from .base import Agent

WEATHER_ANALYSIS_PROMPT = (
    "You are a weather analysis expert. Using the data {weather_data} and considering the farmer's question '{query}', "
    "provide short actionable advice about the weather."
)

weather_agent = Agent(WEATHER_ANALYSIS_PROMPT)

def analyze_weather(query: str, weather_data: dict) -> str:
    return weather_agent.run(query=query, weather_data=str(weather_data))
