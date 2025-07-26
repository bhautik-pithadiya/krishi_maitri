from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
import asyncio
from typing import Dict, List
import base64

from app.services.stt_live_service import LiveSTTService

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.transcription_sessions: Dict[WebSocket, LiveSTTService] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.transcription_sessions[websocket] = LiveSTTService()
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.transcription_sessions:
            del self.transcription_sessions[websocket]
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

manager = ConnectionManager()


@router.websocket("/live-transcription")
async def websocket_live_transcription(websocket: WebSocket):
    """WebSocket endpoint for live speech-to-text transcription."""
    await manager.connect(websocket)
    stt_service = manager.transcription_sessions[websocket]
    
    try:
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "Connected to live transcription service",
            "timestamp": stt_service.client.__class__.__name__
        }, websocket)

        # Start live transcription in background
        transcription_task = asyncio.create_task(
            start_live_transcription_task(websocket, stt_service)
        )

        # Listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "stop_transcription":
                    transcription_task.cancel()
                    await manager.send_personal_message({
                        "type": "transcription_stopped",
                        "message": "Transcription stopped by client request"
                    }, websocket)
                    break
                elif message.get("type") == "audio_data":
                    # Handle audio data if sent from client
                    audio_data = base64.b64decode(message.get("data", ""))
                    async for result in stt_service.process_audio_stream(audio_data):
                        await manager.send_personal_message({
                            "type": "transcription_result",
                            "data": result
                        }, websocket)
                elif message.get("type") == "change_language":
                    # Change transcription language
                    language_code = message.get("language", "en-US")
                    stt_service = LiveSTTService(language_code=language_code)
                    manager.transcription_sessions[websocket] = stt_service
                    await manager.send_personal_message({
                        "type": "language_changed",
                        "message": f"Language changed to {language_code}"
                    }, websocket)
                        
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Server error: {str(e)}"
        }, websocket)
    finally:
        if not transcription_task.done():
            transcription_task.cancel()
        manager.disconnect(websocket)


async def start_live_transcription_task(websocket: WebSocket, stt_service: LiveSTTService):
    """Background task for live transcription."""
    try:
        async for result in stt_service.start_live_transcription():
            await manager.send_personal_message({
                "type": "transcription_result",
                "data": result
            }, websocket)
            
            # If exit command received, break the loop
            if result.get("action") == "exit":
                break
                
    except asyncio.CancelledError:
        logger.info("Transcription task cancelled")
    except Exception as e:
        logger.error(f"Error in transcription task: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Transcription error: {str(e)}"
        }, websocket)


@router.websocket("/audio-transcription")
async def websocket_audio_transcription(websocket: WebSocket):
    """WebSocket endpoint for audio data transcription (client sends audio)."""
    await manager.connect(websocket)
    stt_service = manager.transcription_sessions[websocket]
    
    try:
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "Connected to audio transcription service"
        }, websocket)

        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio_chunk":
                    # Decode base64 audio data
                    audio_data = base64.b64decode(message.get("data", ""))
                    
                    # Process audio chunk
                    async for result in stt_service.process_audio_stream(audio_data):
                        await manager.send_personal_message({
                            "type": "transcription_result",
                            "data": result
                        }, websocket)
                        
                elif message.get("type") == "stop":
                    break
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                logger.error(f"Error processing audio: {str(e)}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)

    except WebSocketDisconnect:
        logger.info("Client disconnected from audio transcription")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)


@router.get("/connection-info")
async def get_connection_info():
    """Get current WebSocket connection information."""
    return {
        "active_connections": len(manager.active_connections),
        "endpoints": {
            "live_transcription": "/api/v1/stt/live-transcription",
            "audio_transcription": "/api/v1/stt/audio-transcription"
        },
        "supported_message_types": [
            "stop_transcription",
            "audio_data", 
            "change_language",
            "audio_chunk",
            "stop"
        ]
    }