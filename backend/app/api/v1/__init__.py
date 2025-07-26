from fastapi import APIRouter
from .endpoints import (
    disease_agent_router,
    weather_agent_router,
    market_agent_router,
    finance_agent_router,
    coordinator_agent_router,
    advisory_agent_router, # New
    tts_router,
    stt_file_router,
    stt_ws_router
)

api_router = APIRouter()
api_router.include_router(coordinator_agent_router, prefix="/coordinator", tags=["Coordinator Agent"])
api_router.include_router(advisory_agent_router, prefix="/advisory", tags=["Advisory Agent"]) # New
api_router.include_router(disease_agent_router, prefix="/disease", tags=["Disease Agent"])
api_router.include_router(weather_agent_router, prefix="/weather", tags=["Weather Agent"])
api_router.include_router(market_agent_router, prefix="/market", tags=["Market Agent"])
api_router.include_router(finance_agent_router, prefix="/finance", tags=["Finance Agent"])

api_router.include_router(tts_router, prefix="/tts", tags=["TTS"])
api_router.include_router(stt_file_router, prefix="/stt_test", tags=["STT"])
api_router.include_router(stt_ws_router, prefix="/stt_live", tags=["STT"])
