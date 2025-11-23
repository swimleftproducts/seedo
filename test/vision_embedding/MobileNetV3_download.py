# save_mobilenet_embed.py
import torch
import torchvision.models as models
import torch.nn as nn

print("Loading MobileNetV3-small pretrained...")
model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)

# remove classifier head
embedding_model = nn.Sequential(*list(model.children())[:-1])
embedding_model.eval()

# save local model
torch.save(embedding_model.state_dict(), "test/vision_embedding/mobilenetv3_embed.pt")
print("Saved local embedding model to test/vision_embedding/mobilenetv3_embed.pt")

# ONNX export needs a dummy input with correct tensor size
dummy_input = torch.randn(1, 3, 224, 224)

# export embedding model (not full classifier)
torch.onnx.export(
    embedding_model,
    dummy_input,
    "test/vision_embedding/mobilenetv3_embed_batch.onnx",
    export_params=True,
    opset_version=18,
    input_names=["input"],
    output_names=["embedding"],
    dynamic_axes={
        "input": {0: "batch_size"},      
        "embedding": {0: "batch_size"}   
    }
)

print("Saved ONNX model to test/vision_embedding/mobilenetv3_embed_batch.onnx")