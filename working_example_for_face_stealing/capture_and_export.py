import cv2
import json
import numpy as np
import mediapipe as mp
from pathlib import Path

# MediaPipe Face Mesh setup
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def get_triangle_indices():
    """Extract triangle indices from MediaPipe face mesh connections"""
    # MediaPipe FACEMESH_TESSELATION provides edges
    # We need to reconstruct triangles from these edges
    connections = mp_face_mesh.FACEMESH_TESSELATION
    
    # Build adjacency list
    adj = {}
    for edge in connections:
        v0, v1 = edge[0], edge[1]
        if v0 not in adj:
            adj[v0] = set()
        if v1 not in adj:
            adj[v1] = set()
        adj[v0].add(v1)
        adj[v1].add(v0)
    
    # Find triangles: for each edge (v0, v1), find common neighbors
    triangles = []
    visited_triangles = set()
    
    for v0 in range(468):  # MediaPipe has 468 landmarks
        if v0 not in adj:
            continue
        neighbors = list(adj[v0])
        for i, v1 in enumerate(neighbors):
            for v2 in neighbors[i+1:]:
                if v2 in adj[v1]:  # v0-v1-v2 forms a triangle
                    # Sort to avoid duplicates
                    tri = tuple(sorted([v0, v1, v2]))
                    if tri not in visited_triangles:
                        visited_triangles.add(tri)
                        triangles.append([v0, v1, v2])
    
    return triangles

def kabsch_align(src, dst):
    """Align source points to destination using Kabsch algorithm"""
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    
    src_centered = src - src_mean
    dst_centered = dst - dst_mean
    
    H = src_centered.T @ dst_centered
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    
    # Fix reflection
    if np.linalg.det(R) < 0:
        Vt[-1] *= -1
        R = Vt.T @ U.T
    
    # Scale
    src_var = (src_centered ** 2).sum()
    if src_var > 0:
        scale = S.sum() / src_var
    else:
        scale = 1.0
    
    aligned = (scale * (src_centered @ R)) + dst_mean
    return aligned

# Get triangle indices (cache them)
print("Preparing triangle indices...")
triangle_indices = get_triangle_indices()
print(f"Found {len(triangle_indices)} triangles")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit(1)

print("\nPress SPACE to capture, ESC to exit")

captured = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extract detected landmarks (468 points)
        detected_landmarks = []
        for lm in face_landmarks.landmark:
            detected_landmarks.append([lm.x, lm.y, lm.z])
        
        detected_landmarks = np.array(detected_landmarks, dtype=np.float32)
        
        # Draw landmarks on frame
        annotated_frame = frame.copy()
        mp_drawing.draw_landmarks(
            annotated_frame,
            face_landmarks,
            mp_face_mesh.FACEMESH_TESSELATION,
            None,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
        )
        cv2.imshow("Face Mesh - Press SPACE to capture", annotated_frame)
        
        # Capture on SPACE key
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            print("\nCapturing frame...")
            
            # For minimal setup: use detected landmarks as vertices
            # MediaPipe landmarks are already in a normalized coordinate system
            # We'll align them to a canonical orientation (centered, normalized)
            
            # Create canonical reference: center and normalize
            vertices = detected_landmarks.copy()
            
            # Center the face
            vertices[:, :2] = vertices[:, :2] - vertices[:, :2].mean(axis=0)
            
            # Normalize scale (keep aspect ratio)
            scale = np.abs(vertices[:, :2]).max()
            if scale > 0:
                vertices[:, :2] = vertices[:, :2] / scale
            
            # Keep z-depth as is (relative depth)
            
            # UV coordinates: use normalized x,y from original landmarks
            # MediaPipe landmarks x,y are in [0,1] range (image coordinates)
            # Flip y for texture mapping (image y is top-to-bottom, UV y is bottom-to-top)
            uvs = detected_landmarks[:, :2].copy()
            uvs[:, 1] = 1.0 - uvs[:, 1]  # Flip Y for UV
            
            # Export data
            export_data = {
                "vertices": vertices.tolist(),
                "uvs": uvs.tolist(),
                "indices": triangle_indices
            }
            
            # Save JSON
            json_path = Path("mesh_data.json")
            json_path.write_text(json.dumps(export_data, indent=2))
            print(f"✓ Saved mesh data to {json_path} ({len(vertices)} vertices, {len(triangle_indices)} triangles)")
            
            # Save texture
            texture_path = Path("texture.jpg")
            cv2.imwrite(str(texture_path), frame)
            print(f"✓ Saved texture to {texture_path}")
            
            captured = True
            break
        
        if key == 27:  # ESC
            break
    else:
        cv2.imshow("Face Mesh - Press SPACE to capture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()

if captured:
    print("\n✓ Capture complete!")
    print("Run: python server.py")
    print("Then open: http://localhost:8000")
else:
    print("\nNo capture made.")
