import torch
from depth_anything_v2.dpt import DepthAnythingV2

encoder = "vits"  # change if using vits/vitb
checkpoint = f"test/ml_depth_map/Depth-Anything-V2/checkpoints/depth_anything_v2_{encoder}.pth"

model_configs = {
    'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
    'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
}

model = DepthAnythingV2(**model_configs[encoder])
model.load_state_dict(torch.load(checkpoint, map_location="cpu"))
model.eval()

dummy = torch.randn(1, 3, 518, 518)  # use your input size
fp16=''

#convert to fp16 if wanted
# model.half()
# dummy = torch.randn(1, 3, 518, 518).half()  # use your input size
# fp16 ='_fp16'

torch.onnx.export(
    model,
    dummy,
    f"depth_anything_{encoder}{fp16}.onnx",
    input_names=["input"],
    output_names=["depth"],
    opset_version=18,
    do_constant_folding=True,
    dynamic_axes={
        "input": {2: "height", 3: "width"},
        "depth": {1: "height", 2: "width"}
    }
)

print(f"Exported ONNX {fp16} → depth_anything.onnx")
