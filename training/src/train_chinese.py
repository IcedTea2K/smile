import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras.models import Sequential

train_dir = "../input/train" # Directory containing the training data

batch_size = 32
img_height = 48
img_width = 48

checkpoint_path = '../output/training_model_chinese.weights.h5'
epochs=50
lr = 1e-3

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

input = Input(shape=(img_height, img_width, 1))
x = Conv2D(filters=256,kernel_size=3,activation='relu',padding='same')(input)

x = Conv2D(filters=512,kernel_size=3,activation='relu',padding='same')(x)
x = BatchNormalization()(x)

#
x = MaxPooling2D(pool_size=(2,2))(x)
x = Dropout(0.4)(x)

x = Conv2D(filters=384,kernel_size=3,activation='relu',padding='same')(x)
x = BatchNormalization()(x)

x = MaxPooling2D(pool_size=(2,2))(x)
x = Dropout(0.4)(x)

x = Conv2D(filters=192,kernel_size=3,activation='relu',padding='same')(x)
x = BatchNormalization()(x)

x = MaxPooling2D(pool_size=(2,2))(x)
x = Dropout(0.4)(x)


x = Conv2D(filters=384,kernel_size=3,activation='relu',padding='same')(x)
x = BatchNormalization()(x)

x = MaxPooling2D(pool_size=(2,2))(x)
x = Dropout(0.4)(x)

x = Flatten()(x)

x = Dense(256,activation='relu')(x)
x = BatchNormalization()(x)

x = Dropout(0.3)(x)
x = Dense(len(class_names),activation='softmax')(x)

model = Model(input,x)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1)

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path,
    monitor='val_accuracy',
    save_best_only=True,
    save_weights_only=True,
    mode='max',
    verbose=1
)

optimizer=tf.keras.optimizers.Adam(learning_rate=lr)
model.compile(loss=tf.keras.losses.categorical_crossentropy, metrics=['accuracy'],optimizer=optimizer)
model.fit(train_ds,validation_data=val_ds,
          epochs=epochs,callbacks=[early_stopping,checkpoint_callback]
)

model.save('../output/fer_model-chinese.keras')