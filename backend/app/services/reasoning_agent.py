import google.generativeai as genai
from app.core.config import GEMINI_API_KEY
from app.services.gemini_client import call_gemini

# Initialize Gemini
# genai.configure(api_key=GEMINI_API_KEY)

async def generate_farming_advice_gemini(forecast_data: dict, location: str, language: str = "en") -> dict:
    """
    Generate actionable farming advice using Gemini model.
    """
    

    prompt = f"""
    You are an agricultural expert assisting farmers.
    Analyze the weather forecast data and provide:
    1. Short summary of upcoming weather
    2. Reasoning why this matters for farming
    3. 3 clear actionable steps for farmers
    Language: {language}

    Forecast Data:
    {forecast_data["list"][:5]}

    Give response in the following format:
    Summary: <summary>
    Reasoning: <reasoning>
    Recommended Actions:
    - <action 1>
    - <action 2>
    - <action 3>
    Location: {location}

    """
    print(f"Prompt for Gemini:\n{prompt}\n")
    response = call_gemini(prompt)
    print(response)
    text = response 

    # Simple parsing: Expect model to return structured text
    return {
        "summary": extract_section(text, "Summary"),
        "reasoning": extract_section(text, "Reasoning"),
        "recommended_actions": extract_actions(text)
    }

def extract_section(text: str, section: str) -> str:
    # Simple parsing helper
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if section.lower() in line.lower():
            return lines[i+1].strip() if i+1 < len(lines) else ""
    return ""

def extract_actions(text: str) -> list:
    actions = []
    for line in text.split("\n"):
        if line.strip().startswith(("-", "•", "1", "2", "3")):
            actions.append(line.strip("-•0123456789. ").strip())
    return actions[:3]
