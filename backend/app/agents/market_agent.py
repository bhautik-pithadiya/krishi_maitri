from .base import Agent

MARKET_ANALYSIS_PROMPT = (
    "You are a market price analyst. Given the data {market_data} and the farmer's question '{query}', "
    "give short advice about market trends."
)

market_agent = Agent(MARKET_ANALYSIS_PROMPT)

def analyze_market(query: str, market_data: dict) -> str:
    return market_agent.run(query=query, market_data=str(market_data))
