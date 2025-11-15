import cv2
import json
import numpy as np
import mediapipe as mp
from pathlib import Path

# MediaPipe Face Mesh setup with refined landmarks for eyes/iris
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# refine_landmarks=True gives 478 points (468 face + 10 iris points)
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Enables iris landmarks for detailed eyes
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
    
    # With refine_landmarks, we have 478 points (468 face + 10 iris)
    max_vertices = 478
    for v0 in range(max_vertices):
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

def get_iris_triangles():
    """Get triangle indices for iris (eyes) - MediaPipe provides these"""
    # MediaPipe has specific connections for left and right iris
    left_iris = mp_face_mesh.FACEMESH_LEFT_IRIS
    right_iris = mp_face_mesh.FACEMESH_RIGHT_IRIS
    
    # Extract triangles from iris connections
    iris_triangles = []
    
    def extract_triangles_from_connections(connections, adj_map):
        triangles = []
        visited = set()
        for edge in connections:
            v0, v1 = edge[0], edge[1]
            if v0 in adj_map and v1 in adj_map:
                common = adj_map[v0] & adj_map[v1]
                for v2 in common:
                    tri = tuple(sorted([v0, v1, v2]))
                    if tri not in visited:
                        visited.add(tri)
                        triangles.append([v0, v1, v2])
        return triangles
    
    # Build adjacency for iris
    iris_adj = {}
    for edge in list(left_iris) + list(right_iris):
        v0, v1 = edge[0], edge[1]
        if v0 not in iris_adj:
            iris_adj[v0] = set()
        if v1 not in iris_adj:
            iris_adj[v1] = set()
        iris_adj[v0].add(v1)
        iris_adj[v1].add(v0)
    
    iris_triangles = extract_triangles_from_connections(
        list(left_iris) + list(right_iris), iris_adj
    )
    
    return iris_triangles

# Get triangle indices (cache them)
print("Preparing triangle indices...")
triangle_indices = get_triangle_indices()
iris_triangles = get_iris_triangles()
print(f"Found {len(triangle_indices)} face triangles, {len(iris_triangles)} iris triangles")

# Open webcam with higher resolution if available
cap = cv2.VideoCapture(0)

# Try to set higher resolution for better quality
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit(1)

# Get actual resolution
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Webcam resolution: {actual_width}x{actual_height}")

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
        
        # Extract detected landmarks (478 points with refine_landmarks=True)
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
        # Draw iris landmarks
        mp_drawing.draw_landmarks(
            annotated_frame,
            face_landmarks,
            mp_face_mesh.FACEMESH_LEFT_IRIS,
            None,
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
        )
        mp_drawing.draw_landmarks(
            annotated_frame,
            face_landmarks,
            mp_face_mesh.FACEMESH_RIGHT_IRIS,
            None,
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
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
            
            # Combine all triangles (face + iris)
            all_triangles = triangle_indices + iris_triangles
            
            # Export data with metadata
            export_data = {
                "vertices": vertices.tolist(),
                "uvs": uvs.tolist(),
                "indices": all_triangles,
                "metadata": {
                    "num_vertices": len(vertices),
                    "num_face_triangles": len(triangle_indices),
                    "num_iris_triangles": len(iris_triangles),
                    "total_triangles": len(all_triangles),
                    "texture_width": actual_width,
                    "texture_height": actual_height
                }
            }
            
            # Save JSON
            json_path = Path("mesh_data.json")
            json_path.write_text(json.dumps(export_data, indent=2))
            print(f"✓ Saved mesh data to {json_path}")
            print(f"  - {len(vertices)} vertices (including iris)")
            print(f"  - {len(all_triangles)} total triangles")
            
            # Save texture at high quality
            texture_path = Path("texture.jpg")
            # Use high quality JPEG (95% quality)
            cv2.imwrite(str(texture_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"✓ Saved texture to {texture_path} ({actual_width}x{actual_height})")
            
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
    print("Run: ./run_server.sh or python server.py")
else:
    print("\nNo capture made.")
