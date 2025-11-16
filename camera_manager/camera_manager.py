import cv2
import time

class CameraManager:
    def __init__(self, target_fps=15, device_index=0):
        self.cap = cv2.VideoCapture(device_index)
        self.target_fps = target_fps
        self.last_frame_time = 0
        self.latest_frame = None
        self.active = True

    def capture_frame(self):
        """Grab frames throttled to target fps."""
        if not self.active:
            return

        now = time.time()
        if now - self.last_frame_time >= 1 / self.target_fps:
            ret, frame = self.cap.read()
            if ret:
                self.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.last_frame_time = now

    def get_frame(self):
        """Return the most recent grabbed frame."""
        return self.latest_frame

    def release(self):
        self.active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
