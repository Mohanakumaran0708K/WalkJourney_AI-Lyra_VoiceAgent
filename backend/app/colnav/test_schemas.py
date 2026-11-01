from datetime import datetime

from app.colnav.schemas import (
    BoundingBox,
    DetectionResult,
    ColNavResult
)


box = BoundingBox(
    x1=100,
    y1=50,
    x2=250,
    y2=400
)

person = DetectionResult(
    object_id=1,
    class_name="person",
    confidence=0.95,
    bounding_box=box
)

result = ColNavResult(
    frame_id=1,
    timestamp=datetime.now(),
    status="success",
    detections=[person]
)

print(result.model_dump_json(indent=4))