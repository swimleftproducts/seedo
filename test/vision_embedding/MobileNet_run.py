# test_embed.py
import torch
import torchvision.models as models
import torch.nn as nn
from PIL import Image
import torchvision.transforms as T
import torch.nn.functional as F


# initialize same architecture
base = models.mobilenet_v3_small()
embedding_model = nn.Sequential(*list(base.children())[:-1])

# load weights locally
embedding_model.load_state_dict(torch.load("test/vision_embedding/mobilenetv3_embed.pt", map_location="cpu"))
embedding_model.eval()

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225])
])

def get_embedding(img: Image.Image):
    inp = transform(img).unsqueeze(0)
    with torch.no_grad():
        emb = embedding_model(inp)
    return emb.flatten()


def similarity(e1, e2):
    return float(F.cosine_similarity(e1, e2, dim=0))


def compare_images():
    from PIL import Image
    
    ref_path = "test/vision_embedding/image/glass_on_table.png"
    no_glass_path = "test/vision_embedding/image/table_no_glass.png"
    diff_table_path = "test/vision_embedding/image/glass_on_table_2.png"

    img_ref = Image.open(ref_path).convert("RGB")
    img_none = Image.open(no_glass_path).convert("RGB")
    img_diff = Image.open(diff_table_path).convert("RGB")

    emb_ref = get_embedding(img_ref)
    emb_none = get_embedding(img_none)
    emb_diff = get_embedding(img_diff)

    print("Similarity(ref vs no_glass):", similarity(emb_ref, emb_none))
    print("Similarity(ref vs glass_diff_table):", similarity(emb_ref, emb_diff))


compare_images()
