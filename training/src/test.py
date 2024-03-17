import tensorflow as tf

test_dir = "../input/test"  # Directory containing the testing data
test_model_path = "../output/fer_model.keras"

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
