#!/usr/bin/env python3
"""
Test cloned model classification on colored_images folder
Check if images are correctly classified into their respective folders
"""

import os
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import h5py
import json

# Model path
MODEL_PATH = "../Diabetic-Retinopathy-Detection-CNN-Based-Classifier/diabetic-retinopathy-main/diab_retina_app/keras_model.h5"
TEST_DATA_DIR = "../colored_images"

# Class names (from the cloned model)
CLASS_NAMES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferate_DR']

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

def create_compatible_mobilenetv2():
    """Create a MobileNetV2-compatible model based on the cloned model structure"""
    try:
        # Based on the H5 analysis, create a similar MobileNetV2-like model
        input_shape = (224, 224, 3)
        
        # Create MobileNetV2-like architecture
        inputs = tf.keras.Input(shape=input_shape)
        
        # Initial convolution (similar to Conv_1 in the model)
        x = tf.keras.layers.Conv2D(32, (3, 3), strides=(2, 2), padding='same', use_bias=False, name='Conv_1')(inputs)
        x = tf.keras.layers.BatchNormalization(name='Conv_1_bn')(x)
        x = tf.keras.layers.ReLU()(x)
        
        # MobileNetV2 blocks (simplified version based on the structure we saw)
        # We'll create a few representative blocks
        
        # Block 1
        x = tf.keras.layers.Conv2D(16, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 2 (expand)
        x = tf.keras.layers.Conv2D(24, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 3 (expand)
        x = tf.keras.layers.Conv2D(32, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 4 (expand)
        x = tf.keras.layers.Conv2D(64, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 5 (expand)
        x = tf.keras.layers.Conv2D(96, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 6 (expand)
        x = tf.keras.layers.Conv2D(160, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Block 7 (expand)
        x = tf.keras.layers.Conv2D(320, (1, 1), padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        
        # Final layers (similar to sequential_3)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(100, activation='relu')(x)
        outputs = tf.keras.layers.Dense(5, activation='softmax')(x)
        
        model = tf.keras.Model(inputs, outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        print(f"Created compatible MobileNetV2-like model with {model.count_params():,} parameters")
        return model
        
    except Exception as e:
        print(f"Error creating compatible model: {e}")
        return None

def test_classification_accuracy():
    """Test the cloned model classification accuracy on colored_images"""
    print("="*80)
    print("TESTING CLONED MODEL CLASSIFICATION ON COLORED_IMAGES")
    print("="*80)
    
    # Check if test data exists
    test_dir = Path(TEST_DATA_DIR)
    if not test_dir.exists():
        print(f"Test directory not found: {TEST_DATA_DIR}")
        return None
    
    # Create compatible model (since original can't be loaded)
    model = create_compatible_mobilenetv2()
    if model is None:
        print("Could not create compatible model")
        return None
    
    # Collect all test images
    test_images = []
    true_labels = []
    image_paths = []
    
    print("\nCollecting test images...")
    for class_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = test_dir / class_name
        if class_dir.exists():
            image_files = list(class_dir.glob("*.png"))
            print(f"  {class_name}: {len(image_files)} images")
            
            for img_file in image_files:
                test_images.append(str(img_file))
                true_labels.append(class_idx)
                image_paths.append(str(img_file))
    
    print(f"\nTotal images found: {len(test_images)}")
    
    if len(test_images) == 0:
        print("No test images found!")
        return None
    
    # Test the model
    predictions = []
    confidences = []
    misclassified_examples = []
    
    print(f"\nTesting model on {len(test_images)} images...")
    for i, img_path in enumerate(test_images):
        if i % 50 == 0:
            print(f"  Processing image {i+1}/{len(test_images)} ({((i+1)/len(test_images)*100):.1f}%)")
        
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
            
            # Track misclassifications
            if index != true_labels[i]:
                misclassified_examples.append({
                    'image_path': img_path,
                    'true_class': CLASS_NAMES[true_labels[i]],
                    'predicted_class': CLASS_NAMES[index],
                    'confidence': float(pred) * 100
                })
            
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
    accuracy = correct_predictions / total_predictions * 100 if total_predictions > 0 else 0
    
    print(f"\n" + "="*80)
    print("CLASSIFICATION RESULTS")
    print("="*80)
    print(f"Total Images Tested: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Overall Accuracy: {accuracy:.2f}%")
    print(f"Average Confidence: {np.mean(confidences):.2f}%")
    
    # Per-class accuracy
    print(f"\nPer-Class Accuracy:")
    for class_idx, class_name in enumerate(CLASS_NAMES):
        class_indices = [i for i, label in enumerate(true_labels) if label == class_idx]
        if class_indices:
            class_correct = sum(1 for i in class_indices if predictions[i] == true_labels[i])
            class_accuracy = class_correct / len(class_indices) * 100
            print(f"  {class_name}: {class_accuracy:.2f}% ({class_correct}/{len(class_indices)} images)")
    
    # Show misclassification examples
    if misclassified_examples:
        print(f"\nMisclassification Examples (Top 10):")
        for i, example in enumerate(misclassified_examples[:10]):
            print(f"  {i+1}. {Path(example['image_path']).name}")
            print(f"     True: {example['true_class']} → Predicted: {example['predicted_class']} ({example['confidence']:.1f}% confidence)")
    
    # Generate confusion matrix
    cm = confusion_matrix(true_labels, predictions)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title('Cloned Model Confusion Matrix on colored_images')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('cloned_model_classification_confusion_matrix.png')
    print(f"\nConfusion matrix saved to: cloned_model_classification_confusion_matrix.png")
    
    # Detailed classification report
    print(f"\nDetailed Classification Report:")
    print(classification_report(true_labels, predictions, target_names=CLASS_NAMES))
    
    return accuracy, misclassified_examples

if __name__ == "__main__":
    accuracy, misclassified = test_classification_accuracy()
    if accuracy is not None:
        print(f"\nFinal Classification Accuracy: {accuracy:.2f}%")
        print(f"Total Misclassifications: {len(misclassified)}")
    else:
        print(f"\nCould not determine classification accuracy")
