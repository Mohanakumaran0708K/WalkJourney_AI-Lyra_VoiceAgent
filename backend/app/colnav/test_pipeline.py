import cv2

from app.colnav.camera import Camera
from app.colnav.pipeline import ColNavPipeline


camera = Camera()
pipeline = ColNavPipeline()

try:

    camera.open()

    while True:

        frame = camera.read_frame()

        result = pipeline.process_frame(frame)

        cv2.imshow("WalkJourney AI - ColNav", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:

    camera.release()
    cv2.destroyAllWindows()