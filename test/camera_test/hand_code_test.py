from picamera2 import Picamera2
import time

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"},
    controls={"FrameDurationLimits": (16666, 16666)}  # 1/60s -> 60 FPS
)

picam2.configure(config)
picam2.start()

time.sleep(0.5)

start = time.time()
frames = 0

while time.time() - start < 5:
    picam2.capture_array()
    frames += 1

print("FPS:", frames / 5)
