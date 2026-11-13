
import cv2
import time
from pathlib import Path

from app.colnav.pipeline import ColNavPipeline


# MOT17 dataset configuration
DATASET_PATH = Path(
    r"C:\Users\Mohanakumaran K\OneDrive\Desktop"
    r"\WalkJourney AI\MOT17\MOT17\train"
    r"\MOT17-04-FRCNN\img1"
)

SEQUENCE_FPS = 30.0
MAX_FRAMES = 10

# Initialize the complete ColNav pipeline.
# YOLODetector is created internally.
pipeline = ColNavPipeline()

# Find and sort image frames
image_paths = sorted(DATASET_PATH.glob("*.jpg"))

if not image_paths:
    raise FileNotFoundError("No JPG frames found!")

frames_to_process = image_paths[:MAX_FRAMES]

print(f"Frames selected: {len(frames_to_process)}")

# Warm-up
warmup_frame = cv2.imread(str(frames_to_process[0]))

if warmup_frame is None:
    raise RuntimeError("Could not load warm-up frame")

pipeline.detector.detect(warmup_frame)

inference_times = []
total_detections = 0
processed_frames = 0

print("\nStarting ColNav sequential processing...\n")

for image_path in frames_to_process:

    frame = cv2.imread(str(image_path))

    if frame is None:
        print(f"Skipping unreadable frame: {image_path.name}")
        continue

    start_time = time.perf_counter()

    # Process through the complete pipeline
    result = pipeline.process_frame(
        frame,
        source="video"
    )

    elapsed = time.perf_counter() - start_time

    inference_times.append(elapsed)
    processed_frames += 1
    total_detections += len(result.detections)

    # MOT17 relative timestamp
    frame_number = int(image_path.stem)
    timestamp_seconds = (frame_number - 1) / SEQUENCE_FPS

    print(
        f"Dataset Frame: {frame_number:06d} | "
        f"Media Time: {timestamp_seconds:.3f}s | "
        f"Pipeline Frame ID: {result.frame_id} | "
        f"People: {len(result.detections)} | "
        f"Processing: {elapsed * 1000:.2f} ms"
    )

# Performance summary
if inference_times:

    average_time = sum(inference_times) / len(inference_times)
    average_fps = 1 / average_time

    print("\n========== COLNAV BENCHMARK ==========")
    print("Processed frames:", processed_frames)
    print("Total detections:", total_detections)
    print(f"Average processing time: {average_time * 1000:.2f} ms")
    print(f"Average processing FPS: {average_fps:.2f}")
    print("======================================")
