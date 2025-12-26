#!/usr/bin/env python3
"""
Test the cloned repository model accuracy
"""

import os
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Model path
MODEL_PATH = "../Diabetic-Retinopathy-Detection-CNN-Based-Classifier/diabetic-retinopathy-main/diab_retina_app/keras_model.h5"
TEST_DATA_DIR = "../test_images"

# Class names (from the cloned model)
CLASS_NAMES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferate_DR']
NUM_CLASSES = len(CLASS_NAMES)

def load_and_preprocess_image(image_path):
    """Load and preprocess image according to cloned model requirements"""
    try:
        # Load image
        image = Image.open(image_path)
        
        # Resize to 224x224 (same as cloned model)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.LANCZOS)
        
        # Convert to numpy array
        image_array = np.asarray(image)
        
        # Normalize according to cloned model: (array / 127.0) - 1
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        
        return normalized_image_array
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def test_model_accuracy():
    """Test the cloned model accuracy"""
    print("="*60)
    print("TESTING CLONED MODEL ACCURACY")
    print("="*60)
    
    # Load the model
    try:
        print(f"Loading model from: {MODEL_PATH}")
        
        # Try to load with custom objects to handle compatibility issues
        try:
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        except:
            # Try with custom initializer
            from tensorflow.keras import initializers
            custom_objects = {
                'VarianceScaling': initializers.VarianceScaling
            }
            model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects, compile=False)
        
        print("Model loaded successfully!")
        print(f"Model input shape: {model.input_shape}")
        print(f"Model output shape: {model.output_shape}")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Model is not compatible with current TensorFlow version")
        return None
    
    # Check if test data exists
    test_dir = Path(TEST_DATA_DIR)
    if not test_dir.exists():
        print(f"Test directory not found: {TEST_DATA_DIR}")
        print("Using colored_images for testing...")
        test_dir = Path("../colored_images")
    
    # Collect test images
    test_images = []
    true_labels = []
    
    for class_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = test_dir / class_name
        if class_dir.exists():
            image_files = list(class_dir.glob("*.png"))[:50]  # Limit to 50 images per class
            for img_file in image_files:
                test_images.append(str(img_file))
                true_labels.append(class_idx)
    
    print(f"Found {len(test_images)} test images")
    
    if len(test_images) == 0:
        print("No test images found!")
        return
    
    # Test the model
    predictions = []
    confidences = []
    
    print("\nTesting model on images...")
    for i, img_path in enumerate(test_images):
        if i % 10 == 0:
            print(f"Processing image {i+1}/{len(test_images)}")
        
        # Preprocess image
        processed_image = load_and_preprocess_image(img_path)
        if processed_image is None:
            continue
        
        # Create batch
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = processed_image
        
        # Predict
        try:
            prediction = model.predict(data, verbose=0)
            pred_new = prediction[0]
            pred = max(pred_new)
            index = pred_new.tolist().index(pred)
            
            predictions.append(index)
            confidences.append(float(pred) * 100)
            
        except Exception as e:
            print(f"Error predicting {img_path}: {e}")
            predictions.append(0)  # Default to first class
            confidences.append(0.0)
    
    # Calculate accuracy
    if len(predictions) != len(true_labels):
        print("Warning: Mismatch between predictions and true labels")
        min_len = min(len(predictions), len(true_labels))
        predictions = predictions[:min_len]
        true_labels = true_labels[:min_len]
    
    correct_predictions = sum(1 for pred, true in zip(predictions, true_labels) if pred == true)
    total_predictions = len(predictions)
    accuracy = correct_predictions / total_predictions * 100
    
    print(f"\n" + "="*60)
    print("CLONED MODEL RESULTS")
    print("="*60)
    print(f"Total Images Tested: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average Confidence: {np.mean(confidences):.2f}%")
    
    # Detailed classification report
    print(f"\nClassification Report:")
    print(classification_report(true_labels, predictions, target_names=CLASS_NAMES))
    
    # Confusion matrix
    cm = confusion_matrix(true_labels, predictions)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title('Cloned Model Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('cloned_model_confusion_matrix.png')
    print(f"Confusion matrix saved to: cloned_model_confusion_matrix.png")
    
    return accuracy

if __name__ == "__main__":
    accuracy = test_model_accuracy()
    if accuracy is not None:
        print(f"\nFinal Accuracy: {accuracy:.2f}%")
    else:
        print(f"\nCould not determine model accuracy due to compatibility issues")
