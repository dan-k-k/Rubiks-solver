# trainclassifier.py

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import numpy as np
import random

DATA_DIR = 'dataset'
MODELS_DIR = 'models'
IMG_SIZE = (32, 32)
BATCH_SIZE = 32
EPOCHS = 30 # Early stopping happens around ep 7

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

def random_ninety_degree_rotate(image):
    """Randomly rotates an image by 0, 90, 180, or 270 degrees."""
    k = random.choice([0, 1, 2, 3])
    return np.rot90(image, k=k)

# Data Loading and Augmentation
# Apply random transformations (rotation, zoom, etc.)
datagen = ImageDataGenerator(
    rescale=1./255,          # Normalize pixel values to 0-1
    validation_split=0.2,    # Use 20% of data for validation
    preprocessing_function=random_ninety_degree_rotate,  # random 90-deg rotation 
    rotation_range=15,       # Then ±15 degree rotation
    zoom_range=0.15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    brightness_range=[0.8, 1.2],  # Add brightness variation
    horizontal_flip=False,   # Not useful for this task
    fill_mode='nearest'
)

train_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)
    
validation_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# Build the CNN Model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5), # prevent overfitting
    Dense(train_generator.num_classes, activation='softmax')
])

model.summary()

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train the Model
print("\n--- Starting Training ---")

# Save best model automatically during training (used for live predictions)
checkpoint = ModelCheckpoint(
    filepath=os.path.join(MODELS_DIR, 'best_model.keras'),
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    callbacks=[checkpoint, early_stop]
)

# Save the Trained Model
model_path = os.path.join(MODELS_DIR, 'colour_classifierES.h5')
model.save(model_path)
print(f"\n--- Training Complete. Model saved to {model_path} ---")

# Training history
import matplotlib.pyplot as plt
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
num_epochs_ran = len(history.history['accuracy'])
epochs_range = range(num_epochs_ran)
plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')
plt.show()

