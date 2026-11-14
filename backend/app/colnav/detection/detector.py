
from ultralytics import YOLO
from app.colnav.schemas import BoundingBox, DetectionResult


class YOLODetector:
    def __init__(
        self,
        model_path="yolov8n.pt",
        confidence_threshold=0.25,
        tracker_config="bytetrack.yaml"
    ):
        print("Loading YOLOv8 model...")

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.tracker_config = tracker_config

        print("YOLOv8 model loaded successfully!")

    def detect(self, frame):
        results = self.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_config,
            classes=[0],
            conf=self.confidence_threshold,
            device="cpu",
            verbose=False
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()

                confidence = float(box.conf[0].cpu())
                class_id = int(box.cls[0].cpu())

                # Track ID may be unavailable for an untracked detection.
                track_id = None

                if box.id is not None:
                    track_id = int(box.id[0].cpu())

                detection = DetectionResult(
                    object_id=track_id,
                    class_name=self.model.names[class_id],
                    confidence=confidence,
                    bounding_box=BoundingBox(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2
                    )
                )

                detections.append(detection)

        return detections
