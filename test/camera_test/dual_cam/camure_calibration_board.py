import cv2
import os
from picamera2 import Picamera2

SAVE_DIR = "captures"
os.makedirs(SAVE_DIR, exist_ok=True)

camL = Picamera2(0)
camR = Picamera2(1)

# choose resolution (change if needed)
config = {"size": (1536, 864), "format": "RGB888"}

camL.configure(camL.create_still_configuration(main=config))
camR.configure(camR.create_still_configuration(main=config))

camL.start()
camR.start()

counter = 1

print("Preview started.")
print("Press ENTER to capture left+right images")
print("Press Q to quit")

while True:
    frameL = camL.capture_array()
    frameR = camR.capture_array()

    # optional flip if your cameras are upside down
    # frameL = cv2.flip(frameL, 0)
    # frameR = cv2.flip(frameR, 0)

    # show preview side-by-side
    preview = cv2.resize(frameL, (640,360)), cv2.resize(frameR, (640,360))
    preview = cv2.hconcat(preview)

    cv2.imshow("Left | Right", preview)

    key = cv2.waitKey(1)

    if key == 13:  # ENTER key
        left_path = f"{SAVE_DIR}/left_{counter:03d}a.jpg"
        right_path = f"{SAVE_DIR}/right_{counter:03d}a.jpg"

        cv2.imwrite(left_path, frameL)
        cv2.imwrite(right_path, frameR)

        print(f"Captured pair #{counter} → {left_path}, {right_path}")
        counter += 1

    elif key == ord('q'):
        break

camL.stop()
camR.stop()
cv2.destroyAllWindows()
