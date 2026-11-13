
import cv2
import time
from app.colnav.detection.detector import YOLODetector


# Path to the first MOT17 image
image_path = (
    r"C:\Users\Mohanakumaran K\OneDrive\Desktop"
    r"\WalkJourney AI\MOT17\MOT17\train"
    r"\MOT17-04-FRCNN\img1\000001.jpg"
)

# Load image
frame = cv2.imread(image_path)

if frame is None:
    raise FileNotFoundError(f"Could not load image: {image_path}")

print("Image loaded successfully!")
print("Image dimensions:", frame.shape)

# Initialize YOLO detector
detector = YOLODetector()

# Detect pedestrians
# Measure YOLO inference time
start_time = time.perf_counter()

detections = detector.detect(frame)

end_time = time.perf_counter()

inference_time = end_time - start_time
inference_fps = 1 / inference_time

print("\n--- Performance Metrics ---")
print(f"Inference Time: {inference_time * 1000:.2f} ms")
print(f"Inference FPS: {inference_fps:.2f}")

print("\n--- YOLOv8 Detection Results ---")
print("Total pedestrians detected:", len(detections))


# Draw bounding boxes on the original frame
annotated_frame = frame.copy()

for detection in detections:
    box = detection.bounding_box

    x1 = int(box.x1)
    y1 = int(box.y1)
    x2 = int(box.x2)
    y2 = int(box.y2)

    confidence = detection.confidence
    label = f"Person {confidence:.2f}"

    # Draw rectangle
    cv2.rectangle(
        annotated_frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    # Draw confidence label
    cv2.putText(
        annotated_frame,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

# Save the annotated image
output_path = "mot17_detection_result.jpg"

cv2.imwrite(output_path, annotated_frame)

print(f"\nAnnotated image saved: {output_path}")

# Display the annotated image
cv2.imshow("WalkJourney AI - YOLOv8 Detection", annotated_frame)

print("Press Q to close the image window.")
cv2.waitKey(0)
cv2.destroyAllWindows()

for index, detection in enumerate(detections, start=1):
    print(f"\nPerson {index}")
    print("Class:", detection.class_name)
    print("Confidence:", round(detection.confidence, 3))
    print("Bounding Box:", detection.bounding_box)
