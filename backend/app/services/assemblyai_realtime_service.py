import json
import logging
import websockets
from typing import AsyncGenerator, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AssemblyAIRealtimeService:
    """
    Service wrapper for AssemblyAI Streaming Speech-to-Text v3 WebSocket.
    Manages connection authentication, raw PCM16 audio forwarding, and transcript parsing.
    """
    ASSEMBLYAI_V3_WS_URL = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&speech_model=universal-3-5-pro"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ASSEMBLYAI_API_KEY
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False

    async def connect(self):
        """Connect to AssemblyAI Streaming STT v3 WebSocket."""
        if not self.api_key or self.api_key.strip() == "":
            raise ValueError("ASSEMBLYAI_API_KEY is missing from server configuration.")

        headers = {"Authorization": self.api_key}
        logger.info("Connecting to AssemblyAI Streaming STT v3 WebSocket...")
        
        try:
            self.ws = await websockets.connect(
                self.ASSEMBLYAI_V3_WS_URL,
                additional_headers=headers
            )
            self.is_connected = True
            logger.info("Successfully established AssemblyAI STT v3 WebSocket connection.")
        except Exception as e:
            logger.error(f"Failed to connect to AssemblyAI v3 WebSocket: {e}")
            self.is_connected = False
            raise e

    async def send_audio(self, pcm16_audio_chunk: bytes):
        """Forward raw PCM16 mono 16kHz binary audio chunk to AssemblyAI."""
        if self.ws and self.is_connected:
            try:
                await self.ws.send(pcm16_audio_chunk)
            except Exception as e:
                logger.error(f"Error sending audio chunk to AssemblyAI: {e}")

    async def receive_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Listen for incoming WebSocket messages from AssemblyAI v3
        and yield normalized structured events for the client.
        """
        if not self.ws or not self.is_connected:
            yield {"type": "error", "message": "AssemblyAI service is not connected."}
            return

        try:
            async for raw_msg in self.ws:
                try:
                    data = json.loads(raw_msg)
                except Exception:
                    continue

                msg_type = data.get("type") or data.get("message_type")

                # 1. Session Begun / Start
                if msg_type in ["Begin", "SessionBegun"]:
                    yield {
                        "type": "session_started",
                        "session_id": data.get("id") or data.get("session_id")
                    }

                # 2. Turn / Transcript events (v3 protocol)
                elif msg_type in ["Turn", "PartialTranscript", "FinalTranscript"]:
                    # AssemblyAI v3 "Turn" structure contains text and end_of_turn flag
                    text = data.get("text") or data.get("transcript") or ""
                    is_final = data.get("end_of_turn", False) or msg_type == "FinalTranscript"

                    if text.strip():
                        if is_final:
                            yield {
                                "type": "final_transcript",
                                "text": text.strip()
                            }
                        else:
                            yield {
                                "type": "partial_transcript",
                                "text": text.strip()
                            }

                # 3. Termination / Session Ended
                elif msg_type in ["Termination", "SessionTerminated"]:
                    yield {"type": "session_ended"}

                # 4. Error
                elif msg_type in ["Error", "SessionError"]:
                    error_msg = data.get("error") or data.get("message") or "AssemblyAI Stream Error"
                    yield {"type": "error", "message": error_msg}

        except websockets.exceptions.ConnectionClosed as cc:
            logger.info(f"AssemblyAI WebSocket closed: {cc}")
            yield {"type": "session_ended"}
        except Exception as e:
            logger.error(f"Error in AssemblyAI event listener loop: {e}")
            yield {"type": "error", "message": str(e)}

    async def terminate(self):
        """Send termination command to AssemblyAI and close the WebSocket cleanly."""
        if self.ws and self.is_connected:
            try:
                # Send v3 termination message
                await self.ws.send(json.dumps({"type": "terminate"}))
            except Exception as e:
                logger.warning(f"Error sending termination message to AssemblyAI: {e}")
            finally:
                try:
                    await self.ws.close()
                except Exception:
                    pass
                self.is_connected = False
                logger.info("AssemblyAI v3 WebSocket connection terminated cleanly.")
