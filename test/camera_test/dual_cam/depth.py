import cv2
import numpy as np
from picamera2 import Picamera2

# ============================
# 1. Load calibration data
# ============================
data = np.load("stereo_params.npz", allow_pickle=True)

mtxL, distL = data["mtxL"], data["distL"]
mtxR, distR = data["mtxR"], data["distR"]
R, T = data["R"], data["T"]

print("Loaded calibration.\nComputing rectification...")

# ============================
# 2. Rectification & baseline
# ============================
# Resolution must match capture resolution
FRAME_SIZE = (1536, 864)  # width, height of raw camera feed

R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
    mtxL, distL, mtxR, distR,
    FRAME_SIZE,
    R, T,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0
)

# Extract focal length + baseline directly from rectified P1/P2
fx = P1[0,0]
baseline_m = -P2[0,3] / fx    # meters
baseline_mm = baseline_m * 1000

print(f"Rectified fx = {fx:.2f} px")
print(f"Baseline = {baseline_mm:.2f} mm (~{baseline_mm/25.4:.2f} inches)")

# Precompute undistort/rectification maps
mapL1, mapL2 = cv2.initUndistortRectifyMap(mtxL, distL, R1, P1, FRAME_SIZE, cv2.CV_32FC1)
mapR1, mapR2 = cv2.initUndistortRectifyMap(mtxR, distR, R2, P2, FRAME_SIZE, cv2.CV_32FC1)

# ============================
# 3. Initialize cameras
# ============================
config = {"size": FRAME_SIZE, "format": "RGB888"}

camL = Picamera2(0)
camR = Picamera2(1)

camL.configure(camL.create_video_configuration(main=config))
camR.configure(camR.create_video_configuration(main=config))
camL.start(); camR.start()

# ============================
# 4. Stereo matcher
# ============================
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=160,    # multiple of 16
    blockSize=5,
    P1=8*3*5**2,
    P2=32*3*5**2,
    uniquenessRatio=5,
    speckleWindowSize=80,
    speckleRange=2,
    disp12MaxDiff=1
)

# ============================
# 5. Live loop
# ============================
while True:
    L = camL.capture_array()
    R = camR.capture_array()

    # Rectify
    L = cv2.remap(L, mapL1, mapL2, cv2.INTER_LINEAR)
    R = cv2.remap(R, mapR1, mapR2, cv2.INTER_LINEAR)

    # Compute disparity
    grayL = cv2.cvtColor(L, cv2.COLOR_RGB2GRAY)
    grayR = cv2.cvtColor(R, cv2.COLOR_RGB2GRAY)
    disp = stereo.compute(grayL, grayR).astype(np.float32) / 16.0

    # Compute depth map using real calibration scaling
    depth = (fx * baseline_m) / (disp + 1e-6)  # depth in meters

    # Visualization
    disp_vis = cv2.normalize(disp, None, 0, 255, cv2.NORM_MINMAX)
    disp_vis = cv2.applyColorMap(disp_vis.astype(np.uint8), cv2.COLORMAP_MAGMA)

    smallL = cv2.resize(L, (640, 360))
    smallR = cv2.resize(R, (640, 360))
    smallD = cv2.resize(disp_vis, (640, 360))

    view = np.hstack((smallL, smallR, smallD))
    cv2.imshow("LEFT | RIGHT | DEPTH", view)

    k = cv2.waitKey(1)
    if k == ord('q'):
        break

camL.stop(); camR.stop()
cv2.destroyAllWindows()
