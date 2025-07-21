from fastapi import APIRouter, WebSocket
from app.services.tts_client import text_to_speech

router = APIRouter()

@router.websocket("/ws/tts")
async def websocket_tts(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        audio_bytes = await text_to_speech(data)
        await websocket.send_bytes(audio_bytes)