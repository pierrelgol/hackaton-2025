import json
import numpy as np
from pathlib import Path

# Load MediaPipe canonical mesh (468 points)
# You need a canonical file: canonical_468.json
# Format: { "points": [[x,y,z], ... 468 entries ...] }

CANONICAL = np.array(json.loads(Path("canonical_468.json").read_text())["points"])

def load_landmarks(idx):
    data = json.loads(Path("frames") / f"{idx}.json").read_text()
    obj = json.loads(data)
    return np.array(obj["landmarks"], dtype=np.float32)

def kabsch_align(src, dst):
    """
    src: Nx3 predicted
    dst: Nx3 canonical
    returns aligned points
    """
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)

    src_c = src - src_mean
    dst_c = dst - dst_mean

    H = src_c.T @ dst_c
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Fix reflection
    if np.linalg.det(R) < 0:
        Vt[-1] *= -1
        R = Vt.T @ U.T

    # Scale (uniform)
    src_var = (src_c ** 2).sum()
    scale = (S.sum()) / src_var

    aligned = (scale * (src_c @ R)) + dst_mean
    return aligned

def align_frame(idx):
    raw = load_landmarks(idx)
    aligned = kabsch_align(raw, CANONICAL)
    return aligned

if __name__ == "__main__":
    aligned = align_frame(0)
    print("Aligned shape:", aligned.shape)
    print(aligned[:5])
