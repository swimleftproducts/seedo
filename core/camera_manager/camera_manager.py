import cv2
import time
import numpy as np
import threading
from queue import Queue   
import os
from typing import List
from core.camera_manager.camera_pipeline import get_camera_pipeline
import timeit

CAM_DATA_DIR ='data/video'

class CameraManager:
    def __init__(self, target_fps=30, device_index=0, buffer_seconds=2):

        self.target_width = 1280
        self.target_height = 720

        self.video_retention_time_sec = 60 
        self.last_video_clear = time.time()


        pipeline_class = get_camera_pipeline()

        self.cap = pipeline_class(self.target_width, self.target_height,0)
        # set camera resolution, this will fail silently if unsupported

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
        #TODO: adding + .01 here gets the fps closer to actually 15. Do I care?
        if (now - self.last_frame_time  )>= (1 / self.target_fps):
            start = timeit.default_timer()

            ret, frame = self.cap.read()
            if ret:
                # uncomment last line to see actual frame rate
                print(f"actual frame rate: {1/(now-self.last_frame_time)}")
                self.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.buffer.append((now, frame.copy()))

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
        data_dir = os.path.join(BASE_DIR, CAM_DATA_DIR)

        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)


        sample_frame = buffer_copy[0][1]
        height, width, _ = sample_frame.shape

        out = cv2.VideoWriter(
            filepath,
            cv2.VideoWriter_fourcc(*"MJPG"),
            self.target_fps,
            (width, height)
        )

        for ts, frame in buffer_copy:
            out.write(frame)

        out.release()
        elapsed = time.time() - t0
        print(f"Saved {filename} in {elapsed:.2f} seconds\n")

    def clear_old_videos(self):
        """Spawn a background thread to clean old video files."""
        now = time.time()
        if now - self.last_video_clear > self.video_retention_time_sec:
            self.last_video_clear = now
            threading.Thread(
                target=self._clear_old_video_worker,
                daemon=True
            ).start()

    def _clear_old_video_worker(self):
        """Delete video clips older than retention threshold."""
        cutoff = time.time() - self.video_retention_time_sec

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(BASE_DIR, CAM_DATA_DIR)

        all_files = [
            f for f in os.listdir(data_dir)
            if f.startswith("camera_") and f.endswith(".avi")
        ]

        removed_count = 0
        removed_bytes = 0

        for f in all_files:
            try:
                _, s, e = f[:-4].split("_")
                end_ts = float(e)
            except:
                continue

            if end_ts < cutoff:
                filepath = os.path.join(data_dir, f)
                try:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    removed_count += 1
                    removed_bytes += file_size
                    print(f"Deleted old video: {filepath}")
                except Exception as err:
                    print("Failed to remove:", filepath, "Error:", err)

        if removed_count > 0:
            print(f"Cleanup complete: {removed_count} files removed "
                f"({removed_bytes / (1024*1024):.2f} MB freed)")
        else:
            print("Cleanup complete: no old files found.")

    def _list_video_files_by_time(self, start: float, end: float) -> List[str]:
        """Return full paths to video files whose timestamps overlap [start, end]."""
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(BASE_DIR, CAM_DATA_DIR)

        all_files = [
            f for f in os.listdir(data_dir)
            if f.startswith("camera_") and f.endswith(".avi")
        ]

        matched = []
        for f in all_files:
            try:
                # f = camera_<start>_<end>.avi
                _, s, e = f[:-4].split("_")
                start_ts = float(s)
                end_ts = float(e)
            except:
                continue

            # Overlap check
            if end_ts >= start and start_ts <= end:
                matched.append(os.path.join(data_dir, f))

        return sorted(matched)

    def combine_avi_segments(self, output_path, avi_files, fps=15):

        if not avi_files:
            print("No files provided to combine.")
            return None

        # Determine frame size from the first video
        cap = cv2.VideoCapture(avi_files[0])
        if not cap.isOpened():
            print("Failed to open:", avi_files[0])
            return None

        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height)
        )

        # Append frames sequentially
        for filename in avi_files:
            print("Appending:", filename)
            cap = cv2.VideoCapture(filename)

            if not cap.isOpened():
                print("Skipping unreadable file:", filename)
                continue

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                writer.write(frame)

            cap.release()

        writer.release()
        print("Done combining:", output_path)
        return output_path


    def get_and_combine_past_video(self, length, time_end):
        """
        Determine which AVI files overlap the desired time window and
        call an existing combine helper to merge them.
        """
        target_end = time_end
        target_start = target_end - length

        selected = self._list_video_files_by_time(target_start, target_end)

        if not selected:
            print("No segments found in range.")
            return None

        selected.sort()  # chronological

        outfile = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            CAM_DATA_DIR,
            f"combined_{int(target_start)}_{int(target_end)}.mp4"
        )

        return self.combine_avi_segments(outfile, selected)

    def release(self):
        self.active = False
        self.save_queue.put(None)
        if self.cap and self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    # --------- HARD-CODE THESE ---------
    # Example: use a known "event time" (Unix timestamp, float or int)
    START_TIME = 1764270489   # <-- replace with your real timestamp
    LENGTH_SEC = 100            # window length in seconds
    TIME_IN_PAST = 0          # 0 = window ends exactly at START_TIME
    # -----------------------------------

    print("Using parameters:")
    print(f"  START_TIME  = {START_TIME}")
    print(f"  LENGTH_SEC  = {LENGTH_SEC}")
    print(f"  TIME_IN_PAST= {TIME_IN_PAST}")

    # We don't actually need the camera; we just reuse the class logic.
    cam = CameraManager(target_fps=15)

    combined_path = cam.get_and_combine_past_video(
        length=LENGTH_SEC,
        time_end=START_TIME,
    )

    cam.release()
