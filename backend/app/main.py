from fastapi import FastAPI
from app.api.v1 import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="/mnt/D-drive/Sphinx/krishi_maitri/backend/static"), name="static")

@app.get("/")
async def index():
    return FileResponse(os.path.join("/mnt/D-drive/Sphinx/krishi_maitri/backend/static", "realtime_stt.html"))

# API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/live-stt")
async def serve_live_stt_page():
    """Serve the live STT HTML page."""
    return FileResponse('static/realtime_stt.html')