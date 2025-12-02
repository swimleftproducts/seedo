from core.secrets import get_secret
import numpy as np
import cv2


def get_camera_pipeline():
  CAMERA_TYPE = get_secret('CAMERA_TYPE')
  HEIGHT = get_secret('HEIGHT')
  WIDTH = get_secret('WIDTH')
  print(CAMERA_TYPE)
  if CAMERA_TYPE == "PI":
    return CameraCapturePi
  else:
    return CameraCaptureUSB

class CameraCapture:
    def read(self) -> tuple[bool, np.ndarray]:
        raise NotImplementedError

    def release(self):
        raise NotImplementedError
    
    def set(self):
        raise NotImplementedError
    
    def isOpened(self):
        raise NotImplementedError
    
    def release(self):
        raise NotImplementedError
    

class CameraCaptureUSB(CameraCapture):
  def __init__(self, desired_width, desired_height, device_index=0):
         #select_and_configure_camera()
        self.cap = cv2.VideoCapture(device_index)

        # set camera resolution, this will fail silently if unsupported
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

        self.actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("Actual camera resolution:", self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), "x", self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

  def set(self):
    """probably not needed, can just do instance.cap.set"""
    pass
   
  def read(self):
    return self.cap.read()
   
  def isOpened(self):
    return self.cap.isOpened()

  def release(self):
    self.cap.release()
  

class CameraCapturePi(CameraCapture):
    def __init__(self, desired_width, desired_height, device_index=0):
        from picamera2 import Picamera2

        self.cap = Picamera2()

        # Create configuration using requested size
        config = self.cap.create_preview_configuration(
            main={"size": (desired_width, desired_height)}  # width, height
        )

        # Align configuration to hardware-supported modes
        self.cap.align_configuration(config)

        # Apply config and start camera
        self.cap.configure(config)
        self.cap.start()

        # Print actual resulting resolution
        frame = self.cap.capture_array()
        print(f"[PI CAMERA] configured: actual resolution = {frame.shape[1]}x{frame.shape[0]}")

    def set(self, *args, **kwargs):
        return True   # maybe useful in future

    def read(self):
        frame = self.cap.capture_array()
        return True, frame

    def isOpened(self):
        return self.isOpened

    def release(self):
        self.isOpened = False
        print("[PI CAMERA] Releasing camera")
        self.cap.stop()
        self.cap.close()

    