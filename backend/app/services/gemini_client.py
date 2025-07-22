import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv(override=True)

GEMINI_KEY = os.getenv("GEMINI_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=GEMINI_KEY)

def call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text if hasattr(response, 'text') else str(response)