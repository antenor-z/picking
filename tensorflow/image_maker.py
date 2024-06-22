import cv2
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

counter = 0

path = input("Where to save? ")

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture image.")
            break

        filename = f"{path}/image_{counter:04d}.jpg"

        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")

        counter += 1

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting")

finally:
    cap.release()
    cv2.destroyAllWindows()
