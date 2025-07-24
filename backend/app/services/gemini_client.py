import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv(override=True)

GEMINI_KEY = os.getenv("GEMINI_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro") # Default to gemini-pro

genai.configure(api_key=GEMINI_KEY)

def call_gemini(prompt: str) -> str:
    """Calls the Gemini API with the given prompt."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not get a response from the AI model."