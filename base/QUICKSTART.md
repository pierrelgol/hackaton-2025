# Quick Start - Raccoon Mask Pipeline

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First run of MiDaS will download ~500MB model.

### 2. Generate Canonical Face Mesh

Capture a neutral face to use as reference:

```bash
python generate_canonical_from_face.py
```

- Look straight at camera, neutral expression
- Press **SPACE** to capture
- Creates `canonical_mesh.json`

### 3. Generate Depth Map

```bash
python depth_from_image.py
```

Generates `depth.npy` and `depth.png` from `raccoon.png`.

### 4. Generate Normal Map (Optional)

```bash
python depth_to_normals.py
```

Generates `normals.npy` and `normals.png`.

### 5. Build Deformed Mesh

```bash
python build_racoon_mesh.py
```

Creates `raccoon_mask_mesh.json` with depth deformation applied.

### 6. Copy to Web Directory

```bash
mkdir -p web
cp raccoon_mask_mesh.json web/
cp raccoon.png web/
```

### 7. Run Web Server

```bash
cd web
python -m http.server 8000
```

Or:
```bash
python server.py
```

### 8. Open in Browser

Navigate to: `http://localhost:8000`

Allow camera access when prompted. The raccoon mask should appear on your face!

## File Checklist

**Python files:**
- ✅ `generate_canonical_from_face.py` - Capture canonical mesh
- ✅ `depth_from_image.py` - MiDaS depth estimation
- ✅ `depth_to_normals.py` - Normal map generation
- ✅ `build_racoon_mesh.py` - Mesh deformation

**Generated files:**
- ✅ `canonical_mesh.json` - Reference face mesh
- ✅ `depth.npy`, `depth.png` - Depth map
- ✅ `normals.npy`, `normals.png` - Normal map (optional)
- ✅ `raccoon_mask_mesh.json` - Final deformed mesh

**Web files:**
- ✅ `web/index.html` - Main page
- ✅ `web/main.js` - Three.js + MediaPipe code
- ✅ `web/raccoon_mask_mesh.json` - Copy of mesh
- ✅ `web/raccoon.png` - Copy of texture

## Troubleshooting

**"Canonical mesh not found"**
→ Run `generate_canonical_from_face.py` first

**"Depth map not found"**
→ Run `depth_from_image.py` first

**Mask not appearing in browser**
→ Check browser console for errors
→ Verify files are in `/web` directory
→ Check camera permissions

**Mask not tracking face**
→ Ensure good lighting
→ Face camera directly
→ Check MediaPipe is loading (check console)

## Adjusting Mask Appearance

**Displacement strength** (in `build_racoon_mesh.py`):
```python
DISPLACEMENT_STRENGTH = 0.1  # Increase for more 3D depth
```

**Mask scale** (in `web/main.js`):
```javascript
const scale = 0.4;  // Adjust to match your face size
```

