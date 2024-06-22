import tensorflow as tf
import numpy as np
import cv2
import json

model = tf.keras.models.load_model('component_classifier.keras')

with open("categories.json") as fp:
    class_names = json.load(fp)


cap = cv2.VideoCapture(0)  

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    img = cv2.resize(frame, (180, 180))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    
    score = tf.nn.softmax(predictions[0])

    predicted_class = class_names[np.argmax(score)]
    confidence = 100 * np.max(score)

    cv2.putText(frame, f"{predicted_class} {confidence:.2f}%",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('TOP CIENCIA DE DADOS I', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or cv2.getWindowProperty("TOP CIENCIA DE DADOS I", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()