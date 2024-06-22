from tkinter import Tk, simpledialog
from util import open_config
from predictor import predict
import threading
import json
import cv2
import json

TOP_BORDER_HEIGHT = 80
CONFIG_PATH = "config.json"
CAM_NUMBER = 0

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


points_of_interest = open_config()

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

cap = cv2.VideoCapture(CAM_NUMBER)

cv2.namedWindow("TOP CIENCIA DE DADOS I")
cv2.setMouseCallback("TOP CIENCIA DE DADOS I", draw_rectangle)

while True:
    objs_positions = []
    matches = []
    wrong = []

    success, img = cap.read()
    
    _, objs_positions = predict(img)

    # Draw indications of found objects
    for [avg_x, avg_y, obj_name] in objs_positions:
        text_size, _ = cv2.getTextSize(obj_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_width, text_height = text_size
        
        top_left = (avg_x - 30, avg_y - text_height)
        bottom_right = (avg_x - 30 + text_width, avg_y + 5)
        
        cv2.rectangle(img, top_left, bottom_right, (255, 255, 255), cv2.FILLED)
        cv2.putText(img, obj_name, (avg_x - 30, avg_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # Draw boxes defined by the user
    for location in points_of_interest:
        color = (200, 0, 0)
        for hand_position in objs_positions:
            if location["point_1"][0] < hand_position[0] < location["point_2"][0] and \
            location["point_1"][1] < hand_position[1] < location["point_2"][1]:
                if location["name"] == hand_position[2]:  # if object is in the right box
                    matches.append(location["name"])
                    color = (0, 200, 0)
                else:  # if object is in the wrong box
                    wrong.append(location["name"])
                    color = (0, 0, 200)

        title_position = (int(location["point_1"][0]), int(location["point_1"][1] - 10))
        
        text_size, _ = cv2.getTextSize(location["name"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_width, text_height = text_size

        top_left = (title_position[0], title_position[1] - text_height)
        bottom_right = (title_position[0] + text_width, title_position[1] + 5)

        cv2.rectangle(img, top_left, bottom_right, color, cv2.FILLED)
        cv2.putText(img, location["name"], title_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.rectangle(img, location["point_1"], location["point_2"], color, 1)


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
