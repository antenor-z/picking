import mediapipe as mp
import http.client
import urllib.parse
from tkinter import Tk, simpledialog
from util import open_config
from util import point_inside
import threading
import json
import cv2
import json

SCREEN_NAME = "Auxiliary Side View"
TOP_BORDER_HEIGHT = 0
CONFIG_PATH = "configs/config_2.json"
CAM_NUMBER = 0

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

drawing = False
ix,iy = -1,-1
def draw_rectangle(event, x, y, flags, param):
    global drawing, rect_start, points_of_interest
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        rect_start = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = image.copy()
            cv2.rectangle(img_copy, rect_start, (x, y), (0, 255, 0), 1)
            cv2.imshow(SCREEN_NAME, img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect_end = (x, y)
        cv2.rectangle(image, rect_start, rect_end, (0, 255, 0), 1)
        cv2.imshow(SCREEN_NAME, image)
        threading.Thread(target=get_new_object, args=(rect_start, rect_end)).start()        


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

points_of_interest = open_config(CONFIG_PATH)

def average_point(hand_landmarks):
  acc_cx = []
  acc_cy = []
  for id, lm in enumerate(hand_landmarks.landmark):
      h, w, c = image.shape
      cx, cy = int(lm.x * w), int(lm.y * h)
      acc_cx, acc_cy = acc_cx + [cx], acc_cy + [cy]
  avg_cx = int(sum(acc_cx) / len(acc_cx))
  avg_cy = int(sum(acc_cy) / len(acc_cy))
  return [avg_cx, avg_cy]

def send_inside(box):
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

cap = cv2.VideoCapture(CAM_NUMBER)
cv2.namedWindow(SCREEN_NAME)
cv2.setMouseCallback(SCREEN_NAME, draw_rectangle)

with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

  while cap.isOpened():

    success, image = cap.read()
    if not success:
      print("Ignoring Empty Camera Frame")
      continue

    results = hands.process(image)

    hand_center = []

    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        hand_center = average_point(hand_landmarks)
        cv2.circle(image, hand_center, 2, (255, 0, 0), 20, cv2.FILLED)

    collided = False
    for box in points_of_interest:
      color = (200, 0, 0)
      if hand_center != [] and point_inside(box, hand_center):
        send_inside(box)
        collided = True
        color = (0, 200, 0)
      title_position = (int(box["point_1"][0]), int(box["point_1"][1] - 10))
      text_size, _ = cv2.getTextSize(box["name"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
      text_width, text_height = text_size
      top_left = (title_position[0], title_position[1] - text_height)
      bottom_right = (title_position[0] + text_width, title_position[1] + 5)
      cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
      cv2.putText(image, box["name"], title_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
      cv2.rectangle(image, box["point_1"], box["point_2"], color, 1)

    if not collided:
        location = {}
        location['name'] = 'x'
        send_inside(location)

    if new_object is not None:
        if new_object["name"] is not None and new_object["name"].strip() != "":
            points_of_interest.append(new_object)
            with open(CONFIG_PATH, "w") as fp:
                json.dump(points_of_interest, fp=fp, indent=4)
            print(f"New object {new_object} added.")
        new_object = None

    cv2.imshow(SCREEN_NAME, image)
    
    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        break

cap.release()