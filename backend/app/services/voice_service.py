"""
voice_service.py — REST-based voice service layer for Lyra Agent.

Used by the /agent/chat and /agent/status HTTP endpoints.
The primary interaction path is via WebSocket (/ws/voice).
"""
from typing import Dict, Any
from app.config import settings
from app.agent.lyra_agent import LyraAgent


class VoiceService:
    """
    Voice service layer for orchestrating Lyra Agent interactions via HTTP.
    The real-time path goes through the WebSocket endpoint.
    """

    def __init__(self) -> None:
        self.agent = LyraAgent()
        self.is_active = True

    def get_service_status(self) -> Dict[str, Any]:
        """Returns operational readiness status for all service components."""
        llm_configured = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
        aai_configured = bool(settings.ASSEMBLYAI_API_KEY and settings.ASSEMBLYAI_API_KEY.strip())

        return {
            "service": "VoiceService",
            "phase": "Phase 3 — Lyra Intelligence & Tool Calling",
            "active": self.is_active,
            "stt_engine": {
                "provider": "AssemblyAI Realtime STT v3",
                "configured": aai_configured,
                "status": "ready" if aai_configured else "missing_api_key",
            },
            "llm_engine": {
                "provider": "OpenAI",
                "model": settings.LLM_MODEL,
                "configured": llm_configured,
                "status": "ready" if llm_configured else "fallback_mode",
                "note": (
                    "LLM tool calling active"
                    if llm_configured
                    else "No OPENAI_API_KEY — using deterministic local fallback"
                ),
            },
            "tools": [
                "scene_understanding",
                "crowd_analysis",
                "navigation_recommendation",
                "safety_check",
            ],
            "vision_engine": "Not implemented (Phase 4+)",
        }

    def handle_voice_interaction(self, text_transcript: str) -> Dict[str, Any]:
        """
        Synchronous REST path: processes a text query through the Lyra Agent.
        Used by the /agent/chat endpoint for testing and demo scenarios.
        """
        return self.agent.process_message(text_transcript)
