import torch
from depth_anything_v2.dpt import DepthAnythingV2
import cv2
import time
import numpy as np
import matplotlib 

cmap = matplotlib.colormaps.get_cmap('Spectral_r')


print(torch.backends.mps.is_available())
print(torch.cuda.is_available())
DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'

print(DEVICE)

encoder = "vits"  # change if using vits/vitb
checkpoint = f"test/ml_depth_map/Depth-Anything-V2/checkpoints/depth_anything_v2_{encoder}.pth"

model_configs = {
    'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
    'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
}

model = DepthAnythingV2(**model_configs[encoder])
model.load_state_dict(torch.load(checkpoint, map_location="cpu"))
model.to(DEVICE).eval()


img = cv2.imread('test/ml_depth_map/Depth-Anything-V2/shopmadepallet1.jpg')

start = time.time()
depth = model.infer_image(img, 518)
end = time.time()

print('inference took :', end-start)

depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
depth = depth.astype(np.uint8)


depth = (cmap(depth)[:, :, :3] * 255)[:, :, ::-1].astype(np.uint8)

split_region = np.ones((img.shape[0], 50, 3), dtype=np.uint8) * 255
combined_result = cv2.hconcat([img, split_region, depth])

cv2.imwrite('low_res_output.jpg', combined_result)