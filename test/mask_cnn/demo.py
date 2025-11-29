import torch
import torchvision
from torchvision.transforms import functional as F
import numpy as np
import cv2
from PIL import Image

# -----------------------------
# Load image
# -----------------------------
img_path = "test/mask_cnn/roi_image_0.png"
image = Image.open(img_path).convert("RGB").crop((0,0,550,482))
print(image.size)
img_tensor = F.to_tensor(image)

# -----------------------------
# Load pretrained Mask R-CNN
# -----------------------------
print("Loading model...")
model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights="COCO_V1")
model.eval()

import torchvision

weights = torchvision.models.detection.MaskRCNN_ResNet50_FPN_Weights.COCO_V1
categories = weights.meta["categories"]


# -----------------------------
# Predict
# -----------------------------
with torch.no_grad():
    prediction = model([img_tensor])

# -----------------------------
# Inspect predictions
# -----------------------------
print("\nRaw scores (top 10):", prediction[0]["scores"][:10])
print("Raw labels (top 10):", prediction[0]["labels"][:10])

# Convert outputs to numpy safely
scores = np.array(prediction[0]["scores"])
labels = np.array(prediction[0]["labels"])
boxes = np.array(prediction[0]["boxes"])
masks = np.array(prediction[0]["masks"])

# Filter by threshold
threshold = 0.80  # low for debugging
keep = scores > threshold

boxes = boxes[keep]
labels = labels[keep]
masks = masks[keep]
scores = scores[keep]

print(f"\nDetections above threshold = {len(boxes)}")

# COCO classes
COCO_INSTANCE_CATEGORY_NAMES = categories

# -----------------------------
# Draw results
# -----------------------------
img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

if len(boxes) == 0:
    print("⚠️ No valid detections. Saving original image with note.")
    cv2.putText(img_cv, "NO DETECTIONS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
else:
  for i, box in enumerate(boxes):
      x1, y1, x2, y2 = box.astype(int)

      cv2.rectangle(img_cv, (x1, y1), (x2, y2), (255, 0, 0), 2)

      # SAFE LABEL HANDLING
      label_idx = int(labels[i])
      if 0 <= label_idx < len(COCO_INSTANCE_CATEGORY_NAMES):
          label_name = COCO_INSTANCE_CATEGORY_NAMES[label_idx]
      else:
          label_name = f"unknown_{label_idx}"

      score = float(scores[i])

      cv2.putText(
          img_cv, f"{label_name} {score:.2f}",
          (x1, y1 - 10),
          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2
      )

      # Mask handling
      mask = masks[i, 0]
      mask = (mask > 0.5).astype(np.uint8)

      colored_mask = np.zeros_like(img_cv)
      colored_mask[:, :, 1] = mask * 255
      img_cv = cv2.addWeighted(img_cv, 1.0, colored_mask, 0.45, 0)

      if i>3:
        break


# -----------------------------
# Save result
# -----------------------------
output_path = "output_maskrcnn.png"
cv2.imwrite(output_path, img_cv)
print(f"\nSaved visualization → {output_path}")
