from google.cloud import speech

class TranscribeService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe(self, audio_content: bytes) -> tuple[str, float]:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # sample_rate_hertz=8000,
            language_code="en-US",
            model="latest_short",  # Chosen model
        )
        response = self.client.recognize(config=config, audio=audio)

        # Check if results list is not empty before accessing
        if response.results:
            # Check if alternatives list is not empty
            if response.results[0].alternatives:
                alternative = response.results[0].alternatives[0]
                return alternative.transcript, alternative.confidence
            else:
                # Handle case with empty alternatives
                print("Warning: Transcription result has no alternatives.")
                return "", 0.0
        else:
            # Handle case with empty results
            print("Warning: Transcription returned no results.")
            return "", 0.0
    