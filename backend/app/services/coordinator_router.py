from app.services.gemini_client import call_gemini
from app.services.tts_client import text_to_speech
from app.services.stt_client import speech_to_text
# Import other agents as needed

async def route_request(task_type: str, payload: dict):
    if task_type == "disease_diagnosis":
        # Call disease_agent logic
        return await process_gemini_request(payload)
    elif task_type == "generate_voice":
        return await generate_tts(payload)
    elif task_type == "transcribe_audio":
        return await transcribe_audio(payload)
    elif task_type == "finance_summary":
        # You can build out the call to finance_agent
        pass
    else:
        raise ValueError(f"Unsupported task_type: {task_type}")
