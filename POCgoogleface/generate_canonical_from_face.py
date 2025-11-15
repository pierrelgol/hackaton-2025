#!/usr/bin/env python3
"""
Generate canonical_mesh.json from a captured neutral face.
This creates the reference mesh that will be deformed by the depth map.
"""
import cv2
import json
import numpy as np
import mediapipe as mp
from pathlib import Path

mp_face_mesh = mp.solutions.face_mesh

def get_triangle_indices():
    """Extract triangle indices from MediaPipe face mesh connections"""
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
    
    # Find triangles
    triangles = []
    visited_triangles = set()
    
    for v0 in range(468):
        if v0 not in adj:
            continue
        neighbors = list(adj[v0])
        for i, v1 in enumerate(neighbors):
            for v2 in neighbors[i+1:]:
                if v2 in adj[v1]:
                    tri = tuple(sorted([v0, v1, v2]))
                    if tri not in visited_triangles:
                        visited_triangles.add(tri)
                        triangles.append([v0, v1, v2])
    
    return triangles

def capture_canonical_face():
    """
    Capture a neutral face to use as canonical reference.
    User should look straight at camera with neutral expression.
    """
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=False,  # Use 468 points
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    print("\nLook straight at the camera with a neutral expression.")
    print("Press SPACE to capture canonical face, ESC to exit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Draw landmarks
            annotated = frame.copy()
            mp.solutions.drawing_utils.draw_landmarks(
                annotated,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                None,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )
            cv2.imshow("Canonical Face Capture - Press SPACE", annotated)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                # Extract landmarks
                vertices = []
                uvs = []
                
                for lm in face_landmarks.landmark:
                    # MediaPipe landmarks are in normalized image space
                    vertices.append([lm.x, lm.y, lm.z])
                    # UVs are the same as x,y (normalized)
                    uvs.append([lm.x, lm.y])
                
                triangles = get_triangle_indices()
                
                canonical_mesh = {
                    "vertices": vertices,
                    "uv": uvs,
                    "faces": triangles
                }
                
                with open("canonical_mesh.json", "w") as f:
                    json.dump(canonical_mesh, f, indent=2)
                
                print(f"\n✓ Saved canonical_mesh.json")
                print(f"  - {len(vertices)} vertices")
                print(f"  - {len(triangles)} faces")
                
                cap.release()
                cv2.destroyAllWindows()
                return True
            
            if key == 27:  # ESC
                break
        else:
            cv2.imshow("Canonical Face Capture - Press SPACE", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
    
    cap.release()
    cv2.destroyAllWindows()
    return False

if __name__ == "__main__":
    if capture_canonical_face():
        print("\nCanonical mesh generated! Now run:")
        print("  1. python depth_from_image.py")
        print("  2. python depth_to_normals.py")
        print("  3. python build_racoon_mesh.py")
    else:
        print("\nNo face captured.")

