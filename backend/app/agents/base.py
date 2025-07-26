from app.services.gemini_client import call_gemini

class Agent:
    """Simple Gemini-powered agent that formats a prompt and returns the result."""

    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template

    def run(self, **kwargs) -> str:
        prompt = self.prompt_template.format(**kwargs)
        return call_gemini(prompt)
