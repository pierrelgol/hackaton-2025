# depth_from_image.py
import cv2
import torch
import numpy as np
from pathlib import Path

# Try different raccoon image names
IMG_PATH = None
for path in ["Raccoon-cartoon.png", "raccoon.png", "racoon.png", "raccoon_transparent.png"]:
    if Path(path).exists():
        IMG_PATH = path
        break

if IMG_PATH is None:
    raise SystemExit("Could not find raccoon image in current directory")

DEPTH_NPY = "depth.npy"
DEPTH_PNG = "depth.png"

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Loading MiDaS model (this may take a moment on first run)...")
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Large", trust_repo=True)
    midas.to(device)
    midas.eval()

    transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
    transform = transforms.dpt_transform

    print(f"Reading image: {IMG_PATH}")
    img_bgr = cv2.imread(IMG_PATH)
    if img_bgr is None:
        raise SystemExit(f"Could not read {IMG_PATH}")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze(0).squeeze(0)

    depth = prediction.cpu().numpy().astype(np.float32)

    # normalize to [0, 1]
    depth -= depth.min()
    if depth.max() > 0:
        depth /= depth.max()

    np.save(DEPTH_NPY, depth)
    depth_u8 = (depth * 255.0).clip(0, 255).astype(np.uint8)
    cv2.imwrite(DEPTH_PNG, depth_u8)

    print(f"✓ Saved depth map to {DEPTH_NPY} and {DEPTH_PNG}")
    print(f"  Depth range: {depth.min():.3f} to {depth.max():.3f}")

if __name__ == "__main__":
    main()
