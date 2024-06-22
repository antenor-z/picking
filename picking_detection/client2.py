import mediapipe as mp
import json
import cv2
import json
import http.client
import urllib.parse

SCREEN_NAME = "teste 2"
JSON_NAME = "boxes2.json"
CAMERA = 2

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

try:
    with open(JSON_NAME, 'r') as fp:
        points_of_interest = json.load(fp)
except FileNotFoundError:
    with open(JSON_NAME, 'w+') as fp:
        fp.write("[]")
        points_of_interest = []

drawing = False
new_object = None
def draw_rectangle(event, x, y, flags, param):
    global drawing, rect_start, points_of_interest, new_object
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        rect_start = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect_end = (x, y)
        new_object = {
          "name": str(len(points_of_interest) + 1),
          "point_1": [rect_start[0], rect_start[1]], # - TOP_BORDER_HEIGHT], 
          "point_2": [rect_end[0], rect_end[1]] #- TOP_BORDER_HEIGHT]
        }
    if drawing:
      img_copy = image.copy()
      cv2.rectangle(img_copy, rect_start, (x, y), (0, 255, 0), 1)
      cv2.imshow(SCREEN_NAME, img_copy)

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

def is_inside(box, point):
    inside_x = min(box['point_1'][0], box['point_2'][0]) \
      < point[0] < max(box['point_1'][0], box['point_2'][0])
    inside_y = min(box['point_1'][1], box['point_2'][1]) \
      < point[1] < max(box['point_1'][1], box['point_2'][1])
    return inside_x and inside_y

def send_inside(box):
  try:
    params = urllib.parse.urlencode({'camera': str(CAMERA), 'name':str(box['name'])})
    conn = http.client.HTTPConnection("0.0.0.0:8000")
    try:
      conn.request("GET", params)
    except:
      print("Couldn't Get URL")
    response = conn.getresponse()
    print("Status:", response.status)
    print("Response:")
    print(response.read().decode())
    conn.close()
  except http.client.HTTPException as e:
    print("HTTPException:", e)


cap = cv2.VideoCapture(CAMERA)
cv2.namedWindow(SCREEN_NAME)
cv2.setMouseCallback(SCREEN_NAME, draw_rectangle)

with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

  while cap.isOpened():

    success, image = cap.read()
    if not success:
      print("Ignoring Empty Camera Frame")
      continue

    #image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:

      hand_center = []
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
        if is_inside(box, hand_center):
          send_inside(box)
          collided = True
          color = (0, 200, 0)
        cv2.rectangle(image, box['point_1'], box['point_2'], color, 1)

      if not collided:
          a = {}
          if (CAMERA == 0):
            a['name'] = 'x'
          else:
            a['name'] = 'y'
          send_inside(a)

    if new_object is not None:
        points_of_interest.append(new_object)
        with open(JSON_NAME, "w") as fp:
            json.dump(points_of_interest, fp=fp, indent=4)
        new_object = None

    cv2.imshow(SCREEN_NAME, image)
    
    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        break

cap.release()