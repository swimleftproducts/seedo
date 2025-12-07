import onnxruntime as ort
import numpy as np
import cv2
import argparse

# ------------------ Args ------------------
parser = argparse.ArgumentParser()
parser.add_argument("--img", type=str, required=True, help="Input image")
parser.add_argument("--onnx", type=str, default="depth_anything_vits.onnx", help="Model path")
parser.add_argument("--location", type=str, default=None, help="Pixel as x,y")
args = parser.parse_args()

# ------------------ Load Model ------------------
session = ort.InferenceSession(args.onnx)

# ------------------ Load Image ------------------
img = cv2.imread(args.img)
orig = img.copy()

# Preprocess
img_resized = cv2.resize(img, (518,518))
inp = img_resized.astype(np.float32) / 255.0
inp = np.transpose(inp, (2,0,1))[None]

# ------------------ Run Model ------------------
depth = session.run(None, {"input": inp})[0][0]

# Normalize for visualization
depth_norm = (depth - depth.min()) / (depth.max() - depth.min())
depth_vis = (depth_norm * 255).astype(np.uint8)
depth_color = cv2.applyColorMap(depth_vis, cv2.COLORMAP_MAGMA)

# Resize back for lookup
depth_resized = cv2.resize(depth, (orig.shape[1], orig.shape[0]))
depth_show = cv2.resize(depth_color, (orig.shape[1], orig.shape[0]))

# ------------------ If --location provided ------------------
if args.location:
    try:
        x, y = map(int, args.location.split(","))
        value = depth_resized[y, x]
        print(f"Depth at ({x},{y}) = {value:.6f}")
    except:
        print("Invalid format. Use --location x,y")
    exit()

# ------------------ Otherwise allow click interaction ------------------
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked ({x},{y}) → depth={depth_resized[y,x]:.6f}")
        img = depth_show.copy()
        cv2.circle(img, (x,y), 4, (0,255,0), -1)
        cv2.imshow("Depth Map", img)

cv2.imshow("Input Image", orig)
cv2.imshow("Depth Map", depth_show)
cv2.setMouseCallback("Depth Map", click_event)

print("\nClick anywhere on Depth Map to print pixel depth.")
print("Or run with --location x,y to query directly.\n")

cv2.waitKey(0)
cv2.destroyAllWindows()
