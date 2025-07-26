from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, WebSocket
from app.models.transcribe import LiveTranscribeRequest, TranscribeResponse
from app.services.stt_client import TranscribeService
from app.utils.audio_convertor import m4a_to_wav_mono_bytes
import os
import base64
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

logger.info("Initializing TranscribeService")
transcribe_service = TranscribeService()

@router.post('/transcribe-file', response_model=TranscribeResponse)
async def test_transcribe_upload(file: UploadFile = File(...)):
    """Test endpoint: Upload an audio file and get transcription."""
    logger.info(f"Received test upload request for file: {file.filename}")
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            logger.warning(f"Invalid file type received: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Read file content as bytes
        logger.debug("Reading file content")
        audio_content = await file.read()
        
        # Get transcription
        logger.info("Starting transcription process")
        transcript, confidence, time_taken = transcribe_service.transcribe(audio_content)
        logger.info(f"Transcription completed with confidence: {confidence} in {time_taken:.3f} seconds")
        
        return TranscribeResponse(
            transcript=transcript,
            confidence=confidence,
            time_taken=time_taken
        )
    except Exception as e:
        logger.error(f"Error in test upload transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))