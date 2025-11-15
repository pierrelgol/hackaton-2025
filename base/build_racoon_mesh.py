# build_raccoon_mesh.py
import json
import numpy as np
from pathlib import Path

CANONICAL_MESH_JSON = "canonical_mesh.json"
DEPTH_NPY = "depth.npy"
OUT_MESH_JSON = "raccoon_mask_mesh.json"

# tweak this to control how "thick" / "3D" the mask becomes
DISPLACEMENT_STRENGTH = 0.3  # Increased for more pronounced 3D raccoon shape

def main():
    if not Path(CANONICAL_MESH_JSON).exists():
        print(f"Error: {CANONICAL_MESH_JSON} not found. Run generate_canonical_mesh.py first.")
        return
    
    if not Path(DEPTH_NPY).exists():
        print(f"Error: {DEPTH_NPY} not found. Run depth_from_image.py first.")
        return
    
    with open(CANONICAL_MESH_JSON, "r") as f:
        mesh = json.load(f)

    verts = np.asarray(mesh["vertices"], dtype=np.float32)  # (N, 3)
    uvs = np.asarray(mesh["uv"], dtype=np.float32)          # (N, 2)
    faces = np.asarray(mesh["faces"], dtype=np.int32)       # (M, 3)

    depth = np.load(DEPTH_NPY).astype(np.float32)
    h, w = depth.shape

    # sample depth at each vertex using its UV
    u = uvs[:, 0] * (w - 1)
    v = (1.0 - uvs[:, 1]) * (h - 1)  # flip V if needed
    u = np.clip(u, 0, w - 1)
    v = np.clip(v, 0, h - 1)

    depth_samples = depth[v.astype(int), u.astype(int)]

    # center & scale depth
    depth_centered = depth_samples - depth_samples.mean()
    displacement_amount = depth_centered * DISPLACEMENT_STRENGTH  # (N,)

    # simple direction: push along vertex direction from origin
    directions = verts / (np.linalg.norm(verts, axis=1, keepdims=True) + 1e-8)
    displacement = displacement_amount[:, None] * directions  # (N, 3)

    deformed_verts = verts + displacement

    out = {
        "vertices": deformed_verts.tolist(),
        "uv": mesh["uv"],
        "faces": mesh["faces"]
    }

    with open(OUT_MESH_JSON, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Saved raccoon mask mesh to {OUT_MESH_JSON}")
    print(f"  - {len(deformed_verts)} vertices")
    print(f"  - {len(faces)} faces")

if __name__ == "__main__":
    main()

