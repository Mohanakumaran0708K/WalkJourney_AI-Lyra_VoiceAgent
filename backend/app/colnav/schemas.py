from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
# Frame Input contract
class FrameInput(BaseModel):
    frame_id: int = Field(ge=1)
    timestamp: datetime
    source: Literal["webcam", "mobile", "smart_glass", "video"]
    width: int = Field(gt=0)
    height: int = Field(gt=0)

# 1. Bounding Box
class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


# 2. Detection Result
class DetectionResult(BaseModel):
    object_id: Optional[int] = None
    class_name: str
    confidence: float = Field(ge=0, le=1)
    bounding_box: BoundingBox


# 3. Tracking Result
class TrackingResult(BaseModel):
    track_id: int
    class_name: str
    center_x: float
    center_y: float
    movement_status: str = "unknown"


# 3.1 Kalman Estimated State
class EstimatedMotionState(BaseModel):
    track_id: int
    class_name: str

    # Estimated image-plane position
    x: float
    y: float

    # Estimated image-plane velocity (pixels/second)
    vx: float
    vy: float

    # 4x4 state covariance matrix
    covariance: List[List[float]]

    # Whether this state came from a measurement or prediction
    status: Literal["observed", "predicted"] = "observed"

        # Estimated movement direction in image-plane coordinates
    movement_direction: Literal[
        "left",
        "right",
        "up",
        "down",
        "stationary",
        "unknown"
    ] = "unknown"



# 4. Trajectory Result
class TrajectoryResult(BaseModel):
    track_id: int
    future_positions: List[List[float]] = Field(default_factory=list)
    prediction_horizon_seconds: float = 0.0


# 5. Risk Assessment
class RiskAssessment(BaseModel):
    risk_level: str = "unknown"
    risk_score: float = Field(default=0.0, ge=0, le=1)
    time_to_collision: Optional[float] = None
    description: str = "Risk not assessed"


# 6. Navigation Result
class NavigationResult(BaseModel):
    direction: str = "stop"
    instruction: str = "Navigation decision unavailable"
    confidence: float = Field(default=0.0, ge=0, le=1)


# 7. Complete ColNav Result
class ColNavResult(BaseModel):
    frame_id: int
    timestamp: datetime
    status: str
    detections: List[DetectionResult] = Field(default_factory=list)
    tracking: List[TrackingResult] = Field(default_factory=list)
    estimated_states: List[EstimatedMotionState] = Field(
    default_factory=list
)
    trajectories: List[TrajectoryResult] = Field(default_factory=list)
    risk: Optional[RiskAssessment] = None
    navigation: Optional[NavigationResult] = None