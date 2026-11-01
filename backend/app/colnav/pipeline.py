from datetime import datetime

from app.colnav.schemas import ColNavResult, FrameInput


class ColNavPipeline:

    def __init__(self):
        self.frame_count = 0

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

        result = ColNavResult(
            frame_id=frame_input.frame_id,
            timestamp=frame_input.timestamp,
            status="frame_received"
        )

        print(
            f"Frame: {frame_input.frame_id} | "
            f"Source: {frame_input.source} | "
            f"Resolution: {width}x{height}"
        )

        return result