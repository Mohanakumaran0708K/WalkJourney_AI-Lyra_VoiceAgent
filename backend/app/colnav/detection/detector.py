
from ultralytics import YOLO
from app.colnav.schemas import BoundingBox, DetectionResult


class YOLODetector:
    def __init__(
        self,
        model_path="yolov8n.pt",
        confidence_threshold=0.25
    ):
        print("Loading YOLOv8 model...")

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

        print("YOLOv8 model loaded successfully!")

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            classes=[0],       # COCO class 0 = person
            conf=self.confidence_threshold,
            device="cpu",
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()

                confidence = float(box.conf[0].cpu())
                class_id = int(box.cls[0].cpu())

                detection = DetectionResult(
                    object_id=None,
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
