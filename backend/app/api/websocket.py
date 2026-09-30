"""
websocket.py — FastAPI WebSocket endpoint for Lyra real-time voice interaction.

Architecture:
  Browser Microphone (PCM16 16 kHz)
    → FastAPI WebSocket /api/v1/ws/voice
    → AssemblyAI Realtime STT v3
    → Lyra Agent (LLM + WalkJourney Tools)
    → Structured JSON events → React frontend

Preserved WebSocket event types:
  session_started | partial_transcript | final_transcript | error | session_ended | lyra_response
"""
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings
from app.services.assemblyai_realtime_service import AssemblyAIRealtimeService
from app.agent.lyra_agent import LyraAgent

logger = logging.getLogger(__name__)
ws_router = APIRouter()
lyra_agent = LyraAgent()


@ws_router.websocket("/ws/voice")
async def voice_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interaction.

    Event flow:
      1. Browser connects and streams PCM16 audio.
      2. Audio is forwarded to AssemblyAI Streaming STT v3.
      3. AssemblyAI returns partial and final transcripts.
      4. On final_transcript → Lyra Agent (LLM + Tools) is invoked.
      5. Structured lyra_response event is sent back to the browser.
    """
    await websocket.accept()
    logger.info("Browser WebSocket connected to /ws/voice.")

    # ── Guard: require AssemblyAI key ──────────────────────────────────
    if not settings.ASSEMBLYAI_API_KEY or not settings.ASSEMBLYAI_API_KEY.strip():
        logger.error("ASSEMBLYAI_API_KEY is not configured.")
        await websocket.send_json({
            "type": "error",
            "message": (
                "AssemblyAI API key is missing on the server. "
                "Please configure ASSEMBLYAI_API_KEY in backend/.env"
            ),
        })
        await websocket.close(code=1008)
        return

    service = AssemblyAIRealtimeService()

    try:
        await service.connect()
    except Exception as exc:
        logger.error(f"Failed to connect to AssemblyAI STT v3: {exc}")
        await websocket.send_json({
            "type": "error",
            "message": f"Could not connect to AssemblyAI Speech Recognition: {str(exc)}",
        })
        await websocket.close(code=1011)
        return

    # ── Task 1: Browser → AssemblyAI (audio forwarding) ────────────────
    async def handle_browser_to_assemblyai():
        try:
            while True:
                message = await websocket.receive()
                if "bytes" in message and message["bytes"]:
                    await service.send_audio(message["bytes"])
                elif "text" in message and message["text"]:
                    text_data = message["text"].strip().lower()
                    if "terminate" in text_data or "close" in text_data:
                        logger.info("Received termination signal from browser.")
                        break
        except WebSocketDisconnect:
            logger.info("Browser WebSocket disconnected (audio task).")
        except Exception as err:
            logger.warning(f"Error in browser audio forwarding task: {err}")

    # ── Task 2: AssemblyAI events → Browser + Lyra Agent ───────────────
    async def handle_assemblyai_to_browser():
        try:
            async for event in service.receive_events():
                event_type = event.get("type")

                # Always forward the raw STT event to the browser first
                # Preserved events: session_started, partial_transcript, final_transcript,
                #                   error, session_ended
                try:
                    await websocket.send_json(event)
                except Exception as send_err:
                    logger.warning(f"Failed to send STT event to browser: {send_err}")
                    return

                # On final transcript — invoke Lyra Agent (LLM + Tools)
                if event_type == "final_transcript" and event.get("text"):
                    user_text = event["text"]
                    logger.info(
                        f"[WS] Final transcript received: '{user_text}'. "
                        f"Invoking Lyra Agent..."
                    )

                    try:
                        agent_result = await lyra_agent.process_message_async(user_text)

                        lyra_event = {
                            "type": "lyra_response",
                            "user_text": user_text,
                            "response": agent_result.get("response", ""),
                            "tools_used": agent_result.get("tools_used", []),
                            "telemetry": agent_result.get("telemetry"),
                            "scenario": agent_result.get("scenario"),
                            "status": agent_result.get("status", "success"),
                        }

                        logger.info(
                            f"[WS] Lyra response dispatched. "
                            f"Tools used: {agent_result.get('tools_used', [])}. "
                            f"Status: {agent_result.get('status')}."
                        )

                        await websocket.send_json(lyra_event)

                    except WebSocketDisconnect:
                        logger.info("Browser disconnected before Lyra response could be sent.")
                        return
                    except Exception as agent_err:
                        logger.error(f"[WS] Lyra Agent error for query '{user_text}': {agent_err}")
                        try:
                            await websocket.send_json({
                                "type": "error",
                                "message": (
                                    "Lyra encountered an issue processing your request. "
                                    "Please try again."
                                ),
                            })
                        except Exception:
                            pass

        except WebSocketDisconnect:
            logger.info("Browser WebSocket disconnected (events task).")
        except Exception as err:
            logger.warning(f"Error in AssemblyAI-to-browser event task: {err}")

    # ── Run both tasks concurrently, stop when either completes ────────
    input_task = asyncio.create_task(handle_browser_to_assemblyai())
    output_task = asyncio.create_task(handle_assemblyai_to_browser())

    done, pending = await asyncio.wait(
        [input_task, output_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    # Clean up AssemblyAI session
    await service.terminate()
    logger.info("AssemblyAI session terminated. /ws/voice endpoint closed cleanly.")
