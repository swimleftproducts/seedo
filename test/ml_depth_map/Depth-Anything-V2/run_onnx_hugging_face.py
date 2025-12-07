import onnxruntime as ort
import numpy as np
import cv2
import argparse
from huggingface_hub import hf_hub_download
from pathlib import Path
import os

# ------------------ Args ------------------
parser = argparse.ArgumentParser()
parser.add_argument("--img", type=str, required=True, help="Input image")
parser.add_argument("--repo", type=str, default="swimleft/depth-anything-seedo")
parser.add_argument("--model", type=str, default="depth_anything_vits.onnx")
parser.add_argument("--location", type=str, default=None)
args = parser.parse_args()

# ------------------ Get true repo root no matter where script is launched ------------------
SCRIPT_PATH = Path(__file__).resolve()

def find_repo_root(path: Path):
    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():  # detect project root
            return parent
    raise RuntimeError("Repo root not found")

ROOT = find_repo_root(SCRIPT_PATH)

# ===== THIS is your correct model folder =====
MODEL_DIR = ROOT / "models"    # <--- FINAL ANSWER

MODEL_DIR.mkdir(parents=True, exist_ok=True)

print(f"\nProject root = {ROOT}")
print(f"Model path   = {MODEL_DIR}")

# ------------------ Download Model + .data shard ------------------
print("\nChecking HuggingFace for model...")

# main ONNX
onnx_path = hf_hub_download(
    repo_id=args.repo,
    filename=args.model,
    local_dir=str(MODEL_DIR)
)

# large weight shard auto-name
data_file = args.model + ".data"
data_path = hf_hub_download(
    repo_id=args.repo,
    filename=data_file,
    local_dir=str(MODEL_DIR)
)

print(f"Model files ready:\n  {onnx_path}\n  {data_path}")

# ------------------ Load ONNX ------------------
session = ort.InferenceSession(str(onnx_path))

# ------------------ Load Image ------------------
img = cv2.imread(args.img)
orig = img.copy()

# Preprocess
img_resized = cv2.resize(img, (518,518))
inp = np.transpose(img_resized.astype(np.float32)/255, (2,0,1))[None]

# Run inference
depth = session.run(None, {"input": inp})[0][0]

# Normalize for display only
depth_norm = (depth-depth.min())/(depth.max()-depth.min())
depth_vis = (depth_norm*255).astype(np.uint8)
depth_col = cv2.applyColorMap(depth_vis, cv2.COLORMAP_MAGMA)

# Resize for lookup
H,W = orig.shape[:2]
depth_resized = cv2.resize(depth,(W,H))
depth_show = cv2.resize(depth_col,(W,H))

# Direct lookup mode
if args.location:
    x,y = map(int,args.location.split(","))
    print(f"\nDepth at ({x},{y}) = {depth_resized[y,x]:.6f}\n")
    exit()
# Create depth visualization for display (scaled down only for showing)
DISPLAY_W, DISPLAY_H = 640, 480
depth_display = cv2.resize(depth_show, (DISPLAY_W, DISPLAY_H))

# ---------- Click callback ----------
def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # convert FROM display coords TO real depth coords
        scale_x = depth_resized.shape[1] / DISPLAY_W
        scale_y = depth_resized.shape[0] / DISPLAY_H
        ox = int(x * scale_x)
        oy = int(y * scale_y)

        # safety clamp to avoid boundary crash
        ox = min(max(0, ox), depth_resized.shape[1]-1)
        oy = min(max(0, oy), depth_resized.shape[0]-1)

        print(f"Clicked ({ox},{oy})  depth={depth_resized[oy,ox]:.5f}")

# ---------- Windows ----------
cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)

cv2.imshow("Image", orig)
cv2.imshow("Depth Map", depth_display)  # <-- use display image here!
cv2.setMouseCallback("Depth Map", click)

print("\nClick depth-map window to sample values. Press Q to exit.\n")

while True:
    if cv2.waitKey(16) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()