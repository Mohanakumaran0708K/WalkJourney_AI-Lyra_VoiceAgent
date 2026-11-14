
from datetime import datetime
from typing import Optional
from app.colnav.schemas import ColNavResult, FrameInput
from app.colnav.detection.detector import YOLODetector
from app.colnav.tracking.history import PositionHistory
from app.colnav.tracking.kalman_manager import KalmanFilterManager


class ColNavPipeline:

    def __init__(
        self,
        detector=None,
        position_history=None,
        kalman_manager=None
    ):
        self.frame_count = 0

        self.detector = (
            detector if detector is not None else YOLODetector()
        )

        self.position_history = (
            position_history
            if position_history is not None
            else PositionHistory()
        )

        self.kalman_manager = (
            kalman_manager
            if kalman_manager is not None
            else KalmanFilterManager()
        )

    def process_frame(
    self,
    frame,
    source="webcam",
    timestamp: Optional[datetime] = None,
):

        if frame is None:
            raise ValueError("Invalid frame received")

        self.frame_count += 1

        height, width = frame.shape[:2]

        frame_input = FrameInput(
            frame_id=self.frame_count,
            timestamp=timestamp if timestamp is not None else datetime.now(),
            source=source,
            width=width,
            height=height
        )

        # Step 1: Detect and track pedestrians
        detections = self.detector.detect(frame)

        # Step 2: Update position history
        tracking = self.position_history.update(
            detections=detections,
            timestamp=frame_input.timestamp
        )

        # Step 3: Update Kalman filters for observed tracks
        estimated_states = self.kalman_manager.update(
            tracks=tracking,
            timestamp=frame_input.timestamp
        )

        # Step 4: Predict pedestrians missing in this frame
        observed_track_ids = {
            track.track_id for track in tracking
        }

        missing_predictions = self.kalman_manager.predict_missing(
            timestamp=frame_input.timestamp,
            observed_track_ids=observed_track_ids
        )

        # Step 5: Combine observed and predicted states
        estimated_states.extend(missing_predictions)

        # Step 6: Build structured result
        result = ColNavResult(
            frame_id=frame_input.frame_id,
            timestamp=frame_input.timestamp,
            status="motion_estimation_processed",
            detections=detections,
            tracking=tracking,
            estimated_states=estimated_states
        )

        print(
            f"Frame {frame_input.frame_id}: "
            f"{len(detections)} detections, "
            f"{len(tracking)} tracked, "
            f"{len(estimated_states)} estimated states"
        )

        return result
