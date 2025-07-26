import asyncio
import base64
import websockets
import sounddevice as sd
import numpy as np

# Audio settings
SAMPLE_RATE = 16000  # Google STT preferred
CHUNK_DURATION = 1.0  # seconds per chunk
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

async def send_audio():
    uri = "ws://127.0.0.1:8000/api/v1/stt_live/stream"

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket. Start speaking... (Ctrl+C to stop)")

        loop = asyncio.get_running_loop()  # ✅ Main loop reference

        try:
            def callback(indata, frames, time, status):
                if status:
                    print(f"Stream status: {status}")
                # Convert float32 -> int16 PCM
                pcm_data = (indata * 32767).astype(np.int16).tobytes()
                audio_base64 = base64.b64encode(pcm_data).decode()
                # ✅ Schedule coroutine in main loop
                asyncio.run_coroutine_threadsafe(websocket.send(audio_base64), loop)

            # Start recording from mic
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=callback):
                while True:
                    response = await websocket.recv()
                    print("Transcription:", response)

        except KeyboardInterrupt:
            print("\nStopping stream...")
            await websocket.send("END")  # Signal server
            await websocket.close()

asyncio.run(send_audio())
