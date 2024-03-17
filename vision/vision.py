import numpy as np
import time
import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    results = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=5,
        minSize=(30, 30),
        # flags=cv2.CASCADE_SCALE_IMAGE
    )
    for (x,y,w,h) in results:
        cv2.rectangle(gray, (x,y), (x+w,y+h), (0,255,0),2)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # time.sleep(100)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()