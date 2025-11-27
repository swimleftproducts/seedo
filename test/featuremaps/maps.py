import cv2
import numpy as np

# -----------------------------
# Load image
# -----------------------------
img_path = "test/featuremaps/glass_on_table.png"
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Could not load image at {img_path}")

h, w, _ = img.shape

# -----------------------------
# Draw grid lines every 50 pixels
# -----------------------------
grid_size = 50

for x in range(0, w, grid_size):
    cv2.line(img, (x, 0), (x, h), color=(0, 255, 0), thickness=1)
    cv2.putText(img, str(x), (x+2, 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

for y in range(0, h, grid_size):
    cv2.line(img, (0, y), (w, y), color=(0, 255, 0), thickness=1)
    cv2.putText(img, str(y), (2, y+12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    

#render rectange at {200, 500, 120, 620}
# Both bounding boxes and labels on same image
cv2.rectangle(img, (145, 140), (695, 585), (0,255,0), 2)
cv2.putText(img, "openai", (145, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

cv2.rectangle(img, (145, 140), (695, 585), (255,0,0), 1)
cv2.putText(img, "gemini", (145, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

# -----------------------------
# Show final image
# -----------------------------
cv2.imshow("Grid Overlay", img)
cv2.imwrite("grid_output.png", img)

cv2.waitKey(0)
cv2.destroyAllWindows()

# Optionally save output:
