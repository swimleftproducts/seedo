import cv2
import time

# Set camera index (0 = first USB cam)
cap = cv2.VideoCapture(0)

# --- Try MJPEG mode for higher FPS ---
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 60)            # request 60fps (camera dependent)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev = time.time()
frames = 0
fps=0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Capture failed.")
        break

    frames += 1
    now = time.time()
    dt = now - prev

    # update FPS every second
    if dt >= 1.0:
        fps = frames / dt
        print(f"FPS: {fps:.2f}")
        frames = 0
        prev = now

    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow('Camera FPS Test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
