# _evaluate_model.py

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

MODEL_PATH = os.path.join('models', 'best_model.keras')
TEST_DATA_DIR = 'test_dataset'
IMG_SIZE = (32, 32)
BATCH_SIZE = 32

print("Model Evaluation on Test Dataset\n")

# Load the trained model
print(f"Loading model from {MODEL_PATH}...")
try:
    model = load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Create a data generator for the test set
print(f"\nLoading test data from {TEST_DATA_DIR}...")
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    TEST_DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False  # Crucial for classification report
)

print(f"Found {test_generator.samples} test images across {test_generator.num_classes} classes.")
print(f"Class labels: {list(test_generator.class_indices.keys())}")

# Evaluate the model ,.evaluate()
print("\nEvaluating model on the test set")
loss, accuracy = model.evaluate(test_generator, verbose=1)
print(f"\nTest Results:")
print(f"Test Accuracy: {accuracy * 100:.2f}%")
print(f"Test Loss: {loss:.4f}")

# Get detailed predictions for a classification report
print("\nGenerating classification report")
# Reset the generator to be sure it's at the beginning
test_generator.reset()
# Get predictions
print("Making predictions...")
predictions = model.predict(test_generator, steps=int(np.ceil(test_generator.samples/test_generator.batch_size)), verbose=1)
predicted_classes = np.argmax(predictions, axis=1)

# Get true labels
true_classes = test_generator.classes
class_labels = list(test_generator.class_indices.keys())

# Print the detailed classification report
print("\nClassification Report")
print(classification_report(true_classes, predicted_classes, target_names=class_labels))

# Confusion Matrix
print("\nGenerating confusion matrix")
cm = confusion_matrix(true_classes, predicted_classes)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=class_labels, yticklabels=class_labels, cmap='Blues')
plt.title(f'Confusion Matrix - Test Accuracy: {accuracy * 100:.2f}%')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.show()

# Show per-class breakdown
print("\nPer-Class Image Counts")
for i, class_name in enumerate(class_labels):
    count = np.sum(true_classes == i)
    correct = np.sum((true_classes == i) & (predicted_classes == i))
    print(f"{class_name}: {correct}/{count} correct ({correct/count*100:.1f}%)")

print(f"\nSummary")
print(f"Overall Test Accuracy: {accuracy * 100:.2f}%")
if accuracy < 0.8:
    print("Low accuracy (domain shift?). Model needs more diverse training data")
elif accuracy < 0.9:
    print("Moderate accuracy")
else:
    print("Good accuracy")

