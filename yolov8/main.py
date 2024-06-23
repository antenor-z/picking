import mediapipe as mp
import http.client
import urllib.parse
from tkinter import Tk, simpledialog
from util import open_config
from util import point_inside
from predictor import predict
import threading
import json
import cv2
import json

TOP_BORDER_HEIGHT = 80
CONFIG_PATH = "configs/config_1.json"
CAM_NUMBER = 2

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

new_object = None
def get_new_object(rect_start, rect_end):
    global new_object
    root = Tk()
    root.withdraw()
    new_object_name = simpledialog.askstring("Novo objeto", "Escolha um nome:")
    root.destroy()
    new_object = {
        "name": new_object_name,
        "point_1": [rect_start[0], rect_start[1] - TOP_BORDER_HEIGHT], 
        "point_2": [rect_end[0], rect_end[1] - TOP_BORDER_HEIGHT]
    }

points_of_interest = open_config(CONFIG_PATH)

drawing = False
ix,iy = -1,-1
def draw_rectangle(event, x, y, flags, param):
    global drawing, rect_start, points_of_interest
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        rect_start = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, rect_start, (x, y), (0, 255, 0), 1)
            cv2.imshow("TOP CIENCIA DE DADOS I", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect_end = (x, y)
        cv2.rectangle(img, rect_start, rect_end, (0, 255, 0), 1)
        cv2.imshow("TOP CIENCIA DE DADOS I", img)
        threading.Thread(target=get_new_object, args=(rect_start, rect_end)).start()        

def send_hand_inside(box):
  try:
    params = urllib.parse.urlencode({'camera': str(CAM_NUMBER), 'box':str(box['name'])})
    conn = http.client.HTTPConnection("0.0.0.0:8000")
    try:
      conn.request("GET", params)
      response = conn.getresponse()
    except:
      print("Couldn't Get URL")
    else: 
      print("Status:", response.status)
      print("Response:")
      print(response.read().decode())
      conn.close()
  except http.client.HTTPException as e:
    print("HTTPException:", e)

def average_hand_point(hand_landmarks):
  acc_cx = []
  acc_cy = []
  for id, lm in enumerate(hand_landmarks.landmark):
      h, w, c = img.shape
      cx, cy = int(lm.x * w), int(lm.y * h)
      acc_cx, acc_cy = acc_cx + [cx], acc_cy + [cy]
  avg_cx = int(sum(acc_cx) / len(acc_cx))
  avg_cy = int(sum(acc_cy) / len(acc_cy))
  return [avg_cx, avg_cy]

cap = cv2.VideoCapture(CAM_NUMBER)

cv2.namedWindow("TOP CIENCIA DE DADOS I")
cv2.setMouseCallback("TOP CIENCIA DE DADOS I", draw_rectangle)

with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

  while cap.isOpened():

    success, img = cap.read()
    if not success:
      print("Ignoring Empty Camera Frame")
      continue

    results = hands.process(img)
    
    hand_center = []

    # MEDIAPIPE Draw hand midpoint
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            hand_center = average_hand_point(hand_landmarks)
            cv2.circle(img, hand_center, 2, (255, 0, 0), 20, cv2.FILLED)

    objs_positions = []
    matches = []
    wrong = []
    
    _, objs_positions = predict(img)

    # Draw indications of found objects
    for [avg_x, avg_y, obj_name] in objs_positions:
        text_size, _ = cv2.getTextSize(obj_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_width, text_height = text_size
        
        top_left = (avg_x - 30, avg_y - text_height)
        bottom_right = (avg_x - 30 + text_width, avg_y + 5)
        
        cv2.rectangle(img, top_left, bottom_right, (255, 255, 255), cv2.FILLED)
        cv2.putText(img, obj_name, (avg_x - 30, avg_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    collided = False
    for location in points_of_interest:
        color = (200, 0, 0)
        for obj_position in objs_positions:
            if point_inside(location, obj_position):
                if location["name"] == obj_position[2]:  # if object is in the right box
                    matches.append(location["name"])
                    color = (0, 200, 0)
                else:  # if object is in the wrong box
                    wrong.append(location["name"])
                    color = (0, 0, 200)
                if hand_center != [] and point_inside(location, hand_center):
                    if location["name"] in old_matches:
                        send_hand_inside(location)
                        color = (0, 200, 200)
                        collided = True
        title_position = (int(location["point_1"][0]), int(location["point_1"][1] - 10))
        text_size, _ = cv2.getTextSize(location["name"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_width, text_height = text_size
        top_left = (title_position[0], title_position[1] - text_height)
        bottom_right = (title_position[0] + text_width, title_position[1] + 5)
        cv2.rectangle(img, top_left, bottom_right, color, cv2.FILLED)
        cv2.putText(img, location["name"], title_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.rectangle(img, location["point_1"], location["point_2"], color, 1)
    
    old_matches = matches

    if not collided:
      location = {}
      location['name'] = 'x'
      send_hand_inside(location)

    # Draw information about object in right and wrong boxes
    img = cv2.copyMakeBorder(img, TOP_BORDER_HEIGHT, 0, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    cv2.putText(img, "Correto: " + " ".join(matches), (10, 45), cv2.QT_FONT_NORMAL, 0.7, (0, 255, 0), 1)
    cv2.putText(img, "Errado: " + " ".join(wrong), (10, 70), cv2.QT_FONT_NORMAL, 0.7, (0, 0, 255), 1)

    cv2.putText(img, "Use o mouse para desenhar um retangulo em volta do objeto", (10, 15), cv2.QT_FONT_NORMAL, 0.5, (100, 100, 100), 1)

    cv2.imshow("TOP CIENCIA DE DADOS I", img)

    if new_object is not None:
        if new_object["name"] is not None and new_object["name"].strip() != "":
            points_of_interest.append(new_object)
            with open(CONFIG_PATH, "w") as fp:
                json.dump(points_of_interest, fp=fp, indent=4)
            print(f"New object {new_object} added.")
        new_object = None

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or cv2.getWindowProperty("TOP CIENCIA DE DADOS I", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
