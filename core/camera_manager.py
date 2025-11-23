import cv2
import time
import numpy as np
import threading
from queue import Queue   
import os

class CameraManager:
    def __init__(self, target_fps=15, device_index=0, buffer_seconds=2):
        self.cap = cv2.VideoCapture(device_index)

        self.target_width = 1280
        self.target_height = 720

        # set camera resolution, this will fail silently if unsupported
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)

        print("Actual camera resolution:", self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), "x", self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.target_fps = target_fps
        self.last_frame_time = 0
        self.latest_frame = None
        self.active = False
        self.saving = False

        # Shared buffer for frame capture
        self.buffer = []
        self.buffer_lock = threading.Lock()

        # Queue for save jobs
        self.save_queue = Queue()
        self.save_thread = threading.Thread(
            target=self._save_worker, daemon=True
        )
        self.save_thread.start() 

        self.buffer_seconds = buffer_seconds
        self.max_frames = int(self.target_fps * self.buffer_seconds)

    def capture_frame(self) -> np.ndarray | None:
        """Grab frames throttled to target fps."""
        if not self.active:
            return None
        now = time.time()
        if now - self.last_frame_time >= 1 / self.target_fps:
            ret, frame = self.cap.read()
            if ret:
                self.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                success, jpeg = cv2.imencode(".jpg", frame)
                if success:
                    self.buffer.append((now, jpeg.tobytes()))

                    if len(self.buffer) >= self.max_frames:
                        if not self.saving:
                            print("Buffer full but not currently saving, clearing buffer.")
                            self.buffer.clear()
                        else:
                            self._initiate_saving()

            self.last_frame_time = now
            return self.latest_frame
        else:
            return self.latest_frame

    def _initiate_saving(self):
        """Copy buffer safely and queue work for save thread."""

        buffer_copy = self.buffer[:]
        self.buffer.clear()
        print(f"\nQueueing save job for {len(buffer_copy)} frames...")
        self.save_queue.put(buffer_copy)

    def _save_worker(self):
        """Thread worker that waits for buffer copies and writes them to disk."""
        while True:
            buffer_copy = self.save_queue.get()
            if buffer_copy is None:
                break
            self._save_buffer_internal(buffer_copy)
            self.save_queue.task_done()

    def _save_buffer_internal(self, buffer_copy):
        """Write buffer copy to AVI file."""
        print(f"Save worker: writing {len(buffer_copy)} frames...")

        t0 = time.time()
        start_time = buffer_copy[0][0]
        end_time = buffer_copy[-1][0]
        filename = f"camera_{int(start_time)}_{int(end_time)}.avi"

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(BASE_DIR, "data")

        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)


        sample_frame = cv2.imdecode(
            np.frombuffer(buffer_copy[0][1], dtype=np.uint8),
            cv2.IMREAD_COLOR
        )
        height, width, _ = sample_frame.shape

        out = cv2.VideoWriter(
            filepath,
            cv2.VideoWriter_fourcc(*"MJPG"),
            self.target_fps,
            (width, height)
        )

        for ts, jpeg_bytes in buffer_copy:
            frame = cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), cv2.IMREAD_COLOR)
            out.write(frame)

        out.release()
        elapsed = time.time() - t0
        print(f"Saved {filename} in {elapsed:.2f} seconds\n")

    def get_frame(self):
        return self.latest_frame

    def release(self):
        self.active = False
        self.save_queue.put(None)
        if self.cap and self.cap.isOpened():
            self.cap.release()