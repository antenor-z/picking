import mediapipe as mp
import json
import cv2
import json

TOP_BORDER_HEIGHT = 80
CONFIG_PATH = "utils/config.json"

def mid_point(acc_cx, acc_cy):
    avg_cx = int(sum(acc_cx) / len(acc_cx))
    avg_cy = int(sum(acc_cy) / len(acc_cy))
    return [avg_cx, avg_cy]

with open(CONFIG_PATH) as fp:
    points_of_interest = list(json.load(fp))

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
        name = input("nome do objeto (deixe em branco para cancelar): ")
        if name.strip() != "":
            new_rect = {
                "name": name,
                "point_1": [rect_start[0], rect_start[1] - TOP_BORDER_HEIGHT], 
                "point_2": [rect_end[0], rect_end[1] - TOP_BORDER_HEIGHT]
            }
            points_of_interest.append(new_rect)
            with open(CONFIG_PATH, "w") as fp:
                json.dump(points_of_interest, fp=fp, indent=4)
            print("OK")

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cv2.namedWindow("TOP CIENCIA DE DADOS I")
cv2.setMouseCallback("TOP CIENCIA DE DADOS I", draw_rectangle)

while True:
    hands_positions = []
    matches = []

    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        hands_positions = []  # reset list
        for handLms in results.multi_hand_landmarks:
            acc_cx = []
            acc_cy = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                acc_cx, acc_cy = acc_cx + [cx], acc_cy + [cy]

            (avg_cx, avg_cy) = mid_point(acc_cx, acc_cy)
            cv2.circle(img, (avg_cx, avg_cy), 2, (255, 0, 0), 20, cv2.FILLED)
            hands_positions.append([avg_cx, avg_cy])
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    for location in points_of_interest:
        color = (200, 0, 0)
        for hand_position in hands_positions:
            if location["point_1"][0] < hand_position[0] < location["point_2"][0] and \
                location["point_1"][1] < hand_position[1] < location["point_2"][1]:
                matches.append(location["name"])
                color = (0, 200, 0)                
        title_position = (int(location["point_1"][0]), int(location["point_1"][1] - 10))
        cv2.putText(img, location["name"], title_position, cv2.QT_FONT_NORMAL, 0.8, color, 1)
        cv2.rectangle(img, location["point_1"], location["point_2"], color, 1)

    img = cv2.copyMakeBorder(img, TOP_BORDER_HEIGHT, 0, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    cv2.putText(img, " ".join(matches), (10, 30), cv2.QT_FONT_NORMAL, 0.7, (0, 255, 0), 1)
    # cv2.putText(img, str(hands_positions), (10, 60), cv2.QT_FONT_NORMAL, 0.7, (0, 255, 0), 1)

    cv2.imshow("TOP CIENCIA DE DADOS I", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or cv2.getWindowProperty("TOP CIENCIA DE DADOS I", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
