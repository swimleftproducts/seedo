import onnxruntime as ort
import numpy as np
import cv2
import argparse
from huggingface_hub import hf_hub_download
from pathlib import Path
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="small")
args = parser.parse_args()

# -------- Select model --------
if args.model == 'small':
    model = 'depth_anything_vits.onnx'
else:
    raise ValueError("Model not found. Use --model small")

# -------- Resolve model dir --------
MODELS_DIR = 'models'
CWD = os.getcwd()
MODELS_SOURCE = os.path.join(CWD, MODELS_DIR)

print("\nChecking HuggingFace for model...")

onnx_path = hf_hub_download(
    repo_id='swimleft/depth-anything-seedo',
    filename=model,
    local_dir=str(MODELS_SOURCE)
)

data_file = model + ".data"
data_path = hf_hub_download(
    repo_id='swimleft/depth-anything-seedo',
    filename=data_file,
    local_dir=str(MODELS_SOURCE)
)

print(f"Model files ready:\n  {onnx_path}\n  {data_path}")

# Load ONNX session
session = ort.InferenceSession(str(onnx_path))

# -------- Depth Inference --------
def get_depth_map(img: np.ndarray):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # <-- convert to RGB!
    img_resized = cv2.resize(img, (518,518))
    inp = np.transpose(img_resized.astype(np.float32)/255, (2,0,1))[None]
    depth = session.run(None, {"input": inp})[0][0]  # (518,518)
    return depth

def depth_to_display(depth: np.ndarray) -> np.ndarray:
    depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    return depth_norm.astype(np.uint8)

# -------- Camera Setup --------
cap = cv2.VideoCapture(0)

# Try for higher fps
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev = time.time()
frames = 0
fps = 0

# -------- Main Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Capture failed.")
        break

    frame = cv2.resize(frame, (518,518))
    depth = get_depth_map(frame)
    depth_disp = depth_to_display(depth)
    depth_color = cv2.applyColorMap(depth_disp, cv2.COLORMAP_MAGMA)

    # FPS counter update
    frames += 1
    now = time.time()
    dt = now - prev
    if dt >= 1.0:
        fps = frames / dt
        print(f"FPS: {fps:.2f}")
        frames = 0
        prev = now

    # Overlay FPS text
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # Stack side by side
    combined = np.hstack((frame, depth_color))

    cv2.imshow("Camera + Depth", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
