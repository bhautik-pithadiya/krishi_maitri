from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
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
        transcript, confidence = transcribe_service.transcribe(audio_content)
        logger.info(f"Transcription completed with confidence: {confidence}")
        
        return TranscribeResponse(
            transcript=transcript,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in test upload transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe", response_model=TranscribeResponse)
async def live_transcribe(request: LiveTranscribeRequest):
    """
    Transcribe live audio stream.

    Args:
        request: LiveTranscribeRequest with audio_content as hex string and mime_type.

    Returns:
        LiveTranscribeResponse
    """
    logger.info("Received live transcribe request")
    try:
        # Use audio_content directly as it's already bytes thanks to Pydantic
        logger.debug("Decoding base64 audio content")
        audio_bytes = base64.b64decode(request.audio_content)
        
        # Get transcription and confidence by unpacking the tuple
        logger.info("Starting live transcription process")
        transcript, confidence = transcribe_service.transcribe(audio_bytes)
        logger.info(f"Live transcription completed with confidence: {confidence}")
        
        return TranscribeResponse(
            transcript=transcript,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in live transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription service error: {str(e)}") 