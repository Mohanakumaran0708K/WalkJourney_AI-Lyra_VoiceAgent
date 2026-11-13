
from app.colnav.pipeline import ColNavPipeline
from app.colnav.schemas import (
    DetectionResult,
    BoundingBox
)


# Create a fake detector for testing
class FakeDetector:

    def detect(self, frame):

        return [
            DetectionResult(
                object_id=None,
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


# Inject fake detector into pipeline
fake_detector = FakeDetector()

pipeline = ColNavPipeline(detector=fake_detector)

# Create a dummy image frame
import numpy as np

frame = np.zeros((480, 640, 3), dtype=np.uint8)

# Process frame
result = pipeline.process_frame(
    frame,
    source="video"
)

# Display results
print("\n--- Pipeline Test Results ---")
print("Frame ID:", result.frame_id)
print("Status:", result.status)
print("Total detections:", len(result.detections))

for detection in result.detections:
    print("Class:", detection.class_name)
    print("Confidence:", detection.confidence)
    print("Bounding Box:", detection.bounding_box)
