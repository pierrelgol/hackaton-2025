#!/usr/bin/env python3
"""
Remove white/light background from raccoon image and make it transparent.
"""
import cv2
import numpy as np
from pathlib import Path

# Try both spellings
IMG_PATH = None
for path in ["raccoon.png", "racoon.png"]:
    if Path(path).exists():
        IMG_PATH = path
        break

if IMG_PATH is None:
    raise SystemExit("Could not find raccoon.png or racoon.png")

OUT_PATH = "raccoon_transparent.png"

def remove_background():
    """Remove white/light background and make transparent"""
    
    # Load image
    img = cv2.imread(IMG_PATH)
    if img is None:
        raise SystemExit(f"Could not read {IMG_PATH}")
    
    print(f"Processing {IMG_PATH} ({img.shape[1]}x{img.shape[0]})")
    
    # Convert to RGBA
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # Convert to grayscale for thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Remove pixels that are too white/bright
    # Adjust threshold (0-255) - higher = more aggressive removal
    threshold = 245  # Pixels brighter than this become transparent
    
    # Create mask: True where we want to keep (not white background)
    brightness_mask = gray < threshold
    
    # Method 2: Also remove very light colors (near-white) using HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    brightness = hsv[:, :, 2]  # Value channel
    saturation = hsv[:, :, 1]   # Saturation channel
    
    # Keep pixels that are either:
    # - Dark enough (brightness < threshold), OR
    # - Have good color saturation (not near-white)
    color_mask = (brightness < threshold) | (saturation > 25)
    
    # Method 3: Remove pixels where all RGB channels are high (white/light)
    b, g, r = cv2.split(img)
    rgb_bright = (r > threshold) & (g > threshold) & (b > threshold)
    rgb_mask = ~rgb_bright  # Invert: keep non-white pixels
    
    # Combine all masks
    final_mask = brightness_mask & color_mask & rgb_mask
    
    # Apply mask to alpha channel
    img_rgba[:, :, 3] = final_mask.astype(np.uint8) * 255
    
    # Optional: Apply slight blur to alpha edge for smoother edges
    alpha = img_rgba[:, :, 3]
    alpha_blurred = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    # Combine with original alpha (preserve hard edges but smooth transitions)
    img_rgba[:, :, 3] = np.maximum(alpha, alpha_blurred * 0.7).astype(np.uint8)
    
    # Save with transparency
    cv2.imwrite(OUT_PATH, img_rgba)
    
    # Count removed pixels
    removed_pixels = np.sum(~final_mask)
    total_pixels = final_mask.size
    removal_percent = (removed_pixels / total_pixels) * 100
    
    print(f"✓ Saved transparent image to {OUT_PATH}")
    print(f"  Background removed: {removal_percent:.1f}% of pixels")
    print(f"  Threshold: {threshold}")
    
    return OUT_PATH

if __name__ == "__main__":
    remove_background()

