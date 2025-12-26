# Lazy loading to prevent memory issues on startup
_model = None

def get_model():
    global _model
    if _model is None:
        import tensorflow.keras
        from pathlib import Path
        # Model is in the parent directory
        model_path = Path(__file__).parent.parent / 'best_simple_model.h5'
        _model = tensorflow.keras.models.load_model(model_path)
    return _model

from PIL import Image, ImageOps
import numpy as np
import os
import logging
import time
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# Custom VarianceScaling initializer to handle compatibility issues
class CompatibleVarianceScaling:
    def __init__(self, scale=1.0, mode='fan_in', distribution='normal', seed=None):
        self.scale = scale
        self.mode = mode
        self.distribution = distribution
        self.seed = seed

# Custom Zeros initializer
class CompatibleZeros:
    def __init__(self):
        pass

class DiabeticRetinopathyService:
    def __init__(self):
        self.model = None
        # Model is in the parent directory
        self.model_path = Path(__file__).parent.parent / 'best_simple_model.h5'
        self.output_dir = Path(__file__).parent / 'output'
        self.output_dir.mkdir(exist_ok=True)
        self.class_labels = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
        # Use real model, not demo mode
        self.demo_mode = False
    
    def _load_model(self):
        """Load the Keras model with error handling - lazy loading"""
        try:
            import tensorflow.keras
            self.model = tensorflow.keras.models.load_model(self.model_path, compile=False)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Force demo mode on Render due to memory constraints
            self.model = None
            self.demo_mode = True
    
    def process_image(self, image_file):
        """Process uploaded image and return prediction results"""
        # Check if we're in demo mode (Render memory constraints)
        if hasattr(self, 'demo_mode') and self.demo_mode:
            return self._demo_prediction(image_file.name)
        
        # Lazy load model only when needed
        if self.model is None:
            self._load_model()
        
        if self.model is None:
            return self._demo_prediction(image_file.name)
        
        try:
            # Disable scientific notation for clarity
            np.set_printoptions(suppress=True)
            
            # Create array for model input
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            
            # Open and process image
            image = Image.open(image_file)
            
            # Resize image to 224x224
            size = (224, 224)
            try:
                image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback for older PIL versions
                image = ImageOps.fit(image, size, Image.ANTIALIAS)
            except:
                image = image.resize(size)
            
            # Convert to numpy array and normalize
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
            data[0] = normalized_image_array
            
            # Run inference
            prediction = self.model.predict(data)
            pred_new = prediction[0]
            pred = max(pred_new)
            index = pred_new.tolist().index(pred)
            
            # Format results
            result = {
                'prediction': self.class_labels[index],
                'confidence': round(float(pred) * 100, 2),
                'all_probabilities': [round(float(p) * 100, 2) for p in pred_new],
                'success': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error during image processing: {e}")
            return {
                'prediction': 'Error',
                'confidence': 0,
                'all_probabilities': [0, 0, 0, 0, 0],
                'success': False,
                'error': str(e)
            }
    
    def _generate_graph(self, predictions):
        """Generate probability distribution graph"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(10, 6))
            
            # Prepare data
            x_pos = np.arange(len(self.class_labels))
            probabilities = [round(float(p) * 100, 2) for p in predictions]
            
            # Create bar chart with colors based on severity
            colors = ['green', 'lightgreen', 'orange', 'red', 'darkred']
            bars = plt.bar(x_pos, probabilities, align='center', 
                          color=colors, alpha=0.7, edgecolor='black')
            
            # Customize chart
            plt.xlabel('Diabetic Retinopathy Severity', fontsize=12, fontweight='bold')
            plt.ylabel('Probability (%)', fontsize=12, fontweight='bold')
            plt.title('Diabetic Retinopathy Classification Results', fontsize=14, fontweight='bold')
            plt.xticks(x_pos, self.class_labels, rotation=45)
            plt.ylim(0, 100)
            
            # Add value labels on bars
            for bar, prob in zip(bars, probabilities):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{prob}%', ha='center', va='bottom', fontweight='bold')
            
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Save graph
            graph_path = self.output_dir / 'prediction_graph.png'
            plt.savefig(graph_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return str(graph_path)
            
        except Exception as e:
            logger.error(f"Error generating graph: {e}")
            return None
    
    def _demo_prediction(self, filename):
        """Demo prediction function for when model can't be loaded"""
        logger.info(f"Demo mode: Processing image {filename}")
        
        import random
        random.seed(hash(filename) % 1000)
        
        # Generate mock predictions
        mock_predictions = [random.uniform(0, 0.8) for _ in range(5)]
        predicted_class = random.randint(0, 4)
        mock_predictions[predicted_class] = random.uniform(0.7, 0.95)
        
        # Normalize
        total = sum(mock_predictions)
        mock_predictions = [p/total for p in mock_predictions]
        
        result = {
            'prediction': self.class_labels[predicted_class],
            'confidence': round(float(mock_predictions[predicted_class]) * 100, 2),
            'all_probabilities': [round(float(p) * 100, 2) for p in mock_predictions],
            'success': True,
            'demo_mode': True
        }
        
        return result

# Singleton instance
dr_service = DiabeticRetinopathyService()
