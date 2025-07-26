from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Krishi Maitri API",
    description="A multi-agent AI platform for actionable agricultural insights with Firebase Authentication",
    version="1.0.0"
)

# CORS configuration for frontend integration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"message": "Krishi Maitri API is running."}