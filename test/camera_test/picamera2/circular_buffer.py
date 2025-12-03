import time
import cv2
import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput2, PyavOutput

# -----------------------------
# Setup Picamera2
# -----------------------------
picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={'size': (1280, 720), 'format': 'YUV420'},   # high-res recording
    lores={'size': (320, 240), 'format': 'RGB888'},   # preview stream
    display='lores',
    controls={"FrameDurationLimits": (16666, 16666)}  # ~60 FPS
)

picam2.configure(config)

# -----------------------------
# Setup encoding + circular buffer
# -----------------------------
encoder = H264Encoder(bitrate=10_000_000)
circular = CircularOutput2(buffer_duration_ms=5000)

picam2.start_recording(encoder, circular)

# -----------------------------
# Setup OpenCV preview window
# -----------------------------
cv2.namedWindow("Lores Preview", cv2.WINDOW_AUTOSIZE)

# Start first recording output
circular.open_output(PyavOutput("start.mp4"))
print("Recording start.mp4...")

start_time = time.time()

# -----------------------------
# Main loop: display preview and manage output switching
# -----------------------------
while True:
    # Grab lores frame from Picamera2
    lores_frame = picam2.capture_array("lores")

    # Display in OpenCV window
    cv2.imshow("Lores Preview", lores_frame)

    # Check if we should close the first file and open the second
    if time.time() - start_time > 5:
        print("Closing start.mp4 and switching to end.mp4...")
        circular.close_output()
        circular.open_output(PyavOutput("end.mp4"))
        break

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Continue recording for the second file
# -----------------------------
end_start = time.time()
while True:
    lores_frame = picam2.capture_array("lores")
    cv2.imshow("Lores Preview", lores_frame)

    if time.time() - end_start > 5:
        print("Closing end.mp4...")
        circular.close_output()
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Cleanup
# -----------------------------
picam2.stop_recording()
cv2.destroyAllWindows()
