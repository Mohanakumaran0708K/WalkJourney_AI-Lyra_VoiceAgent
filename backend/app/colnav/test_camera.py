
import cv2
import time

from app.colnav.camera import Camera
from app.colnav.pipeline import ColNavPipeline


# Initialize camera and detection pipeline
camera = Camera()
pipeline = ColNavPipeline()

# Performance tracking
frame_count = 0
start_time = time.perf_counter()

try:

    camera.open()

    print("WalkJourney AI live detection started!")
    print("Press Q to exit.")

    while True:

        # Capture camera frame
        frame = camera.read_frame()

        if frame is None:
            print("Camera frame unavailable.")
            break

        # Process through ColNav pipeline
        result = pipeline.process_frame(
            frame,
            source="webcam"
        )

        frame_count += 1

        # Draw pedestrian bounding boxes
        for detection in result.detections:

            box = detection.bounding_box

            x1 = int(box.x1)
            y1 = int(box.y1)
            x2 = int(box.x2)
            y2 = int(box.y2)

            label = (
                f"Person {detection.confidence:.2f}"
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        # Calculate average processing FPS
        elapsed = time.perf_counter() - start_time

        average_fps = (
            frame_count / elapsed if elapsed > 0 else 0
        )

        # Display performance information
        cv2.putText(
            frame,
            f"People: {len(result.detections)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Average FPS: {average_fps:.2f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        # Display live detection
        cv2.imshow(
            "WalkJourney AI - Live Pedestrian Detection",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:

    camera.release()
    cv2.destroyAllWindows()

    print("\nLive detection stopped.")
    print("Frames processed:", frame_count)
