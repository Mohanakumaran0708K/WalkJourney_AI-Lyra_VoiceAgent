
from datetime import datetime

from app.colnav.schemas import ColNavResult, FrameInput
from app.colnav.detection.detector import YOLODetector


class ColNavPipeline:

    def __init__(self, detector=None):
        self.frame_count = 0

        # Allow an external detector to be injected for testing.
        self.detector = detector if detector is not None else YOLODetector()

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

        # Run pedestrian detection
        detections = self.detector.detect(frame)

        # Build structured ColNav result
        result = ColNavResult(
            frame_id=frame_input.frame_id,
            timestamp=frame_input.timestamp,
            status="detections_processed",
            detections=detections
        )

        print(
            f"Frame: {frame_input.frame_id} | "
            f"Source: {frame_input.source} | "
            f"Resolution: {width}x{height} | "
            f"Pedestrians: {len(detections)}"
        )

        return result
