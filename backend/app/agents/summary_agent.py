from .base import Agent

SUMMARY_PROMPT = (
    "You are an expert agricultural advisor summarizing inputs from different agents. "
    "Using the farmer's question '{query}', the weather advice '{weather}', and the market advice '{market}', "
    "write a final concise recommendation."
)

summary_agent = Agent(SUMMARY_PROMPT)

def summarize(query: str, weather: str, market: str) -> str:
    return summary_agent.run(query=query, weather=weather, market=market)
