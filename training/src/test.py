import tensorflow as tf
import numpy as np

test_dir = "../input/test"  # Directory containing the testing data
test_model_path = "../output/fer_model-chinese-2.keras"

batch_size = 32
img_height = 48
img_width = 48

test_ds: tf.data.Dataset = tf.keras.utils.image_dataset_from_directory(
  test_dir,
  image_size=(img_height, img_width),
  batch_size=batch_size,
  color_mode="grayscale",
  label_mode="categorical"
)

test_model = tf.keras.models.load_model(test_model_path)
test_model.summary()

loss, acc = test_model.evaluate(test_ds, verbose=2)
print('Restored model, accuracy: {:5.2f}%'.format(100 * acc))

happy_img = tf.keras.utils.load_img('../test/happy.png', color_mode='grayscale', target_size=(48, 48))
happy_arr = tf.keras.utils.img_to_array(happy_img)
happy_arr = np.array([happy_arr])

happy_pred = test_model.predict(happy_arr)
print(happy_pred)
print(np.argmax(happy_pred, axis=-1))

sad_img = tf.keras.utils.load_img('../test/sad.png', color_mode='grayscale', target_size=(48, 48))
sad_arr = tf.keras.utils.img_to_array(sad_img)
sad_arr = np.array([sad_arr])

sad_pred = test_model.predict(sad_arr)
print(sad_pred)
print(np.argmax(sad_pred, axis=-1))