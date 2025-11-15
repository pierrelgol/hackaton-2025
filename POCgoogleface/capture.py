import cv2
import json
import mediapipe as mp
from pathlib import Path

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

out_dir = Path("frames")
out_dir.mkdir(exist_ok=True)

cap = cv2.VideoCapture(0)

frame_id = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = mp_face_mesh.process(rgb)

    if res.multi_face_landmarks:
        face = res.multi_face_landmarks[0]

        # Save frame texture
        img_path = out_dir / f"{frame_id}.png"
        cv2.imwrite(str(img_path), frame)

        # Save landmarks
        lm_list = []
        for lm in face.landmark:
            lm_list.append([lm.x, lm.y, lm.z])

        data = {
            "frame": frame_id,
            "landmarks": lm_list
        }

        json_path = out_dir / f"{frame_id}.json"
        json_path.write_text(json.dumps(data))

        frame_id += 1

    cv2.imshow("Live", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

