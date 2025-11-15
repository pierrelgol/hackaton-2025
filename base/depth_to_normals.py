# depth_to_normals.py
import cv2
import numpy as np

DEPTH_NPY = "depth.npy"
NORMALS_NPY = "normals.npy"
NORMALS_PNG = "normals.png"

def main():
    depth = np.load(DEPTH_NPY).astype(np.float32)
    h, w = depth.shape

    # Sobel gradients
    dx = cv2.Sobel(depth, cv2.CV_32F, 1, 0, ksize=3)
    dy = cv2.Sobel(depth, cv2.CV_32F, 0, 1, ksize=3)

    nx = -dx
    ny = -dy
    nz = np.ones_like(depth, dtype=np.float32)

    normals = np.stack([nx, ny, nz], axis=-1)
    norm = np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-8
    normals /= norm

    np.save(NORMALS_NPY, normals)

    normals_01 = (normals + 1.0) * 0.5  # [-1,1] -> [0,1]
    normals_u8 = (normals_01 * 255.0).clip(0, 255).astype(np.uint8)
    cv2.imwrite(NORMALS_PNG, normals_u8)

    print(f"Saved normals to {NORMALS_NPY} and {NORMALS_PNG}")

if __name__ == "__main__":
    main()

