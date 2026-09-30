from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class WalkJourneyTools:
    """
    Modular WalkJourney AI spatial environment & navigation tools.
    Provides structured JSON outputs for scene understanding, crowd analysis,
    navigation recommendations, and safety checks across hackathon demo scenarios.
    """

    @staticmethod
    def _detect_scenario(query: str, requested_scenario: Optional[str] = None) -> str:
        if requested_scenario and requested_scenario != "auto":
            return requested_scenario
        
        cleaned = query.strip().lower()
        if "obstacle" in cleaned or "can i continue straight" in cleaned or "barrier" in cleaned:
            return "obstacle"
        elif "left" in cleaned or "is left clear" in cleaned:
            return "clear_left"
        elif "safest" in cleaned or "safe" in cleaned or "route" in cleaned:
            return "safe_straight"
        elif "ahead" in cleaned or "what's ahead" in cleaned or "crowd" in cleaned:
            return "crowded"
        return "crowded"

    @classmethod
    def scene_understanding(cls, query: str = "", scenario: str = "auto") -> Dict[str, Any]:
        """
        Tool 1: Scene Understanding
        Analyzes the walking corridor environment, pedestrian positions, and obstacle presence.
        """
        active_scenario = cls._detect_scenario(query, scenario)

        if active_scenario == "crowded":
            return {
                "people_detected": 8,
                "nearest_person_distance_m": 2.1,
                "crowd_density": "high",
                "obstacle_detected": False,
                "left_path": "clear",
                "center_path": "blocked",
                "right_path": "moderate"
            }
        elif active_scenario == "clear_left":
            return {
                "people_detected": 4,
                "nearest_person_distance_m": 4.5,
                "crowd_density": "low",
                "obstacle_detected": False,
                "left_path": "clear",
                "center_path": "moderate",
                "right_path": "high"
            }
        elif active_scenario == "obstacle":
            return {
                "people_detected": 3,
                "nearest_person_distance_m": 1.8,
                "crowd_density": "moderate",
                "obstacle_detected": True,
                "left_path": "narrow",
                "center_path": "blocked_by_obstacle",
                "right_path": "clear"
            }
        else: # safe_straight
            return {
                "people_detected": 2,
                "nearest_person_distance_m": 6.0,
                "crowd_density": "low",
                "obstacle_detected": False,
                "left_path": "clear",
                "center_path": "clear",
                "right_path": "clear"
            }

    @classmethod
    def crowd_analysis(cls, query: str = "", scenario: str = "auto") -> Dict[str, Any]:
        """
        Tool 2: Crowd Analysis
        Evaluates crowd distribution, density, congested zones, and clearer directions.
        """
        active_scenario = cls._detect_scenario(query, scenario)

        if active_scenario == "crowded":
            return {
                "crowd_density": "high",
                "congested_direction": "center",
                "clearer_direction": "left",
                "confidence": 0.93
            }
        elif active_scenario == "clear_left":
            return {
                "crowd_density": "low",
                "congested_direction": "right",
                "clearer_direction": "left",
                "confidence": 0.95
            }
        elif active_scenario == "obstacle":
            return {
                "crowd_density": "moderate",
                "congested_direction": "center",
                "clearer_direction": "right",
                "confidence": 0.90
            }
        else:
            return {
                "crowd_density": "low",
                "congested_direction": "none",
                "clearer_direction": "center",
                "confidence": 0.98
            }

    @classmethod
    def navigation_recommendation(cls, query: str = "", scenario: str = "auto") -> Dict[str, Any]:
        """
        Tool 3: Navigation Recommendation
        Calculates optimal turn direction and reason based on current environment state.
        """
        active_scenario = cls._detect_scenario(query, scenario)

        if active_scenario == "crowded":
            return {
                "recommended_direction": "left",
                "reason": "center path is densely crowded; left walkway is clear",
                "confidence": 0.92,
                "gui_guidance_text": "← MOVE LEFT",
                "telemetry_crowd": "high"
            }
        elif active_scenario == "clear_left":
            return {
                "recommended_direction": "left",
                "reason": "left side has minimal pedestrian density and open passage",
                "confidence": 0.96,
                "gui_guidance_text": "← CLEAR PATH",
                "telemetry_crowd": "low"
            }
        elif active_scenario == "obstacle":
            return {
                "recommended_direction": "right",
                "reason": "physical obstacle blocking center path; right detour is open",
                "confidence": 0.94,
                "gui_guidance_text": "→ MOVE RIGHT",
                "telemetry_crowd": "moderate"
            }
        else:
            return {
                "recommended_direction": "straight",
                "reason": "forward path is completely clear of obstacles and crowds",
                "confidence": 0.99,
                "gui_guidance_text": "↑ CONTINUE",
                "telemetry_crowd": "low"
            }

    @classmethod
    def safety_check(cls, query: str = "", scenario: str = "auto") -> Dict[str, Any]:
        """
        Tool 4: Safety Check
        Assesses proximity risks, obstacles, and route safety.
        """
        active_scenario = cls._detect_scenario(query, scenario)

        if active_scenario == "crowded":
            return {
                "obstacles_present": False,
                "unsafe_directions": ["center"],
                "proximity_risk": "moderate",
                "is_current_route_safe": True,
                "safety_recommendation": "Bypass center crowd via left side."
            }
        elif active_scenario == "clear_left":
            return {
                "obstacles_present": False,
                "unsafe_directions": ["right"],
                "proximity_risk": "low",
                "is_current_route_safe": True,
                "safety_recommendation": "Left path is safe for movement."
            }
        elif active_scenario == "obstacle":
            return {
                "obstacles_present": True,
                "unsafe_directions": ["center"],
                "proximity_risk": "high",
                "is_current_route_safe": False,
                "safety_recommendation": "Obstacle ahead. Divert to the right."
            }
        else:
            return {
                "obstacles_present": False,
                "unsafe_directions": [],
                "proximity_risk": "low",
                "is_current_route_safe": True,
                "safety_recommendation": "Route is safe to proceed forward."
            }


# OpenAI Function / Tool Definitions for LLM Tool Calling
OPENAI_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "scene_understanding",
            "description": "Scans the walking environment to detect pedestrians, obstacles, nearest person distance, and path statuses (left, center, right).",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Optional scenario identifier ('auto', 'crowded', 'clear_left', 'obstacle', 'safe_straight')."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crowd_analysis",
            "description": "Analyzes crowd density, identifies congested directions, and locates clearer walkways.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Optional scenario identifier ('auto', 'crowded', 'clear_left', 'obstacle', 'safe_straight')."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigation_recommendation",
            "description": "Calculates the recommended walking direction (left, right, straight) and justification based on sensor tool outputs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Optional scenario identifier ('auto', 'crowded', 'clear_left', 'obstacle', 'safe_straight')."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "safety_check",
            "description": "Evaluates proximity risks, obstacle hazards, and checks whether the proposed walking route is safe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Optional scenario identifier ('auto', 'crowded', 'clear_left', 'obstacle', 'safe_straight')."
                    }
                },
                "required": []
            }
        }
    }
]

def execute_walkjourney_tool(tool_name: str, tool_args: dict, user_query: str) -> Dict[str, Any]:
    """
    Executes a requested WalkJourney tool by name and returns structured JSON output.
    """
    scenario = tool_args.get("scenario", "auto")
    logger.info(f"Executing tool '{tool_name}' with args {tool_args} for query '{user_query}'")

    if tool_name == "scene_understanding":
        return WalkJourneyTools.scene_understanding(user_query, scenario)
    elif tool_name == "crowd_analysis":
        return WalkJourneyTools.crowd_analysis(user_query, scenario)
    elif tool_name == "navigation_recommendation":
        return WalkJourneyTools.navigation_recommendation(user_query, scenario)
    elif tool_name == "safety_check":
        return WalkJourneyTools.safety_check(user_query, scenario)
    else:
        logger.warning(f"Unknown tool requested: {tool_name}")
        return {"error": f"Tool '{tool_name}' is not recognized."}
