import asyncio
import websockets
import soundfile as sf
import numpy as np

# Config
SERVER_URI = "ws://127.0.0.1:8000/api/v1/stt_live/stream"
AUDIO_FILE = "tests/audios/testing.wav"
SAMPLE_RATE = 8000  # Must match what server/Google expects
CHUNK_DURATION = 2.0  # Seconds per chunk

async def send_audio_file():
    async with websockets.connect(SERVER_URI) as websocket:
        print(f"Connected to WebSocket: {SERVER_URI}")
        print(f"Sending audio file: {AUDIO_FILE}")

        # ✅ Read the entire audio file
        data, samplerate = sf.read(AUDIO_FILE, dtype='float32')

        if samplerate != SAMPLE_RATE:
            print(f"Warning: File sample rate {samplerate} != expected {SAMPLE_RATE}. Resampling might be required.")

        # ✅ Convert stereo to mono if necessary
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        # ✅ Split audio into chunks
        chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
        num_chunks = len(data) // chunk_size
        print(f"Sending {num_chunks} chunks of {CHUNK_DURATION}s each...")

        for i in range(num_chunks):
            chunk = data[i * chunk_size : (i + 1) * chunk_size]
            pcm_data = (chunk * 32767).astype(np.int16).tobytes()

            await websocket.send(pcm_data)
            print(f"Sent chunk {i+1}/{num_chunks}")

            # ✅ Try to receive any available transcripts after sending chunk
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.3)
                    print("Transcript:", response)
            except asyncio.TimeoutError:
                pass  # No transcript yet, move to next chunk

        print("All chunks sent. Waiting for final transcripts...")

        # ✅ Receive any remaining transcripts
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print("Final Transcript:", response)
        except asyncio.TimeoutError:
            print("No more transcripts. Closing...")

        await websocket.close()

if __name__ == "__main__":
    asyncio.run(send_audio_file())
