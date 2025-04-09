import cv2
import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from PIL import Image
import io

class TrainablePhotoValidator:
    def __init__(self, model_path=None):
        """
        Initialize the trainable photo validator.
        
        Args:
            model_path: Path to a pre-trained model file (optional)
        """
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        
        # Load pre-trained model if provided
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"Loaded pre-trained model from {model_path}")
        else:
            self.model = None
            print("No pre-trained model loaded. Use train() method to train a new model.")
    
    def extract_features(self, image):
        """
        Extract features from an image for classification.
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Basic image properties
        height, width = image.shape[:2]
        features['resolution'] = width * height
        features['aspect_ratio'] = width / height if height > 0 else 0
        
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Blur detection
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        features['laplacian_var'] = laplacian_var
        
        # Background analysis
        # Sample background from edges
        edge_points = [
            (0, 0),                # Top-left
            (width-1, 0),          # Top-right
            (0, height-1),         # Bottom-left
            (width-1, height-1),   # Bottom-right
            (width//2, 0),         # Top-middle
            (width//2, height-1),  # Bottom-middle
            (0, height//2),        # Left-middle
            (width-1, height//2)   # Right-middle
        ]
        
        # Get background color samples
        bg_colors = []
        for x, y in edge_points:
            if len(image.shape) == 3:
                bg_colors.append(image[y, x])
            else:
                bg_colors.append(np.array([image[y, x], image[y, x], image[y, x]]))
        
        # Calculate average background color
        avg_bg = np.mean(bg_colors, axis=0)
        features['bg_r'] = avg_bg[0]
        features['bg_g'] = avg_bg[1]
        features['bg_b'] = avg_bg[2]
        features['bg_brightness'] = np.mean(avg_bg)
        
        # Background uniformity
        non_bg_pixels = 0
        sample_step = max(1, min(height, width) // 50)  # Sample fewer pixels for efficiency
        
        for y in range(0, height, sample_step):
            for x in range(0, width, sample_step):
                if len(image.shape) == 3:
                    pixel = image[y, x]
                else:
                    pixel = np.array([image[y, x], image[y, x], image[y, x]])
                color_diff = np.sqrt(np.sum((pixel - avg_bg) ** 2))
                if color_diff > 30:  # Threshold for background difference
                    non_bg_pixels += 1
        
        sampled_pixels = (height // sample_step) * (width // sample_step)
        features['bg_uniformity'] = 1.0 - (non_bg_pixels / sampled_pixels)
        
        # Face detection
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        features['face_count'] = len(faces)
        
        if len(faces) == 1:
            # Single face detected
            x, y, w, h = faces[0]
            
            # Face size ratio
            face_area = w * h
            image_area = width * height
            features['face_ratio'] = face_area / image_area
            
            # Face position
            face_center_x = x + w / 2
            face_center_y = y + h / 2
            image_center_x = width / 2
            image_center_y = height / 2
            
            features['face_h_offset'] = abs(face_center_x - image_center_x) / width
            features['face_v_offset'] = abs(face_center_y - image_center_y) / height
            
            # Eye detection
            face_roi = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi)
            features['eye_count'] = len(eyes)
            
            # Face ROI blur
            face_blur = cv2.Laplacian(face_roi, cv2.CV_64F).var()
            features['face_blur'] = face_blur
        else:
            # No face or multiple faces
            features['face_ratio'] = 0
            features['face_h_offset'] = 1.0
            features['face_v_offset'] = 1.0
            features['eye_count'] = 0
            features['face_blur'] = 0
        
        return features
    
    def train(self, valid_dir, invalid_dir, model_output_path=None):
        """
        Train the validator using directories of valid and invalid photos.
        
        Args:
            valid_dir: Directory containing valid ID photos
            invalid_dir: Directory containing invalid ID photos
            model_output_path: Path to save the trained model (optional)
            
        Returns:
            Classification report
        """
        # Load and extract features from valid images
        valid_features = []
        print(f"Processing valid images from {valid_dir}...")
        valid_files = [f for f in os.listdir(valid_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for filename in valid_files:
            try:
                image_path = os.path.join(valid_dir, filename)
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Warning: Could not read {filename}")
                    continue
                    
                features = self.extract_features(image)
                valid_features.append((features, 1))  # 1 = valid
                print(f"Processed valid image: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        
        # Load and extract features from invalid images
        invalid_features = []
        print(f"Processing invalid images from {invalid_dir}...")
        invalid_files = [f for f in os.listdir(invalid_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for filename in invalid_files:
            try:
                image_path = os.path.join(invalid_dir, filename)
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Warning: Could not read {filename}")
                    continue
                    
                features = self.extract_features(image)
                invalid_features.append((features, 0))  # 0 = invalid
                print(f"Processed invalid image: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        
        # Combine datasets
        all_data = valid_features + invalid_features
        
        if len(all_data) == 0:
            print("Error: No valid training data found")
            return None
            
        # Prepare data for training
        X = []
        y = []
        
        for features, label in all_data:
            # Convert features dictionary to vector
            feature_vector = [
                features['resolution'],
                features['aspect_ratio'],
                features['laplacian_var'],
                features['bg_r'],
                features['bg_g'],
                features['bg_b'],
                features['bg_brightness'],
                features['bg_uniformity'],
                features['face_count'],
                features['face_ratio'],
                features['face_h_offset'],
                features['face_v_offset'],
                features['eye_count'],
                features['face_blur']
            ]
            X.append(feature_vector)
            y.append(label)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train a Random Forest classifier
        print("Training classifier...")
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred)
        print("Model evaluation:")
        print(report)
        
        # Save the model
        self.model = clf
        if model_output_path:
            joblib.dump(clf, model_output_path)
            print(f"Model saved to {model_output_path}")
        
        # Get feature importances
        feature_names = [
            'resolution', 'aspect_ratio', 'laplacian_var', 
            'bg_r', 'bg_g', 'bg_b', 'bg_brightness', 'bg_uniformity',
            'face_count', 'face_ratio', 'face_h_offset', 'face_v_offset',
            'eye_count', 'face_blur'
        ]
        
        importances = clf.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print("Feature ranking:")
        for i in range(len(feature_names)):
            print(f"{i+1}. {feature_names[indices[i]]} ({importances[indices[i]]:.4f})")
        
        return report
    
    def validate(self, image_path=None, image_buffer=None):
        """
        Validate an image using the trained model.
        
        Args:
            image_path: Path to the image file (optional)
            image_buffer: Image buffer (optional)
            
        Returns:
            Dictionary with validation results
        """
        if self.model is None:
            return {"valid": False, "error": "No trained model available. Please train the model first."}
        
        # Load image
        if image_path:
            image = cv2.imread(image_path)
            if image is None:
                return {"valid": False, "error": "Could not read image file"}
        elif image_buffer:
            nparr = np.frombuffer(image_buffer, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return {"valid": False, "error": "Could not decode image data"}
        else:
            return {"valid": False, "error": "No image provided"}
        
        # Check minimum resolution
        height, width = image.shape[:2]
        if width < 150 or height < 150:
            return {"valid": False, "error": "Image resolution too low (minimum 150x150 pixels required)"}
        
        # Extract features
        features = self.extract_features(image)
        
        # Basic checks before ML classification
        if features['face_count'] == 0:
            return {"valid": False, "error": "No face detected in the image"}
        
        if features['face_count'] > 1:
            return {"valid": False, "error": "Multiple faces detected. Only one face should be in the ID photo"}
        
        # Prepare feature vector
        feature_vector = [
            features['resolution'],
            features['aspect_ratio'],
            features['laplacian_var'],
            features['bg_r'],
            features['bg_g'],
            features['bg_b'],
            features['bg_brightness'],
            features['bg_uniformity'],
            features['face_count'],
            features['face_ratio'],
            features['face_h_offset'],
            features['face_v_offset'],
            features['eye_count'],
            features['face_blur']
        ]
        
        # Predict using the trained model
        prediction = self.model.predict([feature_vector])[0]
        probability = self.model.predict_proba([feature_vector])[0]
        
        # Get confidence score
        confidence = probability[1] if prediction == 1 else probability[0]
        
        # Prepare detailed result
        result = {
            "valid": bool(prediction),
            "confidence": float(confidence),
            "details": {
                "resolution": f"{width}x{height}",
                "blur_level": features['laplacian_var'],
                "background": {
                    "uniformity": features['bg_uniformity'] * 100,
                    "brightness": features['bg_brightness']
                },
                "face": {
                    "detected": features['face_count'] > 0,
                    "size_ratio": features['face_ratio'] * 100,
                    "centered": max(features['face_h_offset'], features['face_v_offset']) < 0.3,
                    "eyes_detected": features['eye_count']
                }
            }
        }
        
        # Add error message if invalid
        if not result["valid"]:
            # Determine the most likely reason for rejection
            if features['face_count'] == 0:
                result["error"] = "No face detected in the image"
            elif features['bg_uniformity'] < 0.5:
                result["error"] = "Background is not uniform enough"
            elif features['bg_brightness'] < 180:
                result["error"] = "Background is not light enough"
            elif features['laplacian_var'] < 50:
                result["error"] = "Image is too blurry"
            elif features['face_ratio'] < 0.05:
                result["error"] = "Face is too small in the image"
            elif features['face_ratio'] > 0.8:
                result["error"] = "Face is too large in the image"
            elif max(features['face_h_offset'], features['face_v_offset']) > 0.3:
                result["error"] = "Face is not properly centered"
            elif features['eye_count'] < 2:
                result["error"] = "Eyes are not clearly visible"
            else:
                result["error"] = "Image does not meet the learned criteria for a valid ID photo"
        
        return result

