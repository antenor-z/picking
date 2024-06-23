# https://www.youtube.com/watch?v=WbomGeoOT_k

import os, sys
import cv2
from ultralytics import YOLO

if len(sys.argv) == 2 and sys.argv[1] in ["small", "nano", "medium"]:
    mode=sys.argv[1]
else:
    mode="nano"

model = YOLO(f"{os.getcwd()}/weights/best.pt")

cap = cv2.VideoCapture(1)

def predict(frame):
    results = model(frame)

    points = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            avg_x = (x1 + x2) / 2
            avg_y = (y1 + y2) / 2
            object_id = int(box.cls[0])
            object_name = model.names[object_id]
            points.append([int(avg_x), int(avg_y), object_name])
            
    return results, points
    
if __name__ == "__main__":
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        
        results, points = predict(frame)

        frame = results[0].plot()

        print(points)
        
        cv2.imshow(f'TOP CIENCIA DE DADOS I [YOLO {mode}]', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or cv2.getWindowProperty(f"TOP CIENCIA DE DADOS I [YOLO {mode}]", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()
