import time
import os
import csv
import psutil
import cv2
from picamera2 import Picamera2

# ---- Config ----
FILE_OUT = "test/camera_test/fps_test.csv"
DURATION_SEC = 30
WINDOW_SEC = 5
DESIRED_WIDTH = 1280
DESIRED_HEIGHT = 720

# ---- Setup camera ----
picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (DESIRED_WIDTH, DESIRED_HEIGHT), "format": "RGB888"},
    controls={"FrameDurationLimits": (16666, 16666)}  # 60 FPS
)

picam2.configure(config)
picam2.start()

print("Applied config:", picam2.camera_config)

# ---- CPU monitoring ----
pid = os.getpid()
proc = psutil.Process(pid)
proc.cpu_percent(interval=None)

# ---- Timing setup ----
start_time = time.time()
prev_frame_time = start_time
window_start = start_time

fps_sum = 0.0
cpu_sum = 0.0
samples = 0

# ---- CSV setup ----
os.makedirs(os.path.dirname(FILE_OUT), exist_ok=True)
csvfile = open(FILE_OUT, "w", newline="")
writer = csv.writer(csvfile)
writer.writerow(["fps", "cpu"])  # 5-second averages

# ---- Display window ----
cv2.namedWindow("PiCam FPS Test", cv2.WINDOW_NORMAL)

# ---- Main Loop ----
while True:
    current = time.time()
    if current - start_time >= DURATION_SEC:
        break

    # Grab frame efficiently (non-blocking)
    request = picam2.capture_request()
    frame = request.make_array("main")
    request.release()

    # Calculate instantaneous FPS
    now = time.time()
    fps = 1.0 / (now - prev_frame_time)
    prev_frame_time = now

    cpu = proc.cpu_percent(interval=None)

    # Add text overlay
    cv2.putText(frame, f"{fps:.1f} FPS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, f"{cpu:.1f}% CPU", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("PiCam FPS Test", frame)

    # Accumulate stats
    fps_sum += fps
    cpu_sum += cpu
    samples += 1

    # Log average every WINDOW_SEC
    if now - window_start >= WINDOW_SEC:
        avg_fps = fps_sum / samples
        avg_cpu = cpu_sum / samples
        writer.writerow([f"{avg_fps:.2f}", f"{avg_cpu:.2f}"])
        print(f"Logged 5s avg -> FPS: {avg_fps:.2f}, CPU: {avg_cpu:.2f}%")

        fps_sum = 0.0
        cpu_sum = 0.0
        samples = 0
        window_start = now

    # break with q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---- Cleanup ----
csvfile.close()
picam2.stop()
picam2.close()
cv2.destroyAllWindows()

print("Done. Results written to:", FILE_OUT)
