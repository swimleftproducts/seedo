import cv2
import numpy as np
from picamera2 import Picamera2

BASELINE_MM = 114.3     # 4.5 inches = 114.3 mm
FOCAL_PIX = 1200        # placeholder, must be calibrated!

# --- Initialize cameras ---
cam0 = Picamera2(0)
cam1 = Picamera2(1)

config = {"size": (1536, 864), "format": "RGB888"}   # faster for depth work
cam0.configure(cam0.create_video_configuration(main=config))
cam1.configure(cam1.create_video_configuration(main=config))
cam0.start(); cam1.start()

# Stereo matcher
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,    # must be divisible by 16
    blockSize=5,
    P1=8*3*5**2,
    P2=32*3*5**2,
    uniquenessRatio=5,
    speckleWindowSize=50,
    speckleRange=1,
    disp12MaxDiff=1,
)

while True:
    # Grab frames
    L = cam0.capture_array()
    R = cam1.capture_array()

    # Flip and resize → same as your code
    L = cv2.flip(L, 0)
    R = cv2.flip(R, 0)

    def resize_640(img):
        h,w = img.shape[:2]
        return cv2.resize(img, (640, int(h*(640/w))))

    L = resize_640(L)
    R = resize_640(R)

    # Convert → grayscale for stereo matching
    grayL = cv2.cvtColor(L, cv2.COLOR_RGB2GRAY)
    grayR = cv2.cvtColor(R, cv2.COLOR_RGB2GRAY)

    # Compute disparity map
    disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0

    # Depth = (focal * baseline) / disparity
    # WARNING: needs correct calibration values
    depth = (FOCAL_PIX * BASELINE_MM) / (disparity + 1e-6)

    # Normalize for display
    disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
    disp_vis = cv2.applyColorMap(disp_vis.astype(np.uint8), cv2.COLORMAP_MAGMA)

    # Stack preview
    view = np.hstack((L, R, disp_vis))

    cv2.imshow("Left | Right | Depth", view)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam0.stop(); cam1.stop()
cv2.destroyAllWindows()
