from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings
from app.services.voice_service import VoiceService

from app.api.websocket import ws_router

router = APIRouter()
router.include_router(ws_router)
voice_service = VoiceService()

class ChatRequest(BaseModel):
    message: str

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint to verify backend operation."""
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/agent/status", tags=["Agent"])
async def get_agent_status():
    """Returns agent service operational readiness status."""
    return voice_service.get_service_status()

@router.post("/agent/chat", tags=["Agent"])
async def agent_chat(payload: ChatRequest):
    """
    Mock voice text chat endpoint for testing Lyra Agent interactions.
    """
    result = voice_service.handle_voice_interaction(payload.message)
    return result
