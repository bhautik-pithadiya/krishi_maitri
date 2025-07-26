from pydantic import BaseModel

class LiveTranscribeRequest(BaseModel):
    audio_content: str
    audio_mime_type: str = "audio/webm;codecs=opus"


class TranscribeResponse(BaseModel):
    """Response model for live transcribe endpoint"""
    transcript: str
    confidence: float
    time_taken: float