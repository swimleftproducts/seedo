import onnxruntime as ort
import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
import os
import threading
import time
import cv2 as cv2


class ML_manager:
  def __init__(self):
      self.mobile_net_v3 = None
      self.depth_anything_v2_vits_518 = None
      self.depth_anything_v2_vits_378 = None
   
  def Load_MobileNetV3(self):
    self.mobile_net_v3 = MobileNetV3()
  
  def Load_DepthAnythingV2(self):
    print('loading depth anything v2')
    self.depth_anything_v2_vits_378 = DepthAnythingV2(378)

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
    depth = np.log(depth + 1e-6)   # compress far range
    depth = (depth - depth.min()) / (depth.max() - depth.min())
    depth = (depth * 255).astype(np.uint8)
    return cv2.cvtColor(depth, cv2.COLOR_GRAY2BGR)

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

class MobileNetV3:
  def __init__(self):
    self.session = ort.InferenceSession("core/ml/mobilenetv3_embed_batch.onnx")
    self.input_name = self.session.get_inputs()[0].name

  def get_image_embedding(self, pil: Image.Image) -> np.ndarray:
    batch = np.vstack([self.preprocess(pil)])   # list for batching
    out = self.session.run(None, {self.input_name: batch})[0]
    return out.squeeze()                        # (576,)

  def get_image_embedding_batch(self, imgs: list[Image.Image]) -> np.ndarray:
    batch = np.vstack([self.preprocess(img) for img in imgs])
    out = self.session.run(None, {self.input_name: batch})[0]
    return out.squeeze()    

  def get_embedding_batch(self, imgs: list[Image.Image]):
    batch = np.vstack([self.preprocess(img) for img in imgs])
    out = self.session.run(None, {self.input_name: batch})[0] # run inference
    return out  # (N, embedding_dim)

  def cosine_similarity_matrix(self, embeddings):
    # Normalize row-wise
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms

    # Cosine similarity = normalized dot normalized^T
    sim_matrix = np.dot(normalized, normalized.T)
    return sim_matrix  

  def preprocess(self, pil: Image.Image) -> np.ndarray:
    #Note: do I care about resize options?
    img = pil.resize((224, 224), Image.Resampling.LANCZOS)
    arr = np.array(img).astype(np.float32) / 255.0

    # ImageNet normalization values
    mean = np.array([0.485, 0.456, 0.406])
    std  = np.array([0.229, 0.224, 0.225])

    arr = (arr - mean) / std   # normalize
    arr = arr.transpose(2, 0, 1)  # HWC -> CHW
    return arr[np.newaxis, ...].astype(np.float32)   # (1,3,224,224)
  
  def slice_roi_from_image(self, pil: Image.Image, roi: tuple[int, int, int, int]) -> Image.Image:
    x1, y1, x2, y2 = roi
    return pil.crop((x1, y1, x2, y2))


if __name__ == "__main__":
  # Example with ./glass_on_table.png
  # img = Image.open("test/vision_embedding/image/glass_on_table.png").convert("RGB")
  # model = MobileNetV3()
  # single_emb = model.get_image_embedding(img)
  # print("Embedding shape:", single_emb.shape)

  # batch_emb = model.get_image_embedding_batch([img for _ in range(40)])
  # print("Embedding shape:", batch_emb.shape)
  # print("Cosine similarity matrix shape:", model.cosine_similarity_matrix(batch_emb).shape)
  # print("Matrix", model.cosine_similarity_matrix(batch_emb))

  # calling deepth_anythinv2

  depth_v2 = DepthAnythingV2()
  img = cv2.imread('core/ml/with_part.jpg')
  depth_v2.start_running_depth_map()
  depth_v2.request_depth(img)
  time.sleep(5)
  depth_gray = depth_v2.raw_to_gray_scale(depth_v2.last_depth_map)
  h,w = img.shape[:2]
  depth_gray_full = cv2.resize(depth_gray, (w, h))
  cv2.imwrite('demo2.png',depth_gray_full)
  import pdb
  pdb.set_trace()
