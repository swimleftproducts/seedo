import cv2
import time
import psutil
import os

pid = os.getpid()
p = psutil.Process(pid)
p.cpu_percent(interval=None)


cap = cv2.VideoCapture(0)

# Force MJPEG (required for FPS > ~10 on Pi)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

# Try your desired resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Try to request higher FPS
cap.set(cv2.CAP_PROP_FPS, 30)

time.sleep(0.2)

print("Actual width :", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Actual height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Driver FPS   :", cap.get(cv2.CAP_PROP_FPS))

now = time.time()
prev = now

#used for cpu usage presentation
last_cpu_check = now
cpu_usage = 0


while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    fps = 1.0 / (now - prev)
    prev = now

    if now - last_cpu_check > 0.5:
        cpu_usage = p.cpu_percent(interval=None)
        last_cpu_check = now

    cv2.putText(frame, f"CPU: {cpu_usage:.1f}%", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"{fps:.1f} FPS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("FPS Test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
