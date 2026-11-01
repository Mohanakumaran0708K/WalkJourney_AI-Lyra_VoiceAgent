import cv2

from app.colnav.camera import Camera


camera = Camera()

try:

    camera.open()

    while True:

        frame = camera.read_frame()

        cv2.imshow("WalkJourney AI - Camera Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:

    camera.release()
    cv2.destroyAllWindows()