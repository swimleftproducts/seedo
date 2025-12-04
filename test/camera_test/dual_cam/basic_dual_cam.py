import cv2
import numpy as np
from picamera2 import Picamera2

# --- Initialize two cameras ---
cam0 = Picamera2(0)
cam1 = Picamera2(1)

config0 = cam0.create_video_configuration(main={"size": (4608, 2592), "format": "RGB888"})
config1 = cam1.create_video_configuration(main={"size": (4608, 2592), "format": "RGB888"})

cam0.configure(config0)
cam1.configure(config1)

cam0.start()
cam1.start()

while True:
    # Grab frames
    f0 = cam0.capture_array()
    f1 = cam1.capture_array()

    f0 = cv2.flip(f0, 0)
    f1 = cv2.flip(f1, 0)

    # Resize or match height if needed
    h, w = f0.shape[:2]
    scale = 640 / w
    f0 = cv2.resize(f0, (640, int(h * scale)))

    f1 = cv2.resize(f1, (640, int(h * scale)))

    # Combine side-by-side
    combined = np.hstack((f0, f1))

    cv2.imshow("Dual Pi Cameras", combined)

    if cv2.waitKey(1) == ord('q'):
        break

cam0.stop()
cam1.stop()
cv2.destroyAllWindows()
