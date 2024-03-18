import tensorflow as tf
import numpy as np
import cv2

test_model_path = "../training/output/fer_model-chinese-2.keras"
test_model = tf.keras.models.load_model(test_model_path)

labels = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"] # FER
# labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"] # Deepface

def predict(frame):
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
    if len(results) > 0:
        (x,y,w,h) = results[0]
        crop_img = gray[y:y+h, x:x+w]
        scaled_img = cv2.resize(crop_img, (48,48))
        
        tensor_img = tf.convert_to_tensor(scaled_img)
        tensor_img = np.expand_dims(tensor_img,axis=0)
        prediction = test_model.predict(tensor_img, batch_size=32)[0]

        return prediction
    else:
        return None