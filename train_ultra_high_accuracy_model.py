#!/usr/bin/env python3
"""
Ultra High-Accuracy Diabetic Retinopathy Model Training Pipeline
Optimized for >90% accuracy using advanced techniques and best practices
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import datetime
import json
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger
from tensorflow.keras.optimizers import AdamW
from tensorflow.keras.regularizers import l2

print("TensorFlow Version:", tf.__version__)
print("GPU Available:", tf.config.list_physical_devices('GPU'))
print("Using float32 precision")

class UltraHighAccuracyDRTrainer:
    def __init__(self):
        # Ultra-optimized configuration for >90% accuracy
        self.IMG_HEIGHT = 512  # Higher resolution for better accuracy
        self.IMG_WIDTH = 512
        self.BATCH_SIZE = 8   # Smaller batch for higher resolution
        self.EPOCHS = 150      # More epochs for better convergence
        self.LEARNING_RATE = 1e-5  # Much lower learning rate for fine-tuning
        
        # Data paths
        self.DATA_DIR = Path('../colored_images')
        self.MODEL_SAVE_PATH = '../best_ultra_high_accuracy_model.h5'
        self.PLOTS_DIR = Path('../training_plots')
        self.PLOTS_DIR.mkdir(exist_ok=True)
        
        # Class names
        self.CLASS_NAMES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferate_DR']
        self.NUM_CLASSES = len(self.CLASS_NAMES)
        
        # Initialize variables
        self.model = None
        self.history = None
        
    def create_enhanced_data_generators(self):
        """Create enhanced data generators with advanced augmentation"""
        print("\n" + "="*60)
        print("ENHANCED DATA GENERATION")
        print("="*60)
        
        # Advanced training augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,           # Increased rotation
            width_shift_range=0.2,       # More horizontal shift
            height_shift_range=0.2,      # More vertical shift
            shear_range=0.2,             # More shear
            zoom_range=0.3,              # More zoom
            horizontal_flip=True,
            vertical_flip=False,         # Don't flip medical images vertically
            brightness_range=[0.7, 1.3],  # More brightness variation
            channel_shift_range=0.1,     # Color channel shifts
            fill_mode='nearest',
            validation_split=0.15        # 15% for validation (more training data)
        )
        
        # Validation generator (minimal augmentation)
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.15
        )
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            self.DATA_DIR,
            target_size=(self.IMG_HEIGHT, self.IMG_WIDTH),
            batch_size=self.BATCH_SIZE,
            class_mode='categorical',
            subset='training',
            shuffle=True,
            seed=42
        )
        
        validation_generator = val_datagen.flow_from_directory(
            self.DATA_DIR,
            target_size=(self.IMG_HEIGHT, self.IMG_WIDTH),
            batch_size=self.BATCH_SIZE,
            class_mode='categorical',
            subset='validation',
            shuffle=False,
            seed=42
        )
        
        print(f"Training samples: {train_generator.samples}")
        print(f"Validation samples: {validation_generator.samples}")
        print(f"Class indices: {train_generator.class_indices}")
        
        # Calculate class weights for imbalanced dataset
        class_weights = self._calculate_class_weights(train_generator)
        print(f"Class weights: {class_weights}")
        
        return train_generator, validation_generator, class_weights
    
    def _calculate_class_weights(self, generator):
        """Calculate class weights to handle imbalanced dataset"""
        from sklearn.utils.class_weight import compute_class_weight
        
        # Get class counts
        class_counts = {}
        for class_name in self.CLASS_NAMES:
            class_path = self.DATA_DIR / class_name
            if class_path.exists():
                class_counts[class_name] = len(list(class_path.glob('*.png')))
            else:
                class_counts[class_name] = 0
        
        # Calculate weights
        classes = list(class_counts.keys())
        counts = list(class_counts.values())
        
        if sum(counts) > 0:
            weights = compute_class_weight(
                'balanced',
                classes=np.array(range(len(classes))),
                y=np.repeat(range(len(classes)), counts)
            )
            class_weights = dict(enumerate(weights))
        else:
            class_weights = {i: 1.0 for i in range(len(classes))}
        
        return class_weights
    
    def create_ultra_advanced_model(self):
        """Create ultra-advanced model using EfficientNetB4 with advanced techniques"""
        print("\n" + "="*60)
        print("ULTRA ADVANCED MODEL ARCHITECTURE")
        print("="*60)
        
        # Use EfficientNetB4 for even better performance
        base_model = tf.keras.applications.EfficientNetB4(
            weights='imagenet',
            include_top=False,
            input_shape=(self.IMG_HEIGHT, self.IMG_WIDTH, 3)
        )
        
        # Freeze more layers initially
        for layer in base_model.layers[:-30]:
            layer.trainable = False
        
        # Build the model with advanced architecture
        inputs = keras.Input(shape=(self.IMG_HEIGHT, self.IMG_WIDTH, 3))
        
        # Advanced data augmentation layers
        x = layers.RandomFlip('horizontal')(inputs)
        x = layers.RandomRotation(0.15)(x)
        x = layers.RandomZoom(0.15)(x)
        x = layers.RandomContrast(0.15)(x)
        x = layers.RandomBrightness(0.15)(x)
        
        # Add Gaussian noise for regularization
        x = layers.GaussianNoise(0.01)(x)
        
        # Preprocess for EfficientNet
        x = tf.keras.applications.efficientnet.preprocess_input(x)
        
        # Base model
        x = base_model(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        
        # Advanced classification head
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.6)(x)
        
        # Dense layers with progressive reduction
        x = layers.Dense(1024, activation='relu', kernel_regularizer=l2(0.01))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(512, activation='relu', kernel_regularizer=l2(0.01))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)
        
        x = layers.Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(128, activation='relu', kernel_regularizer=l2(0.01))(x)
        x = layers.Dropout(0.2)(x)
        
        outputs = layers.Dense(self.NUM_CLASSES, activation='softmax')(x)
        
        model = keras.Model(inputs, outputs)
        
        # Compile with advanced optimizer
        optimizer = AdamW(
            learning_rate=self.LEARNING_RATE,
            weight_decay=1e-4,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-7
        )
        
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        model.summary()
        return model
    
    def create_advanced_callbacks(self):
        """Create advanced callbacks for better training"""
        callbacks = [
            # Early stopping with more patience
            EarlyStopping(
                monitor='val_accuracy',
                patience=25,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Model checkpoint
            ModelCheckpoint(
                self.MODEL_SAVE_PATH,
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False,
                verbose=1
            ),
            
            # Advanced learning rate scheduler
            ReduceLROnPlateau(
                monitor='val_accuracy',
                factor=0.5,
                patience=10,
                min_lr=1e-7,
                verbose=1
            ),
            
            # CSV logger
            CSVLogger('ultra_training_log.csv', append=True)
        ]
        
        return callbacks
    
    def train_model(self):
        """Train the ultra high accuracy model"""
        print("\n" + "="*60)
        print("TRAINING ULTRA HIGH ACCURACY MODEL")
        print("="*60)
        
        # Create data generators
        train_gen, val_gen, class_weights = self.create_enhanced_data_generators()
        
        # Create model
        self.model = self.create_ultra_advanced_model()
        
        # Create callbacks
        callbacks = self.create_advanced_callbacks()
        
        # Calculate steps
        steps_per_epoch = train_gen.samples // self.BATCH_SIZE
        validation_steps = val_gen.samples // self.BATCH_SIZE
        
        print(f"Steps per epoch: {steps_per_epoch}")
        print(f"Validation steps: {validation_steps}")
        
        # Train model
        self.history = self.model.fit(
            train_gen,
            steps_per_epoch=steps_per_epoch,
            epochs=self.EPOCHS,
            validation_data=val_gen,
            validation_steps=validation_steps,
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1
        )
        
        return self.history
    
    def fine_tune_model(self):
        """Fine-tune the model with unfrozen layers"""
        print("\n" + "="*60)
        print("FINE-TUNING MODEL")
        print("="*60)
        
        # Unfreeze more layers
        for layer in self.model.layers[-50:]:
            layer.trainable = True
        
        # Recompile with lower learning rate
        optimizer = AdamW(
            learning_rate=5e-6,  # Even lower for fine-tuning
            weight_decay=1e-5,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-7
        )
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        # Continue training
        fine_tune_history = self.model.fit(
            train_gen,
            steps_per_epoch=steps_per_epoch,
            epochs=50,  # Additional epochs for fine-tuning
            validation_data=val_gen,
            validation_steps=validation_steps,
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1
        )
        
        return fine_tune_history

def main():
    """Main training function"""
    trainer = UltraHighAccuracyDRTrainer()
    
    print("Starting Ultra High-Accuracy DR Model Training...")
    print("Target: >90% Accuracy")
    
    # Train the model
    history = trainer.train_model()
    
    # Fine-tune the model
    fine_tune_history = trainer.fine_tune_model()
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED")
    print("="*60)
    print(f"Best validation accuracy: {max(history.history['val_accuracy']):.4f}")
    print(f"Best validation AUC: {max(history.history['val_auc']):.4f}")
    print(f"Model saved to: {trainer.MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()
