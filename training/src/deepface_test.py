import numpy as np
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Flatten, Dense, Dropout
from tensorflow.keras.models import Sequential

batch_size = 32
img_height = 48
img_width = 48

test_dir = "../input/test"  # Directory containing the testing data
test_model_path = "../output/facial_expression_model_weights.h5"

test_ds: tf.data.Dataset = tf.keras.utils.image_dataset_from_directory(
  test_dir,
  image_size=(img_height, img_width),
  batch_size=batch_size,
  color_mode="grayscale",
  label_mode="categorical"
)

num_classes = 7

model = Sequential()

# 1st convolution layer
model.add(Conv2D(64, (5, 5), activation="relu", input_shape=(48, 48, 1)))
model.add(MaxPooling2D(pool_size=(5, 5), strides=(2, 2)))

# 2nd convolution layer
model.add(Conv2D(64, (3, 3), activation="relu"))
model.add(Conv2D(64, (3, 3), activation="relu"))
model.add(AveragePooling2D(pool_size=(3, 3), strides=(2, 2)))

# 3rd convolution layer
model.add(Conv2D(128, (3, 3), activation="relu"))
model.add(Conv2D(128, (3, 3), activation="relu"))
model.add(AveragePooling2D(pool_size=(3, 3), strides=(2, 2)))

model.add(Flatten())

# fully connected neural networks
model.add(Dense(1024, activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(1024, activation="relu"))
model.add(Dropout(0.2))

model.add(Dense(num_classes, activation="softmax"))

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.load_weights(test_model_path)

model.save('../output/deepface_model.keras')

# model.summary()

# loss, acc = model.evaluate(test_ds, verbose=2)
# print('Restored model, accuracy: {:5.2f}%'.format(100 * acc))

happy_img = tf.keras.utils.load_img('../happy.png', color_mode='grayscale', target_size=(48, 48))
happy_arr = tf.keras.utils.img_to_array(happy_img)
happy_arr = np.array([happy_arr])

happy_pred = model.predict(happy_arr)
print(happy_pred)
print(np.argmax(happy_pred, axis=-1))

sad_img = tf.keras.utils.load_img('../sad.png', color_mode='grayscale', target_size=(48, 48))
sad_arr = tf.keras.utils.img_to_array(sad_img)
sad_arr = np.array([sad_arr])

sad_pred = model.predict(sad_arr)
print(sad_pred)
print(np.argmax(sad_pred, axis=-1))