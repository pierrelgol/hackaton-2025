#!/bin/bash
# Complete pipeline runner for raccoon mask

set -e  # Exit on error

# Use venv Python if available
PYTHON_CMD="python"
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="./venv/bin/python"
fi

echo "=== Raccoon Mask Pipeline ==="
echo "Using: $PYTHON_CMD"
echo ""

# Step 1: Generate canonical mesh
echo "Step 1: Generate canonical face mesh"
echo "Look straight at camera with neutral expression, press SPACE to capture"
$PYTHON_CMD generate_canonical_from_face.py

if [ ! -f "canonical_mesh.json" ]; then
    echo "Error: canonical_mesh.json not created"
    exit 1
fi

echo ""
echo "Step 2: Generate depth map from raccoon.png"
$PYTHON_CMD depth_from_image.py

if [ ! -f "depth.npy" ]; then
    echo "Error: depth.npy not created"
    exit 1
fi

echo ""
echo "Step 3: Generate normal map (optional)"
$PYTHON_CMD depth_to_normals.py

echo ""
echo "Step 4: Build raccoon mask mesh (shape-based)"
echo "  This creates a mesh that follows the actual raccoon image shape"
$PYTHON_CMD build_raccoon_shape_mesh.py

if [ ! -f "raccoon_mask_mesh.json" ]; then
    echo "Error: raccoon_mask_mesh.json not created"
    exit 1
fi

echo ""
echo "Step 5: Remove background from raccoon image"
$PYTHON_CMD remove_background.py

echo ""
echo "Step 6: Copy files to web directory"
mkdir -p web
cp raccoon_mask_mesh.json web/

# Copy textures (prefer transparent version)
if [ -f "raccoon_transparent.png" ]; then
    cp raccoon_transparent.png web/
    echo "  Copied transparent texture"
fi

if [ -f "raccoon.png" ]; then
    cp raccoon.png web/
elif [ -f "racoon.png" ]; then
    cp racoon.png web/raccoon.png
    echo "  Copied regular texture as fallback"
fi

echo ""
echo "✓ Pipeline complete!"
echo ""
echo "Now run the web server:"
echo "  cd web && python -m http.server 8000"
echo ""
echo "Or use the existing server:"
echo "  python server.py"
echo ""
echo "Then open: http://localhost:8000"

