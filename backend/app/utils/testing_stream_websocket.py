import asyncio
import websockets
import time
import json
import os

async def send_audio():
    uri = "ws://127.0.0.1:8000/api/v1/stt_live/stream"
    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket connection established.")

        # Set your input audio file path (.wav or .webm)
        audio_file_path = "/mnt/D-drive/Cheating_App/ai-study-assistant/audio_files/output.wav"  # change if using webm
        if not os.path.exists(audio_file_path):
            print(f"❌ Error: Audio file not found at {audio_file_path}")
            return

        # Use appropriate chunk size (~1 second of 16-bit mono 48kHz PCM = 96,000 bytes)
        chunk_size = 48000 * 2  # 96 KB

        try:
            with open(audio_file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    await websocket.send(chunk)

                    # Optional: simulate real-time by adding delay (adjust as needed)
                    await asyncio.sleep(0.3)  # 300 ms delay

            print("📤 Finished sending audio.")

            # Keep receiving results until server closes the connection
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    try:
                        data = json.loads(response)
                        if data.get("is_final"):
                            print("📝 Final Transcript:", data["transcript"])
                        else:
                            print("⏳ Interim:", data["transcript"])
                    except json.JSONDecodeError:
                        print("⚠️ Received non-JSON response:", response)
                except asyncio.TimeoutError:
                    print("⏳ No more messages, assuming stream has ended.")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed by server.")
                    break

        except Exception as e:
            print(f"❌ An error occurred during audio streaming: {e}")

if __name__ == "__main__":
    asyncio.run(send_audio())
