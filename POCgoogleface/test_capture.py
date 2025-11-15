#!/usr/bin/env python3
"""Quick test to verify webcam and MediaPipe are working"""
import cv2
import mediapipe as mp
import sys

print("Testing webcam and MediaPipe...")

# Test webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Could not open webcam")
    print("   - Make sure your webcam is connected")
    print("   - Check if another app is using the webcam")
    sys.exit(1)

print("✓ Webcam opened successfully")

# Test MediaPipe
try:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ MediaPipe loaded successfully")
except Exception as e:
    print(f"❌ ERROR loading MediaPipe: {e}")
    cap.release()
    sys.exit(1)

# Test face detection
print("\nLooking for face... (press ESC to exit)")
face_detected = False

for i in range(300):  # Try for ~10 seconds at 30fps
    ret, frame = cap.read()
    if not ret:
        break
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    if results.multi_face_landmarks:
        face_detected = True
        print(f"✓ Face detected! ({len(results.multi_face_landmarks[0].landmark)} landmarks)")
        break
    
    cv2.putText(frame, "Looking for face...", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Test - Press ESC to exit", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

if face_detected:
    print("\n✅ Everything is working! You can now run: python capture_and_export.py")
else:
    print("\n⚠️  No face detected. Make sure:")
    print("   - You're in a well-lit area")
    print("   - Your face is visible to the camera")
    print("   - You're not too far from the camera")

