from core.camera_manager import CameraManager
from core.seedo_manager import SeeDoManager
from core.ml.ml_manager import ML_manager
import time
from PIL import Image
import numpy as np


class AppController:
    """
    Central orchestrator for backend operations.
    Called by the UI tick loop to update camera, recording, SeeDo evaluations.
    UI never directly interacts with core modules — it only calls controller methods.
    """

    def __init__(self):
        self.camera_manager = CameraManager()
        self.seedo_manager = SeeDoManager()
        self.ml_manager = ML_manager()

        #NOTE: I could see lazy loading of models being better if there are many models
        # and a given model is not used by any SeeDo instances yet.
        self.ml_manager.Load_MobileNetV3()

    def tick(self):
        """Heartbeat invoked by UI .after() loop."""
        if self.camera_manager.active:
            self.camera_manager.capture_frame()
            self.seedo_manager.run(self.camera_manager.latest_frame, time.time())
    # -------- SEEDO CONTROL ---------

    def toggle_seedo(self, seedo_name):
        self.seedo_manager.toggle_seedo(seedo_name)
  

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

    # -------- ML CONTROL --------
    def get_embedding(self, imgs: list[Image.Image]) -> np.ndarray:
        """Get embedding from ML model for given image."""
        return self.ml_manager.mobile_net_v3.get_embedding(imgs)
    

    # -------- SHUTDOWN --------
    def shutdown(self):
        """Gracefully stop camera, recorder, and release hardware."""
        print("Controller shutdown")
        self.camera_manager.active = False
        self.camera_manager.saving = False
        self.camera_manager.release()
