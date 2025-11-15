# How to Run the Raccoon Mask Pipeline

## Quick Start (Automated)

Run the complete pipeline:

```bash
./run_pipeline.sh
```

This will:
1. Capture canonical face (you'll need to press SPACE)
2. Generate depth map
3. Generate normal map
4. Build deformed mesh
5. Copy files to web directory

Then start the server:
```bash
python server.py
```

Open `http://localhost:8000` in your browser.

---

## Manual Step-by-Step

### Step 1: Generate Canonical Face Mesh

```bash
python generate_canonical_from_face.py
```

- Look straight at camera with neutral expression
- Press **SPACE** when ready
- Creates `canonical_mesh.json`

### Step 2: Generate Depth Map

```bash
python depth_from_image.py
```

- Uses MiDaS (DPT_Large) to estimate depth
- Requires `raccoon.png` in current directory
- Creates `depth.npy` and `depth.png`
- **First run downloads ~500MB model**

### Step 3: Generate Normal Map (Optional)

```bash
python depth_to_normals.py
```

- Computes surface normals from depth
- Creates `normals.npy` and `normals.png`

### Step 4: Build Raccoon Mask Mesh

```bash
python build_racoon_mesh.py
```

- Deforms canonical mesh using depth map
- Creates `raccoon_mask_mesh.json`

### Step 5: Copy Files to Web Directory

```bash
mkdir -p web
cp raccoon_mask_mesh.json web/
cp raccoon.png web/
```

### Step 6: Start Web Server

**Option A: Use existing server**
```bash
python server.py
```

**Option B: Python HTTP server**
```bash
cd web
python -m http.server 8000
```

### Step 7: Open in Browser

Navigate to: `http://localhost:8000`

- Allow camera access when prompted
- The raccoon mask should appear on your face!

---

## Using Virtual Environment

If using venv:

```bash
# Activate venv
source venv/bin/activate

# Or use venv Python directly
./venv/bin/python generate_canonical_from_face.py
./venv/bin/python depth_from_image.py
./venv/bin/python build_racoon_mesh.py
```

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'torch'"**
```bash
pip install torch torchvision
```

**"raccoon.png not found"**
- Make sure `raccoon.png` is in the project root
- Or update `IMG_PATH` in `depth_from_image.py`

**"Canonical mesh not found"**
- Run `generate_canonical_from_face.py` first

**"Camera not working in browser"**
- Check browser permissions
- Try a different browser
- Check if another app is using the camera

**"Mask not tracking"**
- Ensure good lighting
- Face camera directly
- Check browser console for errors

---

## File Checklist

Before running web server, verify:

```
web/
  ├── index.html          ✅ (should exist)
  ├── main.js            ✅ (should exist)
  ├── raccoon_mask_mesh.json  ✅ (copy from root)
  └── raccoon.png        ✅ (copy from root)
```

---

## Quick Commands Reference

```bash
# Full pipeline
./run_pipeline.sh

# Individual steps
python generate_canonical_from_face.py
python depth_from_image.py
python depth_to_normals.py
python build_racoon_mesh.py

# Copy to web
cp raccoon_mask_mesh.json web/ && cp raccoon.png web/

# Start server
python server.py
```

