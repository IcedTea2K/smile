import tensorflow as tf
from tensorflow.keras import layers, Input, Model
from tensorflow.keras.models import Sequential

train_dir = "../input/train" # Directory containing the training data

batch_size = 32
img_height = 48
img_width = 48

checkpoint_path = '../output/training_model.weights.h5'
epochs=50

train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
  train_dir,
  image_size=(img_height, img_width),
  batch_size=batch_size,
  color_mode="grayscale",
  label_mode="categorical",
  seed=123,
  validation_split=0.2,
  subset="both"
)

class_names = train_ds.class_names

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

data_augmentation = Sequential([
  layers.RandomFlip("horizontal"),
  layers.RandomRotation(0.1),
  layers.RandomZoom(0.1)
])

model = Sequential([
  Input(shape=(img_height, img_width, 1), batch_size=batch_size),
  data_augmentation,
  layers.Rescaling(1./255),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D((2,2)),
  layers.Dropout(0.25),

  layers.Conv2D(128, 3, padding='same', activation='relu'),
  layers.MaxPooling2D((2,2)),
  layers.Conv2D(128, 3, padding='same', activation='relu'),
  layers.MaxPooling2D((2,2)),
  layers.Dropout(0.25),

  layers.Flatten(),
  layers.Dense(1024, activation='relu'),
  layers.Dropout(0.5),

  layers.Dense(len(class_names), activation='softmax')
])

# base_model = tf.keras.applications.mobilenet.MobileNet(
#   include_top=False,
#   input_shape=(img_height, img_width, 3)
# )

# base_model.trainable = False

# inputs = Input(shape=(img_height, img_width, 3), batch_size=batch_size)

# scale_layer = layers.Rescaling(scale=1 / 127.5, offset=-1)

# x = scale_layer(inputs)
# x = base_model(x)
# x = layers.GlobalAveragePooling2D()(x)
# # x = layers.Dense(1024, activation='relu')(x)
# x = layers.Dropout(0.2)(x)  # Regularize with dropout
# outputs = layers.Dense(len(class_names))(x)
# model = Model(inputs, outputs)

# model.summary(show_trainable=True)

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1)

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path,
    monitor='val_accuracy',
    save_best_only=True,
    save_weights_only=True,
    mode='max',
    verbose=1
)

history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs,
  callbacks=[early_stopping, checkpoint_callback]
)

model.save('../output/fer_model.keras')