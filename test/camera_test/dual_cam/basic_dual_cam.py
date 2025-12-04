import cv2
from picamera2 import Picamera2
import numpy as np

# --- Initialize two Pi cameras ---
cam1 = Picamera2()
cam2 = Picamera2()

# Configure both cameras
config1 = cam1.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
config2 = cam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})

cam1.configure(config1)
cam2.configure(config2)

cam1.start()
cam2.start()

while True:
    # grab frames from both cameras
    f1 = cam1.capture_array()
    f2 = cam2.capture_array()

    # Resize if needed to match (optional)
    h = min(f1.shape[0], f2.shape[0])
    f1 = cv2.resize(f1, (640, h))
    f2 = cv2.resize(f2, (640, h))

    # --- Combine side-by-side ---
    combined = np.hstack((f1, f2))   # left | right

    cv2.imshow("Dual PiCam View", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam1.stop()
cam2.stop()
cv2.destroyAllWindows()
