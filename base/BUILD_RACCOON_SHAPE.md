# Building Raccoon Shape Mesh

## The Problem

The original `build_racoon_mesh.py` deforms a **face mesh** (468 MediaPipe landmarks arranged as a human face) with depth. This creates a human-shaped mask with raccoon texture, not a raccoon-shaped mask.

## The Solution

`build_raccoon_shape_mesh.py` creates a mesh **directly from the raccoon image**:
- Each pixel (or sampled pixels) becomes a vertex
- Depth values determine the Z coordinate
- Result: A 3D mesh that follows the actual raccoon shape

## Usage

**Option 1: Use the new shape-based mesh (recommended)**
```bash
./venv/bin/python build_raccoon_shape_mesh.py
```

**Option 2: Use the old face-based mesh**
```bash
./venv/bin/python build_racoon_mesh.py
```

## Parameters

In `build_raccoon_shape_mesh.py`:

- **MESH_DENSITY**: Sample every Nth pixel
  - Lower = more vertices (detailed but slower)
  - Higher = fewer vertices (faster but less detailed)
  - Default: 5 (good balance)

- **DEPTH_SCALE**: How much to extrude based on depth
  - Higher = more 3D depth
  - Lower = flatter
  - Default: 0.5

## Result

The new mesh:
- ✅ Follows the actual raccoon image shape
- ✅ Has proper 3D depth from the depth map
- ✅ Maintains raccoon proportions (not human face shape)
- ✅ Can be positioned on your face using rigid transforms

## View the Result

After building, view in 3D:
```bash
# Copy to web
cp raccoon_mask_mesh.json web/

# Start server
./venv/bin/python server.py

# Open viewer
http://localhost:8000/viewer.html
```

