import asyncio
import json
import websockets
import base64
import wave
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveSTTWebSocketTester:
    def __init__(self, ws_url: str = "ws://localhost:8000/api/v1/stt/live-transcription"):
        self.ws_url = ws_url
        self.websocket = None

    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info(f"Connected to {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket")

    async def listen_for_messages(self):
        """Listen for messages from the WebSocket server."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error listening for messages: {str(e)}")

    async def handle_message(self, message: dict):
        """Handle incoming messages from the server."""
        msg_type = message.get("type")
        
        if msg_type == "connection_established":
            logger.info(f"✅ {message.get('message')}")
        elif msg_type == "transcription_result":
            data = message.get("data", {})
            transcript = data.get("transcript", "")
            is_final = data.get("is_final", False)
            confidence = data.get("confidence", 0)
            timestamp = data.get("timestamp", 0)
            
            status = "FINAL" if is_final else "INTERIM"
            logger.info(f"🎤 [{status}] ({confidence:.2f}) {transcript}")
            
            if data.get("action") == "exit":
                logger.info("🔴 Exit command detected, stopping...")
                await self.send_stop_command()
                
        elif msg_type == "error":
            logger.error(f"❌ Error: {message.get('message')}")
        elif msg_type == "transcription_stopped":
            logger.info(f"⏹️ {message.get('message')}")
        else:
            logger.info(f"📨 {msg_type}: {message}")

    async def send_stop_command(self):
        """Send stop transcription command."""
        if self.websocket:
            stop_message = {"type": "stop_transcription"}
            await self.websocket.send(json.dumps(stop_message))
            logger.info("Sent stop command")

    async def send_audio_file(self, file_path: str):
        """Send audio file data to the server for transcription."""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())
                encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                
                message = {
                    "type": "audio_data",
                    "data": encoded_audio
                }
                
                await self.websocket.send(json.dumps(message))
                logger.info(f"Sent audio file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error sending audio file: {str(e)}")

    async def test_live_transcription(self, duration: int = 30):
        """Test live transcription for a specified duration."""
        if not await self.connect():
            return

        logger.info(f"Testing live transcription for {duration} seconds...")
        logger.info("Speak into your microphone. Say 'exit' or 'quit' to stop early.")

        try:
            # Start listening for messages
            listen_task = asyncio.create_task(self.listen_for_messages())
            
            # Wait for the specified duration or until the task completes
            await asyncio.wait_for(listen_task, timeout=duration)
            
        except asyncio.TimeoutError:
            logger.info(f"Test completed after {duration} seconds")
            await self.send_stop_command()
        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
            await self.send_stop_command()
        finally:
            await self.disconnect()

    async def test_audio_file_transcription(self, file_path: str):
        """Test transcription of an audio file."""
        # Connect to audio transcription endpoint
        audio_ws_url = self.ws_url.replace("live-transcription", "audio-transcription")
        
        try:
            websocket = await websockets.connect(audio_ws_url)
            logger.info(f"Connected to audio transcription endpoint")

            # Listen for messages in background
            async def listen():
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_message(data)

            listen_task = asyncio.create_task(listen())

            # Send audio file
            with wave.open(file_path, 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())
                encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                
                message = {
                    "type": "audio_chunk",
                    "data": encoded_audio
                }
                
                await websocket.send(json.dumps(message))
                logger.info(f"Sent audio file: {file_path}")

            # Wait a bit for processing
            await asyncio.sleep(5)

            # Send stop command
            await websocket.send(json.dumps({"type": "stop"}))
            
            # Wait for final results
            await asyncio.sleep(2)
            
            listen_task.cancel()
            await websocket.close()

        except Exception as e:
            logger.error(f"Error in audio file test: {str(e)}")


async def main():
    """Main test function."""
    tester = LiveSTTWebSocketTester()

    print("Choose test type:")
    print("1. Live transcription (microphone)")
    print("2. Audio file transcription")
    
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        duration = int(input("Enter test duration in seconds (default 30): ") or 30)
        await tester.test_live_transcription(duration)
    elif choice == "2":
        file_path = input("Enter path to audio file (WAV format): ").strip()
        if file_path:
            await tester.test_audio_file_transcription(file_path)
        else:
            print("No file path provided")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())