import onnxruntime as ort
import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
import os
import threading
import time
import cv2 as cv2


class DepthAnythingV2:

  def __init__(self, model_resolution = 378):

    self._lock = threading.Lock()

    self.model_resolution = model_resolution
    self.last_depth_map = None
    self.last_depth_ts = 0.0

    self._pending_frame = None
    self._last_run = 0.0

    self._worker = None
    self._run_event = threading.Event()
  
    model_path = self._download_models(model_resolution)
    self.session = self._create_session(model_path)

    
  def request_depth(self, frame):
    reszied_frame = cv2.resize(frame, (self.model_resolution, self.model_resolution), interpolation=cv2.INTER_NEAREST)
    with self._lock:
      self._pending_frame = reszied_frame.copy()

  def start_running_depth_map(self):
    if self._worker and self._worker.is_alive():
      return
    self._run_event.set()
    self._worker = threading.Thread(
        target=self._depth_map_worker, daemon=True
    )
    self._worker.start()    

  def stop_running_depth_map(self):
    self._run_event.clear()
    
  def _depth_map_worker(self):
    while self._run_event.is_set():
      frame = None
      with self._lock:
          if self._pending_frame is not None:
              frame = self._pending_frame
              self._pending_frame = None
      
      if frame is not None:
        depth = self.get_depth_map(frame)
        self.last_depth_map = depth
        self.last_depth_ts = time.time()

      time.sleep(0.05) 

    print('_depth_map_worker is terminating')

  def raw_to_gray_scale(self, depth: np.ndarray) -> np.ndarray:
    depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
    depth = depth.astype(np.uint8)
    depth = np.repeat(depth[..., np.newaxis], 3, axis=-1)
    return depth

  def _create_session(self, model_path):
    so = ort.SessionOptions()
    so.intra_op_num_threads = os.cpu_count()   
    so.execution_mode = ort.ExecutionMode.ORT_PARALLEL
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(
        model_path,
        sess_options=so,
        providers=["CPUExecutionProvider"]  # or CoreMLExecutionProvider first
    )
    return session

  def get_depth_map(self, frame: np.ndarray) -> np.ndarray:
    """The image size must match the model loaded"""
    inp = np.transpose(frame.astype(np.float32) / 255.0, (2,0,1))[None]
    print('starting inference')
    return self.session.run(None, {"input": inp})[0][0]

  def _download_models(self, model_resolution):
    model = f"depth_anything_vits_{model_resolution}.onnx"
    MODELS_DIR = "models"
    # models will be found on hugging face
    MODEL_PATH = hf_hub_download(
    repo_id="swimleft/depth-anything-seedo",
    filename=model,
    local_dir=MODELS_DIR
    )
    hf_hub_download(
        repo_id="swimleft/depth-anything-seedo",
        filename=model + ".data",
        local_dir=MODELS_DIR
    )
    print(f"\nModel loaded from: {MODEL_PATH}")
    return MODEL_PATH