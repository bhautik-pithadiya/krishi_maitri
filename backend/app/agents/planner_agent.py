from .base import Agent

PLANNER_PROMPT = (
    "You are a planning agent for an agricultural assistant. "
    "Given the farmer's query: '{query}', decide which of the following tasks are needed: "
    "WEATHER and/or MARKET. Respond with a comma separated list using lowercase names."
)

planner_agent = Agent(PLANNER_PROMPT)


def plan_tasks(query: str) -> list[str]:
    """Return a list of tasks suggested by the planner agent."""
    response = planner_agent.run(query=query)
    tasks = [task.strip().lower() for task in response.split(',') if task.strip()]
    return tasks
