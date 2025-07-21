from fastapi import FastAPI
from app.api.v1 import api_router

app = FastAPI()

# API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"message": "Krishi Maitri API is running."}