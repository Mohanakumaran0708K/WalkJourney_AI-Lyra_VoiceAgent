"""
lyra_agent.py — Lyra Intelligent AI Agent for WalkJourney AI (Phase 3)

Processes final voice transcripts via OpenAI LLM tool calling.
Falls back to deterministic local tool execution if LLM is unavailable.
All API keys are server-side only. Keys are never logged.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List


import openai
from google import genai
from google.genai import types

from app.config import settings
from app.agent.prompts import LYRA_SYSTEM_PROMPT
from app.tools.walkjourney_tools import (
    WalkJourneyTools,
    OPENAI_TOOL_DEFINITIONS,
    execute_walkjourney_tool,
)

logger = logging.getLogger(__name__)


class LyraAgent:
    """
    Intelligent AI Agent for WalkJourney AI.

    Flow:
      1. Receives a final voice transcript from AssemblyAI STT.
      2. Sends it to the OpenAI LLM with WalkJourney tool definitions.
      3. LLM decides which environmental tools to call.
      4. Tools return structured JSON environment data.
      5. LLM synthesises a concise spoken-style navigation response.
      6. Falls back to deterministic local tool execution if LLM is absent/failed.
    """

    def __init__(self) -> None:
        self.name = "Lyra Voice Agent"

    # ------------------------------------------------------------------
    # Public async entry point (called from the WebSocket handler)
    # ------------------------------------------------------------------

    async def process_message_async(self, user_text: str) -> Dict[str, Any]:
        """
        Async wrapper: runs the (blocking) OpenAI SDK call in a thread pool
        so the FastAPI event loop is never blocked.
        """
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._process_message_sync, user_text),
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(
                f"Lyra Agent timed out after {settings.LLM_TIMEOUT_SECONDS}s "
                f"for query: '{user_text}'. Falling back to local tools."
            )
            return self._local_fallback(user_text, timeout=True)
        except Exception as exc:
            logger.error(f"Unexpected error in process_message_async: {exc}")
            return self._local_fallback(user_text)

    # Synchronous alias kept for the REST /agent/chat endpoint
    def process_message(self, user_text: str) -> Dict[str, Any]:
        return self._process_message_sync(user_text)

    # ------------------------------------------------------------------
    # Core synchronous processing logic
    # ------------------------------------------------------------------

    def _process_message_sync(self, user_text: str) -> Dict[str, Any]:
        """
        Main Lyra processing pipeline using Google Gemini function calling.
        Falls back to deterministic local tools if Gemini is unavailable.
        """
        cleaned_text = user_text.strip()
        logger.info(f"[Lyra] Processing transcript: '{cleaned_text}'")

        tools_used: List[str] = []
        final_response_text = ""

        # Detect current demo scenario for telemetry / local fallback
        scenario_id = WalkJourneyTools._detect_scenario(cleaned_text)

        # ── 1. Gemini tool-calling flow ─────────────────────────────
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            logger.info(
                f"[Lyra] Gemini configured "
                f"(model={settings.GEMINI_MODEL}). Invoking tool-calling flow."
            )

            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                # Convert existing OpenAI-style tool definitions
                # into Gemini function declarations.
                function_declarations = []

                for tool_definition in OPENAI_TOOL_DEFINITIONS:
                    function_data = tool_definition.get("function", {})

                    function_declarations.append(
                        types.FunctionDeclaration(
                            name=function_data.get("name"),
                            description=function_data.get("description"),
                            parameters=function_data.get("parameters"),
                        )
                    )

                gemini_tools = [
                    types.Tool(
                        function_declarations=function_declarations
                    )
                ]

                config = types.GenerateContentConfig(
                    system_instruction=LYRA_SYSTEM_PROMPT,
                    tools=gemini_tools,
                    temperature=0.3,
                )

                # ── Step A: Ask Gemini to reason about the request ──
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=cleaned_text,
                    config=config,
                )

                # Gemini may request one or more functions.
                function_calls = []

                if response.candidates:
                    candidate = response.candidates[0]

                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if getattr(part, "function_call", None):
                                function_calls.append(part.function_call)

                # ── Step B: Execute requested WalkJourney tools ────
                if function_calls:
                    logger.info(
                        f"[Lyra] Gemini requested {len(function_calls)} tool(s): "
                        f"{[call.name for call in function_calls]}"
                    )

                    tool_response_parts = []

                    for function_call in function_calls:
                        func_name = function_call.name
                        tools_used.append(func_name)

                        # Gemini arguments are already structured.
                        func_args = {}

                        if function_call.args:
                            func_args = dict(function_call.args)

                        try:
                            tool_result = execute_walkjourney_tool(
                                func_name,
                                func_args,
                                cleaned_text,
                            )

                            logger.info(
                                f"[Lyra] Tool '{func_name}' returned: "
                                f"{json.dumps(tool_result, default=str)}"
                            )

                        except Exception as tool_exc:
                            logger.error(
                                f"[Lyra] Tool '{func_name}' raised an error: "
                                f"{tool_exc}"
                            )

                            tool_result = {
                                "error": (
                                    f"Tool '{func_name}' failed: "
                                    f"{str(tool_exc)}"
                                )
                            }

                        tool_response_parts.append(
                            types.Part.from_function_response(
                                name=func_name,
                                response=tool_result,
                            )
                        )

                    # ── Step C: Give tool results back to Gemini ────
                    logger.info(
                        "[Lyra] Sending WalkJourney tool results "
                        "back to Gemini for final response."
                    )

                    final_response = client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[
    types.Content(
        role="user",
        parts=[types.Part.from_text(text=cleaned_text)],
    ),
    response.candidates[0].content,
    types.Content(
        role="user",
        parts=tool_response_parts,
    ),
],
                        config=config,
                    )

                    if final_response.text:
                        final_response_text = final_response.text.strip()

                    logger.info(
                        f"[Lyra] Gemini final response: "
                        f"'{final_response_text}'"
                    )

                else:
                    # Gemini answered directly without using tools.
                    if response.text:
                        final_response_text = response.text.strip()

                    logger.info(
                        f"[Lyra] Gemini direct response: "
                        f"'{final_response_text}'"
                    )

            except Exception as exc:
                logger.exception(
                    f"[Lyra] Gemini error: {type(exc).__name__}: {exc}"
                )
                print(
                    f"[LYRA GEMINI ERROR] "
                    f"{type(exc).__name__}: {exc}"
                )
                final_response_text = ""

        else:
            logger.warning(
                "[Lyra] GEMINI_API_KEY not configured. "
                "Using deterministic local tool execution."
            )

        # ── 2. Local deterministic fallback ────────────────────────
        if not final_response_text:
            return self._local_fallback(user_text)

        # ── 3. Build telemetry for the WalkingScene canvas ─────────
        telemetry = self._build_telemetry(
            cleaned_text,
            scenario_id,
        )

        return {
            "agent_name": self.name,
            "user_input": user_text,
            "response": final_response_text,
            "status": "success",
            "scenario": scenario_id,
            "tools_used": list(dict.fromkeys(tools_used)),
            "telemetry": telemetry,

        }   
        # ------------------------------------------------------------------
    # Deterministic local fallback (no LLM required)
    # ------------------------------------------------------------------

    def _local_fallback(self, user_text: str, timeout: bool = False) -> Dict[str, Any]:
        """
        Runs WalkJourney tools locally and generates a simple
        template-based response when Gemini is unavailable.
        """
        cleaned_text = user_text.strip()
        scenario_id = WalkJourneyTools._detect_scenario(cleaned_text)

        logger.info(
            f"[Lyra] Local fallback — scenario='{scenario_id}'"
            + (" (LLM timeout)" if timeout else "")
        )

        scene_info = WalkJourneyTools.scene_understanding(
            cleaned_text,
            scenario_id,
        )

        nav_info = WalkJourneyTools.navigation_recommendation(
            cleaned_text,
            scenario_id,
        )

        safety_info = WalkJourneyTools.safety_check(
            cleaned_text,
            scenario_id,
        )

        tools_used = [
            "scene_understanding",
            "navigation_recommendation",
            "safety_check",
        ]

        rec_dir = nav_info.get(
            "recommended_direction",
            "straight",
        )

        reason = nav_info.get("reason", "")

        is_safe = safety_info.get(
            "is_current_route_safe",
            True,
        )

        obstacle = scene_info.get(
            "obstacle_detected",
            False,
        )

        crowd = scene_info.get(
            "crowd_density",
            "moderate",
        )

        if obstacle and not is_safe:
            response_text = (
                "Warning — there is an obstacle blocking "
                f"the center path. {reason.capitalize()}. "
                f"I recommend moving {rec_dir}."
            )

        elif rec_dir == "left":
            response_text = (
                f"The path ahead is {crowd}ly crowded. "
                "The left side is clearer — "
                "I recommend moving slightly left."
            )

        elif rec_dir == "right":
            response_text = (
                f"The center route is blocked. "
                f"{reason.capitalize()}. "
                "Move to the right to continue safely."
            )

        else:
            response_text = (
                "The path ahead is clear with low crowd density. "
                "You can continue safely straight ahead."
            )

        telemetry = self._build_telemetry(
            cleaned_text,
            scenario_id,
        )

        return {
            "agent_name": self.name,
            "user_input": user_text,
            "response": response_text,
            "status": "fallback",
            "scenario": scenario_id,
            "tools_used": tools_used,
            "telemetry": telemetry,
        }
    
    # ------------------------------------------------------------------
    # Telemetry builder for WalkingScene canvas
    # ------------------------------------------------------------------

    @staticmethod
    def _build_telemetry(user_text: str, scenario_id: str) -> Dict[str, Any]:
        """Builds telemetry data from the current scenario state."""
        scene = WalkJourneyTools.scene_understanding(user_text, scenario_id)
        nav = WalkJourneyTools.navigation_recommendation(user_text, scenario_id)

        return {
            "crowdDensity": nav.get("telemetry_crowd", scene.get("crowd_density", "moderate")),
            "recommendedDirection": nav.get("recommended_direction", "straight"),
            "obstacleDetected": scene.get("obstacle_detected", False),
            "guidanceText": nav.get("gui_guidance_text", "↑ CONTINUE"),
            "pathStatus": scene.get("center_path", "clear"),
            "environment": "SIMULATION • DEMO",
        }
