import json
from pathlib import Path
import cv2

def load_frame(idx):
    json_path = Path("frames") / f"{idx}.json"
    img_path = Path("frames") / f"{idx}.png"

    data = json.loads(json_path.read_text())
    img = cv2.imread(str(img_path))

    return data["landmarks"], img

if __name__ == "__main__":
    landmarks, texture = load_frame(0)
    print("Landmarks:", len(landmarks))
    print("Texture shape:", texture.shape)

