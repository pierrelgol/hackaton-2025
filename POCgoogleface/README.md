# Minimal Face Mesh Capture & Display

Simple pipeline to capture face from webcam, extract MediaPipe landmarks, and display in Three.js.

## Setup

**Note:** MediaPipe works best with Python 3.8-3.12. If you're using Python 3.13, you may need to use Python 3.11 or 3.12 instead.

### 1. Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

If you need a specific Python version:
```bash
python3.11 -m venv venv  # or python3.12
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

### Option 1: Use helper scripts (recommended)
```bash
# Capture face
./run_capture.sh

# View in browser
./run_server.sh
```

### Option 2: Use venv Python directly
```bash
# Capture face
./venv/bin/python capture_and_export.py

# View in browser
./venv/bin/python server.py
```

### Option 3: Fix shell alias (if python points to wrong version)
```bash
# Unalias python temporarily
unalias python

# Then activate venv and run normally
source venv/bin/activate
python capture_and_export.py
```

**Capture instructions:**
- Press **SPACE** to capture when face is detected
- Press **ESC** to exit

**Viewer instructions:**
- Opens http://localhost:8000 automatically
- Drag mouse to rotate the 3D mesh

**macOS Camera Permission:**
If you get "not authorized to capture video", grant camera access:
1. System Settings → Privacy & Security → Camera
2. Enable Terminal (or your terminal app)
3. Restart terminal and try again

## Files

- `capture_and_export.py` - Captures webcam, extracts 468 MediaPipe landmarks, exports JSON + texture
- `index.html` - Three.js viewer that loads and displays the mesh
- `server.py` - Simple HTTP server
- `mesh_data.json` - Output: vertices, UVs, triangle indices
- `texture.jpg` - Output: captured webcam frame

