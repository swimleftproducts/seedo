import torch
from depth_anything_v2.dpt import DepthAnythingV2

encoder = "vits"  # change if using vits/vitb
checkpoint = f"checkpoints/depth_anything_v2_{encoder}.pth"

model_configs = {
    'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
    'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
}

model = DepthAnythingV2(**model_configs[encoder])
model.load_state_dict(torch.load(checkpoint, map_location="cpu"))
model.eval()

dummy = torch.randn(1, 3, 518, 518)  # use your input size
torch.onnx.export(
    model,
    dummy,
    f"depth_anything_{encoder}.onnx",
    input_names=["input"],
    output_names=["depth"],
    opset_version=17,
    do_constant_folding=True
)

print("Exported ONNX → depth_anything.onnx")
