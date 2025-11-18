from core.camera_manager import CameraManager
from core.seedo_manager import SeeDoManager
import time


class AppController:
    """
    Central orchestrator for backend operations.
    Called by the UI tick loop to update camera, recording, SeeDo evaluations.
    UI never directly interacts with core modules — it only calls controller methods.
    """

    def __init__(self):
        self.camera_manager = CameraManager()
        self.seedo_manager = SeeDoManager()

    def tick(self):
        """Heartbeat invoked by UI .after() loop."""
        if self.camera_manager.active:
            self.camera_manager.capture_frame()
            self.seedo_manager.run(self.camera_manager.latest_frame, time.time())

    # -------- CAMERA CONTROL --------
    def start_camera(self):
        print("Starting camera...")
        self.camera_manager.active = True

    def stop_camera(self):
        print("Stopping camera...")
        self.camera_manager.active = False

    # -------- RECORDING CONTROL --------
    def start_recording(self):
        print("Recording enabled")
        self.camera_manager.saving = True

    def stop_recording(self):
        print("Recording disabled")
        self.camera_manager.saving = False

    # -------- SHUTDOWN --------
    def shutdown(self):
        """Gracefully stop camera, recorder, and release hardware."""
        print("Controller shutdown")
        self.camera_manager.active = False
        self.camera_manager.saving = False
        self.camera_manager.release()
