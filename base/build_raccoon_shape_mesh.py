#!/usr/bin/env python3
"""
Build a 3D mesh directly from the raccoon image and depth map.
Creates a mesh that follows the actual raccoon shape, not the face mesh.
"""
import cv2
import json
import numpy as np
from pathlib import Path

IMG_PATH = None
for path in ["Raccoon-cartoon.png", "raccoon.png", "racoon.png", "raccoon_transparent.png"]:
    if Path(path).exists():
        IMG_PATH = path
        break

if IMG_PATH is None:
    raise SystemExit("Could not find raccoon image")

DEPTH_NPY = "depth.npy"
OUT_MESH_JSON = "raccoon_mask_mesh.json"

# Mesh density - lower = more vertices (slower but more detailed)
# Higher = fewer vertices (faster but less detailed)
MESH_DENSITY = 5  # Sample every Nth pixel (5 = good balance for performance)

# Depth scaling - how much to extrude based on depth
DEPTH_SCALE = 0.5  # Adjust to make 3D effect more/less pronounced

def create_mesh_from_depth():
    """Create a 3D mesh directly from the image and depth map"""
    
    # Load image
    img = cv2.imread(IMG_PATH)
    if img is None:
        raise SystemExit(f"Could not read {IMG_PATH}")
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    # Load depth map
    if not Path(DEPTH_NPY).exists():
        raise SystemExit(f"{DEPTH_NPY} not found. Run depth_from_image.py first.")
    
    depth = np.load(DEPTH_NPY).astype(np.float32)
    depth_h, depth_w = depth.shape
    
    # Resize depth to match image if needed
    if depth_h != h or depth_w != w:
        depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_LINEAR)
    
    print(f"Image size: {w}x{h}")
    print(f"Creating mesh with density {MESH_DENSITY} (every {MESH_DENSITY} pixels)")
    
    # Create grid of vertices
    vertices = []
    uvs = []
    faces = []
    
    # Sample grid points
    step = MESH_DENSITY
    grid_h = (h // step) + 1
    grid_w = (w // step) + 1
    
    # Create vertex grid
    vertex_grid = {}
    vertex_idx = 0
    
    for y in range(0, h, step):
        for x in range(0, w, step):
            # Clamp to image bounds
            x_clamped = min(x, w - 1)
            y_clamped = min(y, h - 1)
            
            # Get depth value
            depth_val = depth[y_clamped, x_clamped]
            
            # Normalize coordinates to [-1, 1] range (centered)
            # X: left to right -> -1 to 1
            # Y: top to bottom -> 1 to -1 (flip for 3D)
            # Z: depth from image
            x_norm = (x_clamped / w - 0.5) * 2.0
            y_norm = (0.5 - y_clamped / h) * 2.0  # Flip Y
            z_norm = (depth_val - 0.5) * DEPTH_SCALE  # Center depth and scale
            
            vertices.append([float(x_norm), float(y_norm), float(z_norm)])
            
            # UV coordinates (normalized 0-1)
            uvs.append([float(x_clamped / w), float(y_clamped / h)])
            
            # Store grid position for face creation
            grid_y = y // step
            grid_x = x // step
            vertex_grid[(grid_y, grid_x)] = vertex_idx
            vertex_idx += 1
    
    print(f"Created {len(vertices)} vertices")
    
    # Create faces (triangles) from grid
    for y in range(grid_h - 1):
        for x in range(grid_w - 1):
            # Get 4 corner vertices of this quad
            v00 = vertex_grid.get((y, x))
            v01 = vertex_grid.get((y, x + 1))
            v10 = vertex_grid.get((y + 1, x))
            v11 = vertex_grid.get((y + 1, x + 1))
            
            # Skip if any vertex is missing
            if None in [v00, v01, v10, v11]:
                continue
            
            # Create two triangles per quad
            # Triangle 1: v00, v10, v01
            faces.append([v00, v10, v01])
            # Triangle 2: v01, v10, v11
            faces.append([v01, v10, v11])
    
    print(f"Created {len(faces)} faces")
    
    # Export mesh
    mesh_data = {
        "vertices": vertices,
        "uv": uvs,
        "faces": faces
    }
    
    with open(OUT_MESH_JSON, "w") as f:
        json.dump(mesh_data, f, indent=2)
    
    print(f"\n✓ Saved raccoon shape mesh to {OUT_MESH_JSON}")
    print(f"  - {len(vertices)} vertices")
    print(f"  - {len(faces)} faces")
    print(f"  - Mesh follows actual raccoon image shape")
    
    return mesh_data

if __name__ == "__main__":
    create_mesh_from_depth()

