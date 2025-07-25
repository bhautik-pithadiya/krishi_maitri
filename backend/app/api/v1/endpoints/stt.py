from fastapi import APIRouter, WebSocket, UploadFile, File, WebSocketDisconnect
from app.services.stt_client import (
    speech_to_text,
    streaming_speech_to_text,
)

router = APIRouter()

@router.websocket("/ws/stt")
async def websocket_stt(websocket: WebSocket):
    await websocket.accept()
    async def chunk_generator():
        try:
            while True:
                chunk = await websocket.receive_bytes()
                yield chunk
        except WebSocketDisconnect:
            return

    transcript = await streaming_speech_to_text(chunk_generator())
    await websocket.send_text(transcript)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file."""
    audio_bytes = await file.read()
    text = await speech_to_text(audio_bytes)
    return {"transcript": text}
