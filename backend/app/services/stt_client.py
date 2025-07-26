from google.cloud import speech
import time

class TranscribeService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe(self, audio_content: bytes) -> tuple[str, float, float]:
        start_time = time.monotonic()
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # sample_rate_hertz=48000,
            language_code="en-US",
            model="latest_short",  # Chosen model
        )
        response = self.client.recognize(config=config, audio=audio)
        elapsed = time.monotonic() - start_time

        # Check if results list is not empty before accessing
        if response.results:
            # Check if alternatives list is not empty
            if response.results[0].alternatives:
                alternative = response.results[0].alternatives[0]
                return alternative.transcript, alternative.confidence, elapsed
            else:
                # Handle case with empty alternatives
                print("Warning: Transcription result has no alternatives.")
                return "", 0.0, elapsed
        else:
            # Handle case with empty results
            print("Warning: Transcription returned no results.")
            return "", 0.0, elapsed
    