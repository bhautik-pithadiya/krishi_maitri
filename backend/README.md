# Krishi Maitri Backend

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI app:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

- `app/` - Main backend application code
- `tests/` - Test cases
- `scripts/` - Utility scripts

## Speech-to-Text

The backend integrates with **Google Cloud Speech-to-Text**. Set the
`GOOGLE_APPLICATION_CREDENTIALS` environment variable to your service account
JSON file before running the app. A WebSocket endpoint is available at
`/api/v1/stt/ws/stt` for streaming recognition, and `/api/v1/stt/transcribe` can
be used to transcribe uploaded audio files.