from fastapi import APIRouter
from .endpoints import (
    disease_agent_router,
    weather_agent_router,
    market_agent_router,
    finance_agent_router,
    coordinator_agent_router,
    tts_router,
    stt_router,
    auth_router
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Agent endpoints
api_router.include_router(coordinator_agent_router, prefix="/coordinator", tags=["Coordinator Agent"])
api_router.include_router(disease_agent_router, prefix="/disease", tags=["Disease Agent"])
api_router.include_router(weather_agent_router, prefix="/weather", tags=["Weather Agent"])
api_router.include_router(market_agent_router, prefix="/market", tags=["Market Agent"])
api_router.include_router(finance_agent_router, prefix="/finance", tags=["Finance Agent"])

# WebSocket endpoints
api_router.include_router(tts_router, prefix="/tts", tags=["TTS"])
api_router.include_router(stt_router, prefix="/stt", tags=["STT"])