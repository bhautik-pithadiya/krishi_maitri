import asyncio
from typing import AsyncIterable
from google.cloud import speech_v1p1beta1 as speech

client = speech.SpeechClient()


def _config(language_code: str) -> speech.RecognitionConfig:
    """Return recognition config with multiple regional languages."""
    return speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        alternative_language_codes=[
            "hi-IN",
            "en-IN",
            "bn-IN",
            "gu-IN",
            "kn-IN",
            "ml-IN",
            "mr-IN",
            "pa-IN",
            "ta-IN",
            "te-IN",
        ],
        enable_automatic_punctuation=True,
    )


async def speech_to_text(audio_bytes: bytes, language_code: str = "hi-IN") -> str:
    """Transcribe a block of audio bytes using Google STT."""

    def _recognize() -> str:
        audio = speech.RecognitionAudio(content=audio_bytes)
        response = client.recognize(config=_config(language_code), audio=audio)
        return " ".join(r.alternatives[0].transcript for r in response.results)

    return await asyncio.to_thread(_recognize)


async def speech_to_text_from_file(file_path: str, language_code: str = "hi-IN") -> str:
    """Convenience wrapper to transcribe an audio file."""
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    return await speech_to_text(audio_bytes, language_code)


async def streaming_speech_to_text(
    chunks: AsyncIterable[bytes], language_code: str = "hi-IN"
) -> str:
    """Transcribe audio streamed in chunks."""
    collected = [chunk async for chunk in chunks]

    def _stream() -> str:
        requests = (
            speech.StreamingRecognizeRequest(audio_content=c) for c in collected
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=_config(language_code),
            interim_results=False,
        )
        responses = client.streaming_recognize(streaming_config, requests)
        transcripts = []
        for response in responses:
            for result in response.results:
                transcripts.append(result.alternatives[0].transcript)
        return " ".join(transcripts)

    return await asyncio.to_thread(_stream)
