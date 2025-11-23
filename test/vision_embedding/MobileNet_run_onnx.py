# test_embed_onnx.py

import numpy as np
from PIL import Image
import onnxruntime as ort
import timeit
import numpy as np

# Load ONNX session
session = ort.InferenceSession("test/vision_embedding/mobilenetv3_embed_batch.onnx")
input_name = session.get_inputs()[0].name

def preprocess(pil):
    img = pil.resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406])
    std  = np.array([0.229, 0.224, 0.225])

    arr = (arr - mean) / std   # normalize
    arr = arr.transpose(2, 0, 1)  # HWC -> CHW
    return arr[np.newaxis, ...].astype(np.float32)   # (1,3,224,224)


def get_embedding_batch(imgs: list[Image.Image]):
    batch = np.vstack([preprocess(img) for img in imgs])
    out = session.run(None, {input_name: batch})[0] # run inference
    return out  # (N, embedding_dim)

def get_embedding(img: Image.Image):
    x = preprocess(img)
    out = session.run(None, {input_name: x})[0] # run inference
    return out.flatten()                        # numpy vector

def similarity(e1, e2):
    e1 = np.array(e1, dtype=np.float32)
    e2 = np.array(e2, dtype=np.float32)

    dot = np.dot(e1, e2)
    norm1 = np.linalg.norm(e1)
    norm2 = np.linalg.norm(e2)

    return float(dot / (norm1 * norm2))

def cosine_similarity_matrix(embeddings):
    # Normalize row-wise
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms

    # Cosine similarity = normalized dot normalized^T
    sim_matrix = np.dot(normalized, normalized.T)
    return sim_matrix


def compare_images():
    ref_path = "test/vision_embedding/image/same_A.png"
    no_glass_path = "test/vision_embedding/image/same_B.png"
    diff_table_path = "test/vision_embedding/image/glass_on_table_2.png"

    img_ref = Image.open(ref_path).convert("RGB")
    img_none = Image.open(no_glass_path).convert("RGB")
    img_diff = Image.open(diff_table_path).convert("RGB")

    emb_ref = get_embedding(img_ref)
    emb_none = get_embedding(img_none)
    emb_diff = get_embedding(img_diff)

    print("Similarity(A vs B):", similarity(emb_ref, emb_none))
    print("Similarity(ref vs glass_diff_table):", similarity(emb_ref, emb_diff))


def compare_images_batch() :
    ref_path = "test/vision_embedding/image/glass_on_table.png"
    no_glass_path = "test/vision_embedding/image/table_no_glass.png"
    diff_table_path = "test/vision_embedding/image/glass_on_table_2.png"

    img_ref = Image.open(ref_path).convert("RGB")
    img_none = Image.open(no_glass_path).convert("RGB")
    img_diff = Image.open(diff_table_path).convert("RGB")

    embeddings = get_embedding_batch([img_ref, img_none, img_diff])
    embeddings = embeddings.squeeze()
    sim_matrix = cosine_similarity_matrix(embeddings)
    print(sim_matrix)

    emb_ref, emb_none, emb_diff = [e.flatten() for e in embeddings]
    print("Batch Similarity(ref vs no_glass):", similarity(emb_ref, emb_none))
    print("Batch Similarity(ref vs glass_diff_table):", similarity(emb_ref, emb_diff))

if __name__ == "__main__":
    start = timeit.default_timer()
    compare_images()
    end = timeit.default_timer()
    print(f"ONNX inference time single: {end - start:.4f} seconds")

    # start = timeit.default_timer()
    # compare_images_batch()
    # end = timeit.default_timer()
    # print(f"ONNX inference time batch: {end - start:.4f} seconds")
