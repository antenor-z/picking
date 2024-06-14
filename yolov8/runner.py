# https://www.youtube.com/watch?v=WbomGeoOT_k

import os, sys
import cv2
from ultralytics import YOLO

if len(sys.argv) == 2 and sys.argv[1] in ["small", "nano", "medium"]:
    mode=sys.argv[1]
else:
    mode="nano"

model = YOLO(f"{os.getcwd()}/output/train_{mode}/weights/best.pt")

cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break
    
    results = model(frame)
    
    frame = results[0].plot()
    
    cv2.imshow(f'TOP CIENCIA DE DADOS I [YOLO {mode}]', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or cv2.getWindowProperty(f"TOP CIENCIA DE DADOS I [YOLO {mode}]", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
