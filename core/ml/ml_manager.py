import onnxruntime as ort
import numpy as np
from PIL import Image

class ML_manager:
   def __init__(self):
      self.mobile_net_v3 = None
   
   def Load_MobileNetV3(self):
      self.mobile_net_v3 = MobileNetV3()
   

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
  img = Image.open("test/vision_embedding/image/glass_on_table.png").convert("RGB")
  model = MobileNetV3()
  single_emb = model.get_image_embedding(img)
  print("Embedding shape:", single_emb.shape)

  batch_emb = model.get_image_embedding_batch([img for _ in range(40)])
  print("Embedding shape:", batch_emb.shape)
  print("Cosine similarity matrix shape:", model.cosine_similarity_matrix(batch_emb).shape)
  print("Matrix", model.cosine_similarity_matrix(batch_emb))