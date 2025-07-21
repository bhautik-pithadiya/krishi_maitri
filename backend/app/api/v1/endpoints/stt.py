from fastapi import APIRouter, WebSocket
from app.services.stt_client import speech_to_text

router = APIRouter()

@router.websocket("/ws/stt")
async def websocket_stt(websocket: WebSocket):
    await websocket.accept()
    while True:
        audio_bytes = await websocket.receive_bytes()
        text = await speech_to_text(audio_bytes)
        await websocket.send_text(text)