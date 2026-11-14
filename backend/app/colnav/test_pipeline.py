
import numpy as np
from datetime import datetime, timedelta
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
    pipeline = ColNavPipeline(detector=FakeDetector())

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = pipeline.process_frame(frame, source="video")

    # Verify frame processing
    assert result.frame_id == 1
    assert result.status == "motion_estimation_processed"

    # Verify detections
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "person"

    # Verify tracking
    assert len(result.tracking) == 1
    assert result.tracking[0].track_id == 7
    assert result.tracking[0].center_x == 150
    assert result.tracking[0].center_y == 300

    # Verify Kalman estimation
    assert len(result.estimated_states) == 1

    estimated = result.estimated_states[0]

    assert estimated.track_id == 7
    assert estimated.class_name == "person"
    assert estimated.status == "observed"

    # Verify covariance matrix
    assert len(estimated.covariance) == 4
    assert all(len(row) == 4 for row in estimated.covariance)


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

class IntermittentDetector:
    def __init__(self):
        self.call_count = 0

    def detect(self, frame):
        self.call_count += 1

        # First frame: pedestrian detected.
        # Second frame: pedestrian temporarily missing.
        if self.call_count == 1:
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

        return []


def test_pipeline_predicts_temporarily_missing_pedestrian():
    pipeline = ColNavPipeline(
        detector=IntermittentDetector()
    )

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    first_result = pipeline.process_frame(
        frame,
        source="video"
    )

    second_result = pipeline.process_frame(
        frame,
        source="video"
    )

    assert len(first_result.tracking) == 1
    assert first_result.estimated_states[0].status == "observed"

    assert len(second_result.detections) == 0
    assert len(second_result.tracking) == 0

    assert len(second_result.estimated_states) == 1

    prediction = second_result.estimated_states[0]

    assert prediction.track_id == 7
    assert prediction.status == "predicted"
    assert prediction.covariance[0][0] > 0

class MovingDetector:
    def __init__(self):
        self.call_count = 0

    def detect(self, frame):
        self.call_count += 1

        x_position = 100 + (self.call_count - 1) * 20

        return [
            DetectionResult(
                object_id=7,
                class_name="person",
                confidence=0.95,
                bounding_box=BoundingBox(
                    x1=x_position,
                    y1=150,
                    x2=x_position + 100,
                    y2=450
                )
            )
        ]


def test_pipeline_initial_movement_is_unknown():
    pipeline = ColNavPipeline(detector=FakeDetector())

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = pipeline.process_frame(frame, source="video")

    assert len(result.estimated_states) == 1
    assert result.estimated_states[0].movement_direction == "unknown"


def test_pipeline_classifies_rightward_movement():
    pipeline = ColNavPipeline(detector=MovingDetector())

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    pipeline.process_frame(
        frame,
        source="video",
        timestamp=timestamp
    )

    result = pipeline.process_frame(
        frame,
        source="video",
        timestamp=timestamp + timedelta(seconds=0.2)
    )

    estimated = result.estimated_states[0]

    assert estimated.status == "observed"
    assert estimated.movement_direction == "right"


def test_pipeline_preserves_movement_during_missing_detection():
    pipeline = ColNavPipeline(
        detector=IntermittentDetector()
    )

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    first_result = pipeline.process_frame(frame, source="video")

    second_result = pipeline.process_frame(frame, source="video")

    assert first_result.estimated_states[0].movement_direction == "unknown"

    assert second_result.estimated_states[0].status == "predicted"
    assert second_result.estimated_states[0].movement_direction == "unknown"
