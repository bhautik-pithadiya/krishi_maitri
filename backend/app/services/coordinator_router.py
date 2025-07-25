from app.services.gemini_client import call_gemini
from app.services.tts_client import text_to_speech
from app.services.stt_client import speech_to_text
# Import other agents as needed

async def route_request(task_type: str, payload: dict):
    if task_type == "disease_diagnosis":
        # This should call the predict_disease logic, which uses Gemini
        # This is a simplified example. In reality, you'd call the endpoint or refactor the logic.
        from app.api.v1.endpoints.disease_agent import predict_disease_logic
        return predict_disease_logic(payload)
    elif task_type == "generate_voice":
        text = payload.get("text", "")
        return await text_to_speech(text)
    elif task_type == "transcribe_audio":
        audio_bytes = payload.get("audio", b"")
        return await speech_to_text(audio_bytes)
    elif task_type == "advisory":
        from app.services.coordinator_service import get_holistic_advisory
        return await get_holistic_advisory(**payload)
    else:
        raise ValueError(f"Unsupported task_type: {task_type}")