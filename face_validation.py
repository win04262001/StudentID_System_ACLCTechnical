import cv2
import numpy as np
import os
from PIL import Image
import io

class FaceValidator:
    def __init__(self):
        # Configuration parameters - you can adjust these
        self.blur_threshold = 80  # Lowered from 100 to be more lenient on blur
        self.background_threshold = 35  # Increased from 30 to be more lenient on background
        self.min_face_size = 0.08  # Lowered from 0.1 to allow slightly smaller faces
        self.max_face_size = 0.75  # Increased from 0.7 to allow slightly larger faces
        self.position_tolerance = 0.25  # Increased from 0.2 to be more lenient on centering
        
        # Load face cascade
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Load eye cascade for additional validation
        eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        
    def validate_from_file(self, image_path):
        """Validate a profile image from a file path"""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {"valid": False, "error": "Could not read image file"}
        
        return self._validate_image(image)
    
    def validate_from_buffer(self, image_buffer):
        """Validate a profile image from a buffer (e.g., from request.files)"""
        # Convert buffer to numpy array
        nparr = np.frombuffer(image_buffer, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return {"valid": False, "error": "Could not decode image data"}
        
        return self._validate_image(image)
    
    def validate_from_pil(self, pil_image):
        """Validate a profile image from a PIL Image object"""
        # Convert PIL Image to OpenCV format
        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR (OpenCV uses BGR)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        
        return self._validate_image(open_cv_image)
    
    def _validate_image(self, image):
        """Core validation logic for a profile image"""
        # Check image dimensions and resize if needed
        height, width = image.shape[:2]
        if width < 300 or height < 300:
            # If image is too small but has reasonable dimensions, try to resize it
            if width >= 150 and height >= 150 and width/height >= 0.5 and width/height <= 2.0:
                # Resize to minimum dimensions
                scale = max(300/width, 300/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                height, width = image.shape[:2]
                print(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            else:
                return {"valid": False, "error": "Image resolution too low (minimum 300x300 pixels required)"}
        
        # Check if image is blurry
        blur_result = self._check_image_blur(image)
        if blur_result["is_blurry"]:
            return {
                "valid": False, 
                "error": "Image is too blurry. Please upload a clearer photo.", 
                "details": blur_result
            }
        
        # Check background
        background_result = self._check_background(image)
        if not background_result["is_plain_background"]:
            return {
                "valid": False, 
                "error": "Background is not plain or uniform. Please use a solid white or light background.", 
                "details": background_result
            }
        
        if not background_result["is_light_background"]:
            return {
                "valid": False, 
                "error": "Background is not light enough. Please use a white or light-colored background.", 
                "details": background_result
            }
        
        # Detect face and validate
        face_result = self._validate_face(image)
        if not face_result["valid"]:
            return face_result
        
        # All checks passed
        return {
            "valid": True,
            "message": "Profile image meets all requirements",
            "details": {
                "blur": blur_result,
                "background": background_result,
                "face": face_result
            }
        }
    
    def _check_image_blur(self, image):
        """Check if an image is blurry using Laplacian variance"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return {
            "is_blurry": laplacian_var < self.blur_threshold,
            "laplacian_variance": laplacian_var,
            "threshold": self.blur_threshold
        }
    
    def _check_background(self, image):
        """Check if image has a plain, uniform background"""
        # Sample background from edges
        h, w = image.shape[:2]
        
        # Sample points from edges
        edge_points = [
            (0, 0),                # Top-left
            (w-1, 0),              # Top-right
            (0, h-1),              # Bottom-left
            (w-1, h-1),            # Bottom-right
            (w//2, 0),             # Top-middle
            (w//2, h-1),           # Bottom-middle
            (0, h//2),             # Left-middle
            (w-1, h//2)            # Right-middle
        ]
        
        # Get background color samples
        bg_colors = []
        for x, y in edge_points:
            bg_colors.append(image[y, x])
        
        # Calculate average background color
        avg_bg = np.mean(bg_colors, axis=0)
        
        # Count pixels that differ significantly from background
        non_bg_pixels = 0
        total_pixels = h * w
        
        # Sample a subset of pixels for efficiency
        sample_step = max(1, min(h, w) // 100)
        
        for y in range(0, h, sample_step):
            for x in range(0, w, sample_step):
                pixel = image[y, x]
                color_diff = np.sqrt(np.sum((pixel - avg_bg) ** 2))
                if color_diff > self.background_threshold:
                    non_bg_pixels += 1
        
        # Adjust for sampling
        sampled_pixels = (h // sample_step) * (w // sample_step)
        non_bg_percentage = (non_bg_pixels / sampled_pixels) * 100
        
        # Check if background is light colored
        is_light_bg = (
            avg_bg[0] > 200 and 
            avg_bg[1] > 200 and 
            avg_bg[2] > 200
        )
        
        return {
            "is_plain_background": non_bg_percentage < 30,
            "is_light_background": is_light_bg,
            "background_percentage": 100 - non_bg_percentage,
            "avg_background": avg_bg.tolist()
        }
    
    def _validate_face(self, image):
        """Detect and validate face in the image using Haar cascade"""
        height, width = image.shape[:2]
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with multiple scale factors for better accuracy
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Check if face is detected
        if len(faces) == 0:
            # Try with different parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces) == 0:
                return {"valid": False, "error": "No face detected in the image"}
        
        # Check if multiple faces are detected
        if len(faces) > 1:
            return {
                "valid": False, 
                "error": "Multiple faces detected. Only one face should be in the ID photo",
                "face_count": len(faces)
            }
        
        # Get the detected face
        x, y, w, h = faces[0]
        
        # Calculate face size ratio
        face_area = w * h
        image_area = width * height
        face_ratio = face_area / image_area
        
        # Check if face is too small
        if face_ratio < self.min_face_size:
            return {
                "valid": False,
                "error": f"Face is too small in the image. It should take up at least {int(self.min_face_size * 100)}% of the image.",
                "face_ratio": face_ratio
            }
        
        # Check if face is too large
        if face_ratio > self.max_face_size:
            return {
                "valid": False,
                "error": f"Face is too large in the image. It should take up no more than {int(self.max_face_size * 100)}% of the image.",
                "face_ratio": face_ratio
            }
        
        # Check face position (should be centered)
        face_center_x = x + w / 2
        face_center_y = y + h / 2
        image_center_x = width / 2
        image_center_y = height / 2
        
        horizontal_offset = abs(face_center_x - image_center_x) / width
        vertical_offset = abs(face_center_y - image_center_y) / height
        
        if horizontal_offset > self.position_tolerance or vertical_offset > self.position_tolerance:
            return {
                "valid": False,
                "error": "Face is not properly centered in the image",
                "horizontal_offset": horizontal_offset,
                "vertical_offset": vertical_offset
            }
        
        # Check for eyes to ensure face is properly visible
        face_roi = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi)
        
        if len(eyes) < 2:
            return {
                "valid": False,
                "error": "Eyes are not clearly visible. Please ensure face is not tilted and eyes are open."
            }
        
        # Check face symmetry as a proxy for rotation
        # Extract left and right halves of the face
        face_img = gray[y:y+h, x:x+w]
        mid_x = w // 2
        left_half = face_img[:, :mid_x]
        right_half = face_img[:, mid_x:]
        
        # Flip right half for comparison
        right_half_flipped = cv2.flip(right_half, 1)
        
        # Resize for comparison if needed
        if left_half.shape[1] != right_half_flipped.shape[1]:
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
        
        # Calculate symmetry score
        if left_half.size > 0 and left_half.shape == right_half_flipped.shape:
            diff = cv2.absdiff(left_half, right_half_flipped)
            symmetry_score = np.mean(diff) / 255.0
            
            # If asymmetry is high, face might be rotated
            if symmetry_score > 0.25:  # Threshold for asymmetry
                return {
                    "valid": False,
                    "error": "Face appears to be tilted or rotated. Please keep your head straight.",
                    "symmetry_score": symmetry_score
                }
        
        # All face checks passed
        return {
            "valid": True,
            "face_ratio": face_ratio,
            "horizontal_offset": horizontal_offset,
            "vertical_offset": vertical_offset,
            "eyes_detected": len(eyes)
        }

# Helper function to process and save a valid profile picture
def process_profile_picture(image_buffer, output_path, student_id):
    """
    Process a validated profile picture:
    1. Resize to standard dimensions
    2. Ensure proper format
    3. Save with standardized naming
    
    Returns the filename of the processed image
    """
    try:
        # Open image from buffer
        image = Image.open(io.BytesIO(image_buffer))
        
        # Resize to standard dimensions (3:4 ratio, common for ID photos)
        target_width = 300
        target_height = 400
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Ensure directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Save with standardized naming
        filename = f"{student_id}_profile.jpg"
        filepath = os.path.join(output_path, filename)
        
        # Save as JPEG with good quality
        image.convert('RGB').save(filepath, 'JPEG', quality=95)
        
        return filename
    except Exception as e:
        print(f"Error processing profile picture: {str(e)}")
        return None

