# https://docs.ultralytics.com/modes/train/#usage-examples

from ultralytics import YOLO
import os

model = YOLO("yolov8m.pt") # medium
# model = YOLO("yolov8s.pt") # small
# model = YOLO("yolov8n.pt") # nano
results = model.train(data=f"{os.getcwd()}/dataset_v2/data.yaml", 
                      project=f"{os.getcwd()}/output",
                      epochs=100, 
                      imgsz=640)