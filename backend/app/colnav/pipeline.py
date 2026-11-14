
from datetime import datetime

from app.colnav.schemas import ColNavResult, FrameInput
from app.colnav.detection.detector import YOLODetector
from app.colnav.tracking.history import PositionHistory


class ColNavPipeline:
    def __init__(self, detector=None, position_history=None):
        self.frame_count = 0

        self.detector = (
            detector if detector is not None else YOLODetector()
        )

        self.position_history = (
            position_history
            if position_history is not None
            else PositionHistory()
        )

    def process_frame(self, frame, source="webcam"):
        if frame is None:
            raise ValueError("Invalid frame received")

        self.frame_count += 1

        height, width = frame.shape[:2]

        frame_input = FrameInput(
            frame_id=self.frame_count,
            timestamp=datetime.now(),
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

        # Step 3: Build structured result
        result = ColNavResult(
            frame_id=frame_input.frame_id,
            timestamp=frame_input.timestamp,
            status="tracking_processed",
            detections=detections,
            tracking=tracking
        )

        print(
            f"Frame {frame_input.frame_id}: "
            f"{len(detections)} detections, "
            f"{len(tracking)} tracked pedestrians"
        )

        return result
