import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.live_stt_service import LiveSTTService


class CLITranscriptionTester:
    def __init__(self):
        self.stt_service = LiveSTTService()

    async def test_live_transcription(self):
        """Test live transcription with CLI output."""
        print("🎤 Starting live transcription...")
        print("Speak into your microphone. Say 'exit', 'quit', or 'stop' to end.")
        print("=" * 60)

        try:
            async for result in self.stt_service.start_live_transcription():
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    break
                elif result.get("action") == "exit":
                    print(f"🔴 {result.get('message')}")
                    break
                else:
                    transcript = result.get("transcript", "")
                    is_final = result.get("is_final", False)
                    confidence = result.get("confidence", 0)
                    timestamp = result.get("timestamp", 0)

                    status = "FINAL" if is_final else "INTERIM"
                    status_color = "🟢" if is_final else "🟡"
                    
                    print(f"{status_color} [{status}] ({confidence:.2f}) [{timestamp}ms]: {transcript}")

        except KeyboardInterrupt:
            print("\n🔴 Transcription stopped by user")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

    async def test_with_specific_language(self, language_code: str):
        """Test transcription with a specific language."""
        print(f"🌍 Testing with language: {language_code}")
        self.stt_service = LiveSTTService(language_code=language_code)
        await self.test_live_transcription()


async def main():
    """Main CLI test function."""
    tester = CLITranscriptionTester()

    print("Live Speech-to-Text CLI Tester")
    print("=" * 40)
    print("1. Test with English (en-US)")
    print("2. Test with custom language")
    print("3. Exit")

    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        await tester.test_live_transcription()
    elif choice == "2":
        language_code = input("Enter language code (e.g., es-ES, fr-FR, de-DE): ").strip()
        if language_code:
            await tester.test_with_specific_language(language_code)
        else:
            print("Invalid language code")
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())