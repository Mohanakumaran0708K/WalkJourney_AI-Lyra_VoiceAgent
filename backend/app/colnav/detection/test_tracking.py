
import cv2
import time

from app.colnav.detection.detector import YOLODetector


VIDEO_PATH = r"C:\Users\Mohanakumaran K\OneDrive\Desktop\WalkJourney AI\MOT17\MOT17\train\MOT17-04-FRCNN\img1"

detector = YOLODetector()

image_files = sorted(
    __import__("glob").glob(VIDEO_PATH + r"\*.jpg")
)

if not image_files:
    raise RuntimeError("No MOT17 images found!")

print(f"Total frames available: {len(image_files)}")

previous_ids = set()
total_frames = 0
total_detections = 0
total_inference_time = 0

for image_path in image_files[:100]:

    frame = cv2.imread(image_path)

    if frame is None:
        continue

    start_time = time.perf_counter()

    detections = detector.detect(frame)

    inference_time = time.perf_counter() - start_time

    current_ids = {
        detection.object_id
        for detection in detections
        if detection.object_id is not None
    }

    total_frames += 1
    total_detections += len(detections)
    total_inference_time += inference_time

    new_ids = current_ids - previous_ids
    continuing_ids = current_ids & previous_ids

    print(
        f"Frame: {total_frames:03d} | "
        f"Detections: {len(detections):02d} | "
        f"Active IDs: {sorted(current_ids)} | "
        f"New IDs: {sorted(new_ids)} | "
        f"Continuing IDs: {sorted(continuing_ids)} | "
        f"FPS: {1 / inference_time:.2f}"
    )

    previous_ids = current_ids

print("\n========== TRACKING SUMMARY ==========")

print(f"Frames processed: {total_frames}")
print(f"Total detections: {total_detections}")

if total_frames:
    avg_time = total_inference_time / total_frames

    print(f"Average inference time: {avg_time * 1000:.2f} ms")
    print(f"Average FPS: {1 / avg_time:.2f}")

print("Tracking test completed.")
