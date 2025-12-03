from picamera2 import Picamera2
import cv2
import numpy as np

# Create Picamera2 instance
picam2 = Picamera2()

# Configure main + lores stream
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"},
    lores={"size": (320, 240), "format": "RGB888"},
    display="lores"
)

picam2.configure(config)
picam2.start()

while True:
    # Capture both streams
    frame_main = picam2.capture_array("main")
    frame_lores = picam2.capture_array("lores")

    # Resize lores display to a similar height for nice side-by-side comparison
    lores_resized = cv2.resize(frame_lores, (frame_main.shape[1] // 4, frame_main.shape[0] // 4))

    # Combine horizontally
    combined = np.hstack((frame_main, cv2.resize(lores_resized, (frame_main.shape[1], frame_main.shape[0]))))

    # Display
    cv2.imshow("Main 1280x720  |  Lores 320x240 (scaled)", combined)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
picam2.stop()
