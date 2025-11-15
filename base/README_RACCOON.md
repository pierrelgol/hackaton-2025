# Raccoon Mask - Real-time Face Tracking

A minimal pipeline that creates a 3D raccoon mask from an image and tracks it on a face in real-time using MediaPipe FaceMesh and Three.js.

## Overview

1. **Python**: Generate depth map from raccoon image, compute normals, deform canonical face mesh
2. **JavaScript**: Real-time face tracking with MediaPipe, render 3D mask with Three.js

## File Structure

```
/python
    depth_from_image.py          # MiDaS depth estimation
    depth_to_normals.py           # Normal map from depth
    generate_canonical_from_face.py  # Capture canonical face mesh
    build_racoon_mesh.py          # Deform mesh with depth
    canonical_mesh.json           # Generated canonical mesh
    raccoon.png                   # Input image
    depth.npy, depth.png          # Generated depth map
    normals.npy, normals.png      # Generated normals
    raccoon_mask_mesh.json        # Final deformed mesh

/web
    index.html                    # Main HTML page
    main.js                       # Three.js + MediaPipe code
    raccoon_mask_mesh.json        # Copy of deformed mesh
    raccoon.png                   # Copy of texture
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

**Note**: MiDaS requires PyTorch. Install with:
```bash
pip install torch torchvision
```

### 2. Generate Canonical Mesh

First, capture a neutral face to use as the canonical reference:

```bash
python generate_canonical_from_face.py
```

- Look straight at camera with neutral expression
- Press **SPACE** to capture
- This creates `canonical_mesh.json`

### 3. Generate Depth Map

```bash
python depth_from_image.py
```

This uses MiDaS (DPT_Large) to generate `depth.npy` and `depth.png` from `raccoon.png`.

### 4. Generate Normal Map

```bash
python depth_to_normals.py
```

Generates `normals.npy` and `normals.png` from the depth map.

### 5. Build Raccoon Mask Mesh

```bash
python build_racoon_mesh.py
```

Deforms the canonical mesh using the depth map. Outputs `raccoon_mask_mesh.json`.

### 6. Copy Files to Web Directory

```bash
cp raccoon_mask_mesh.json web/
cp raccoon.png web/
```

### 7. Run Web Server

```bash
cd web
python -m http.server 8000
```

Or use the existing server:
```bash
python server.py
```

Open `http://localhost:8000` in your browser.

## How It Works

### Python Pipeline

1. **Canonical Mesh**: 468 MediaPipe face vertices in neutral pose
2. **Depth Estimation**: MiDaS generates depth map from raccoon image
3. **Normal Map**: Sobel gradients compute surface normals
4. **Mesh Deformation**: Sample depth at each vertex UV, displace along vertex normal

### JavaScript Pipeline

1. **MediaPipe FaceMesh**: Real-time 468 landmark detection from webcam
2. **Rigid Transform**: Compute transformation from canonical → current face pose
3. **Mesh Update**: Apply transform to mask geometry each frame
4. **Three.js Rendering**: Render mask with texture overlay

## Tuning

### Displacement Strength

In `build_racoon_mesh.py`, adjust `DISPLACEMENT_STRENGTH`:
- Higher = more 3D depth
- Lower = flatter mask

### Transform Quality

The current implementation uses a simplified transform. For better tracking:
- Use proper SVD for Kabsch algorithm
- Add more key points for alignment
- Implement non-rigid deformation

## Troubleshooting

**MiDaS not working?**
- Ensure PyTorch is installed: `pip install torch torchvision`
- First run will download model (~500MB)

**Mask not tracking?**
- Check browser console for errors
- Ensure camera permissions are granted
- Verify `raccoon_mask_mesh.json` exists in `/web` directory

**Mask looks wrong?**
- Re-capture canonical face with `generate_canonical_from_face.py`
- Adjust `DISPLACEMENT_STRENGTH` in `build_racoon_mesh.py`
- Check that depth map was generated correctly

## Next Steps

- Improve transform algorithm (proper SVD)
- Add non-rigid deformation for better fit
- Support multiple masks
- Add UI controls for adjustment

