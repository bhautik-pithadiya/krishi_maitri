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