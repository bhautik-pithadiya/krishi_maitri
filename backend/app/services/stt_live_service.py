import asyncio
import queue
import time
from typing import AsyncGenerator, Optional
import pyaudio
from google.cloud import speech
import logging

logger = logging.getLogger(__name__)

# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms


def get_current_time() -> int:
    """Return Current Time in MS."""
    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate: int = SAMPLE_RATE, chunk_size: int = CHUNK_SIZE) -> None:
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = None
        self._audio_stream = None

    def __enter__(self):
        self.closed = False
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._fill_buffer,
        )
        return self

    def __exit__(self, type, value, traceback):
        if self._audio_stream:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        if self._audio_interface:
            self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""
        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:
                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:
                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset) / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


class LiveSTTService:
    """Service for live speech-to-text transcription."""
    
    def __init__(self, language_code: str = "en-US"):
        self.language_code = language_code
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=language_code,
            max_alternatives=1,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )

    async def process_audio_stream(self, audio_data: bytes) -> AsyncGenerator[dict, None]:
        """Process audio stream and yield transcription results."""
        try:
            # Create a simple generator for the audio data
            def audio_generator():
                yield audio_data

            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator()
            )

            responses = self.client.streaming_recognize(self.streaming_config, requests)
            
            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence if result.alternatives[0].confidence else 0.0

                yield {
                    "transcript": transcript,
                    "is_final": result.is_final,
                    "confidence": confidence,
                    "timestamp": get_current_time()
                }

        except Exception as e:
            logger.error(f"Error in audio processing: {str(e)}")
            yield {
                "error": str(e),
                "timestamp": get_current_time()
            }

    async def start_live_transcription(self) -> AsyncGenerator[dict, None]:
        """Start live transcription from microphone."""
        mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
        
        try:
            with mic_manager as stream:
                while not stream.closed:
                    stream.audio_input = []
                    audio_generator = stream.generator()

                    requests = (
                        speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator
                    )

                    responses = self.client.streaming_recognize(self.streaming_config, requests)

                    for response in responses:
                        if get_current_time() - stream.start_time > STREAMING_LIMIT:
                            stream.start_time = get_current_time()
                            break

                        if not response.results:
                            continue

                        result = response.results[0]
                        if not result.alternatives:
                            continue

                        transcript = result.alternatives[0].transcript
                        
                        # Calculate corrected time
                        result_seconds = result.result_end_time.seconds if result.result_end_time.seconds else 0
                        result_micros = result.result_end_time.microseconds if result.result_end_time.microseconds else 0
                        
                        stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))
                        corrected_time = (
                            stream.result_end_time
                            - stream.bridging_offset
                            + (STREAMING_LIMIT * stream.restart_counter)
                        )

                        result_data = {
                            "transcript": transcript,
                            "is_final": result.is_final,
                            "confidence": result.alternatives[0].confidence if result.alternatives[0].confidence else 0.0,
                            "timestamp": corrected_time,
                            "system_time": get_current_time()
                        }

                        yield result_data

                        if result.is_final:
                            stream.is_final_end_time = stream.result_end_time
                            stream.last_transcript_was_final = True
                            
                            # Check for exit keywords
                            if any(word in transcript.lower() for word in ['exit', 'quit', 'stop']):
                                stream.closed = True
                                yield {
                                    "action": "exit",
                                    "message": "Transcription stopped by user command",
                                    "timestamp": get_current_time()
                                }
                                break
                        else:
                            stream.last_transcript_was_final = False

                    # Reset for next stream
                    if stream.result_end_time > 0:
                        stream.final_request_end_time = stream.is_final_end_time
                    stream.result_end_time = 0
                    stream.last_audio_input = stream.audio_input.copy()
                    stream.audio_input = []
                    stream.restart_counter += 1
                    stream.new_stream = True

        except Exception as e:
            logger.error(f"Error in live transcription: {str(e)}")
            yield {
                "error": str(e),
                "timestamp": get_current_time()
            }