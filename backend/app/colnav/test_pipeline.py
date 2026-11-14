
import numpy as np

from app.colnav.pipeline import ColNavPipeline
from app.colnav.schemas import DetectionResult, BoundingBox


class FakeDetector:
    def detect(self, frame):
        return [
            DetectionResult(
                object_id=7,
                class_name="person",
                confidence=0.95,
                bounding_box=BoundingBox(
                    x1=100,
                    y1=150,
                    x2=200,
                    y2=450
                )
            )
        ]


def test_pipeline_processes_detections_and_tracking():
    fake_detector = FakeDetector()
    pipeline = ColNavPipeline(detector=fake_detector)

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = pipeline.process_frame(frame, source="video")

    # Verify frame processing
    assert result.frame_id == 1
    assert result.status == "tracking_processed"

    # Verify detections
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "person"

    # Verify tracking
    assert len(result.tracking) == 1
    assert result.tracking[0].track_id == 7
    assert result.tracking[0].center_x == 150
    assert result.tracking[0].center_y == 300


def test_pipeline_preserves_position_history():
    pipeline = ColNavPipeline(detector=FakeDetector())

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    pipeline.process_frame(frame, source="video")
    pipeline.process_frame(frame, source="video")

    history = pipeline.position_history.get_history(7)

    assert len(history) == 2
    assert history[-1].center_x == 150
    assert history[-1].center_y == 300


def test_pipeline_rejects_invalid_frame():
    pipeline = ColNavPipeline(detector=FakeDetector())

    try:
        pipeline.process_frame(None)
    except ValueError as error:
        assert str(error) == "Invalid frame received"
    else:
        raise AssertionError("Expected ValueError for invalid frame")
