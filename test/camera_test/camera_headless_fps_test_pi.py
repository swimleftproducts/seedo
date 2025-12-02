import time
import os
import csv
import psutil
from picamera2 import Picamera2

# ---- Config ----
FILE_OUT = "test/camera_test/fps_test.csv"
DURATION_SEC = 30
WINDOW_SEC = 5
DESIRED_WIDTH = 1280
DESIRED_HEIGHT = 720

# ---- Setup camera ----
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (DESIRED_WIDTH, DESIRED_HEIGHT)},  # (width, height)
    controls={"FrameDurationLimits": (16666, 16666)}
)

config = picam2.align_configuration(config)
print("cONFIG IS" , config)
picam2.configure(config)
picam2.start()

# Grab one frame to report actual resolution
test_frame = picam2.capture_array()
actual_h, actual_w = test_frame.shape[0], test_frame.shape[1]
print(f"[PI CAMERA] Actual resolution: {actual_w}x{actual_h}")

# ---- Setup CPU monitoring ----
pid = os.getpid()
proc = psutil.Process(pid)
proc.cpu_percent(interval=None)  # prime first reading

# ---- Timing / averaging setup ----
start_time = time.time()
prev_frame_time = start_time
window_start = start_time

fps_sum = 0.0
cpu_sum = 0.0
samples = 0

# ---- Ensure output directory exists ----
os.makedirs(os.path.dirname(FILE_OUT), exist_ok=True)

# ---- Open CSV and run test ----
with open(FILE_OUT, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["fps", "cpu"])  # 5-second averages

    while True:
        now = time.time()
        if now - start_time >= DURATION_SEC:
            break

        # Capture frame (no display)
        frame = picam2.capture_array()

        # Measure FPS based on time delta between frames
        now = time.time()
        dt = now - prev_frame_time
        if dt == 0:
            continue
        fps = 1.0 / dt
        prev_frame_time = now

        # CPU usage for this sample
        cpu = proc.cpu_percent(interval=None)

        # Accumulate into 5s window
        fps_sum += fps
        cpu_sum += cpu
        samples += 1

        # Every 5 seconds, compute and log averages
        if now - window_start >= WINDOW_SEC:
            if samples > 0:
                avg_fps = fps_sum / samples
                avg_cpu = cpu_sum / samples
                writer.writerow([f"{avg_fps:.2f}", f"{avg_cpu:.2f}"])
                print(f"Logged 5s avg -> FPS: {avg_fps:.2f}, CPU: {avg_cpu:.2f}%")

            # reset window accumulators
            fps_sum = 0.0
            cpu_sum = 0.0
            samples = 0
            window_start = now

# ---- Cleanup ----
picam2.stop()
picam2.close()
print("Done. Results written to:", FILE_OUT)
