#!/usr/bin/env python3
"""
Generate canonical_mesh.json from MediaPipe Face Mesh structure.
This creates a reference mesh with 468 vertices, UVs, and face indices.
"""
import json
import numpy as np
import mediapipe as mp

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
                    tri = tuple(sorted([v0, v1, v2]))
                    if tri not in visited_triangles:
                        visited_triangles.add(tri)
                        triangles.append([v0, v1, v2])
    
    return triangles

def generate_canonical_vertices():
    """
    Generate canonical vertices for MediaPipe face mesh.
    These are normalized coordinates representing a standard face pose.
    MediaPipe landmarks are in normalized image space [0,1] for x,y and relative z.
    """
    # Create a simple canonical face shape
    # This is a simplified approach - in production you'd use MediaPipe's actual canonical mesh
    vertices = []
    
    # For now, we'll create a basic face shape that MediaPipe can align to
    # The actual vertices will be replaced by MediaPipe landmarks during tracking
    # This is just a placeholder structure
    
    # Generate 468 vertices in a basic face-like distribution
    for i in range(468):
        # Simple normalized coordinates (will be replaced by actual face tracking)
        x = 0.5 + (np.random.random() - 0.5) * 0.3
        y = 0.5 + (np.random.random() - 0.5) * 0.3
        z = (np.random.random() - 0.5) * 0.1
        vertices.append([float(x), float(y), float(z)])
    
    return vertices

def generate_canonical_uvs():
    """Generate UV coordinates for 468 vertices"""
    uvs = []
    for i in range(468):
        # MediaPipe landmarks x,y are already in [0,1] range
        # We'll use them as UV coordinates
        x = 0.5 + (np.random.random() - 0.5) * 0.3
        y = 0.5 + (np.random.random() - 0.5) * 0.3
        uvs.append([float(x), float(y)])
    return uvs

def main():
    print("Generating canonical mesh...")
    
    triangles = get_triangle_indices()
    print(f"Found {len(triangles)} triangles")
    
    # For canonical mesh, we need actual MediaPipe canonical coordinates
    # Since MediaPipe doesn't expose them directly, we'll create a reference mesh
    # that will be deformed by the depth map
    
    # Note: In practice, you'd capture a neutral face and use that as canonical
    # For this pipeline, we'll use a simple normalized face shape
    vertices = generate_canonical_vertices()
    uvs = generate_canonical_uvs()
    
    canonical_mesh = {
        "vertices": vertices,
        "uv": uvs,
        "faces": triangles
    }
    
    with open("canonical_mesh.json", "w") as f:
        json.dump(canonical_mesh, f, indent=2)
    
    print(f"Saved canonical_mesh.json with {len(vertices)} vertices and {len(triangles)} faces")

if __name__ == "__main__":
    main()

