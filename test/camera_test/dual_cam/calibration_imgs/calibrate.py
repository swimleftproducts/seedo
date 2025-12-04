import cv2
import numpy as np
import glob

# =========================
# Calibration Settings
# =========================
CHECKERBOARD = (7, 9)     # inner corner count
SQUARE_SIZE = 20.32       # mm per square

# convert to meters if desired
SQUARE_SIZE_M = SQUARE_SIZE / 1000.0

# =========================
# Prepare object points
# =========================
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE_M   # scale to real world units

objpoints = []  # 3D points
imgpointsL = [] # 2D left image points
imgpointsR = [] # 2D right image points

# =========================
# Load image pairs
# =========================
left_images  = sorted(glob.glob("test/camera_test/dual_cam/calibration_imgs/left_*.jpg"))
right_images = sorted(glob.glob("test/camera_test/dual_cam/calibration_imgs/right_*.jpg"))

assert len(left_images) == len(right_images) and len(left_images) > 0, \
    "Left/right image counts mismatch or zero."

print(f"Found {len(left_images)} stereo pairs")

# =========================
# Detect corners
# =========================
for l_img, r_img in zip(left_images, right_images):
    imgL = cv2.imread(l_img)
    imgR = cv2.imread(r_img)

    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    retL, cornersL = cv2.findChessboardCorners(grayL, CHECKERBOARD, None)
    retR, cornersR = cv2.findChessboardCorners(grayR, CHECKERBOARD, None)

    if retL and retR:
        objpoints.append(objp)

        cornersL = cv2.cornerSubPix(grayL, cornersL, (11,11), (-1,-1),
                   (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        cornersR = cv2.cornerSubPix(grayR, cornersR, (11,11), (-1,-1),
                   (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        imgpointsL.append(cornersL)
        imgpointsR.append(cornersR)

        print(f"✔ Corners detected: {l_img} + {r_img}")
    else:
        print(f"✘ Failed: {l_img} / {r_img}")

print("Corner detection complete.")

# =========================
# Calibrate individual cameras
# =========================
retL, mtxL, distL, _, _ = cv2.calibrateCamera(objpoints, imgpointsL, grayL.shape[::-1], None, None)
retR, mtxR, distR, _, _ = cv2.calibrateCamera(objpoints, imgpointsR, grayR.shape[::-1], None, None)

print("\n--- Intrinsic Results ---")
print("Left Camera Matrix:\n", mtxL)
print("Right Camera Matrix:\n", mtxR)

# =========================
# Stereo Calibrate
# =========================
flags = cv2.CALIB_FIX_INTRINSIC
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)

retStereo, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpointsL, imgpointsR,
    mtxL, distL, mtxR, distR,
    grayL.shape[::-1], criteria=criteria, flags=flags
)

print("\n--- Stereo Calibration Results ---")
print("Reprojection Error:", retStereo)
print("Rotation (R):\n", R)
print("Translation (T):\n", T, " <-- Baseline estimate (should be ~4.5\" ≈ 0.114m)")
print("Saved as stereo_params.npz")

# =========================
# Save for later depth use
# =========================
np.savez("stereo_params.npz",
         mtxL=mtxL, distL=distL,
         mtxR=mtxR, distR=distR,
         R=R, T=T, E=E, F=F)
