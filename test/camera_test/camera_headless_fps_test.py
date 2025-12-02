import cv2
import time
import psutil
import os
import csv

# Output file location
FILE_OUT = 'test/camera_test/fps_test.csv'

# Setup process monitoring
pid = os.getpid()
p = psutil.Process(pid)
p.cpu_percent(interval=None)  # prime initial reading

# Setup camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # force MJPG
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

time.sleep(0.3)

print("Actual width :", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Actual height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Driver FPS   :", cap.get(cv2.CAP_PROP_FPS))

# Timing setup
start_time = time.time()
prev_frame_time = start_time

# For averaging 5-second windows
fps_sum = 0.0
cpu_sum = 0.0
samples = 0
window_start = start_time

# Ensure directory exists
os.makedirs(os.path.dirname(FILE_OUT), exist_ok=True)

# Write CSV
with open(FILE_OUT, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["fps", "cpu"])

    # Run for 30 seconds
    while time.time() - start_time < 30:
        ret, frame = cap.read()
        if not ret:
            break

        now = time.time()
        fps = 1.0 / (now - prev_frame_time)
        prev_frame_time = now

        cpu = p.cpu_percent(interval=None)

        # accumulate values
        fps_sum += fps
        cpu_sum += cpu
        samples += 1

        # Every 5 seconds compute and log averages
        if now - window_start >= 5.0:
            avg_fps = fps_sum / samples
            avg_cpu = cpu_sum / samples
            writer.writerow([f"{avg_fps:.2f}", f"{avg_cpu:.2f}"])
            print(f"Logged: FPS={avg_fps:.2f}, CPU={avg_cpu:.2f}")

            # reset accumulators
            fps_sum = 0.0
            cpu_sum = 0.0
            samples = 0
            window_start = now

cap.release()
print("Done. Results written to:", FILE_OUT)
