import tensorflow as tf
import numpy as np
# from rmn import RMN
import cv2

# m = RMN()

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

        # results = m.detect_emotion_for_single_frame(scaled_img)
        # print(results)

        tensor_img = tf.convert_to_tensor(scaled_img)
        tensor_img = np.expand_dims(tensor_img,axis=0)
        prediction = test_model.predict(tensor_img, batch_size=32)[0]

        return prediction
    else:
        return None

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        prediction = predict(frame)
        if prediction is not None:
            # guess = np.argmax(prediction, axis=-1)[0]
            top = prediction.argsort()[-3:][::-1]
            print([f"{labels[guess]} {round(prediction[guess]*100)}%" for guess in top])

        # Display the resulting frame
        cv2.imshow('scale',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # time.sleep(100)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()