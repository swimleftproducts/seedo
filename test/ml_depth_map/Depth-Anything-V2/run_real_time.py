import onnxruntime as ort
import numpy as np
import cv2
import argparse
from huggingface_hub import hf_hub_download
import os, time

# Optional PiCamera2 support
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None


# ------------------------------------------------------------
# CLI ARGS
# ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="small")
parser.add_argument("--resolution", type=int, default='518')
parser.add_argument("--camera", type=str, choices=["opencv","pi"], default="opencv",
                    help="Select camera backend: opencv or pi")
args = parser.parse_args()


# ------------------------------------------------------------
# Model selection & download
# ------------------------------------------------------------
if args.model == "small":
    if args.resolution == 378:
      model = "depth_anything_vits_378.onnx"
    else:
      model = "depth_anything_vits.onnx"
    
elif args.model == 'fp16':
    model = "depth_anything_vits_fp16.onnx"
else:
    raise ValueError("Unknown model. Use --model small")


MODELS_DIR = "models"
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

so = ort.SessionOptions()
so.intra_op_num_threads = os.cpu_count()     # threads inside one op
so.execution_mode = ort.ExecutionMode.ORT_PARALLEL
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL


session = ort.InferenceSession(
    MODEL_PATH,
    sess_options=so,
    providers=["CPUExecutionProvider"]  # or CoreMLExecutionProvider first
)
#session = ort.InferenceSession(str(MODEL_PATH))


# ------------------------------------------------------------
# Depth processing
# ------------------------------------------------------------
def get_depth_map(img: np.ndarray):
    # Convert BGR → RGB for ONNX model
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Normalize + reorder (FAST)
    inp = np.transpose(img.astype(np.float32) / 255.0, (2,0,1))[None]
    start = time.time()
    depth = session.run(None, {"input": inp})[0][0]
    end = time.time()
    print('inference took: ', end -start)
    return depth     # raw float map (518x518)


def depth_to_display(depth: np.ndarray):
    depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    return depth_norm.astype(np.uint8)


# ------------------------------------------------------------
# Camera setup
# ------------------------------------------------------------
def init_camera():
    if args.camera == "opencv":
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap

    if args.camera == "pi":
        if Picamera2 is None:
            raise ImportError("Install Picamera2 first: pip install picamera2")

        cam = Picamera2()
        cam.configure(cam.create_preview_configuration(main={"size": (1280,720)}))
        cam.start()
        return cam


def read_frame(camera):
    """Return a BGR numpy frame regardless of backend."""
    if args.camera == "opencv":
        ret, frame = camera.read()
        return frame if ret else None

    if args.camera == "pi":
        frame = camera.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Pi → BGR like OpenCV


# ------------------------------------------------------------
# Main Loop
# ------------------------------------------------------------
camera = init_camera()
prev = time.time()
frames = 0
fps = 0

print("\nStarting depth stream... Press 'q' to exit.\n")

while True:
    frame = read_frame(camera)
    if frame is None:
        print("Camera read failed.")
        break
    
    frame = cv2.resize(frame,(args.resolution,args.resolution))
    depth = get_depth_map(frame)
    depth_disp = depth_to_display(depth)
    depth_color = cv2.applyColorMap(depth_disp, cv2.COLORMAP_MAGMA)

    # Resize only ONCE for display

    # FPS update
    frames += 1
    now = time.time()
    if now - prev >= 1.0:
        fps = frames / (now - prev)
        print(f"FPS: {fps:.2f}")
        frames = 0
        prev = now

    cv2.putText(frame, f"{fps:.1f} FPS", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    combined = np.hstack((frame, depth_color))
    cv2.imshow("RGB + Depth", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------
if args.camera == "opencv":
    camera.release()

cv2.destroyAllWindows()
print("Exit complete.")
