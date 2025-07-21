from fastapi import APIRouter
from .endpoints import (
    disease_agent_router,
    weather_agent_router,
    market_agent_router,
    finance_agent_router,
    tts_router,
    stt_router
)

api_router = APIRouter()
api_router.include_router(disease_agent_router, prefix="/disease", tags=["Disease Agent"])
api_router.include_router(weather_agent_router, prefix="/weather", tags=["Weather Agent"])
api_router.include_router(market_agent_router, prefix="/market", tags=["Market Agent"])
api_router.include_router(finance_agent_router, prefix="/finance", tags=["Finance Agent"])
api_router.include_router(tts_router, tags=["TTS"])
api_router.include_router(stt_router, tags=["STT"])