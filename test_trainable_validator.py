import os
import argparse
import cv2
import numpy as np
from trainable_validator import TrainablePhotoValidator

def visualize_validation(validator, image_path, output_path=None):
    """
    Create a visual representation of validation results
    """
    # Validate image
    result = validator.validate(image_path=image_path)
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return
    
    # Create a visualization canvas
    height, width = image.shape[:2]
    canvas_width = max(width, 500)
    canvas_height = height + 300  # Extra space for feedback
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    
    # Add image to canvas
    y_offset = 10
    x_offset = (canvas_width - width) // 2
    canvas[y_offset:y_offset+height, x_offset:x_offset+width] = image
    
    # Add colored border based on validation result
    border_color = (0, 255, 0) if result["valid"] else (0, 0, 255)  # Green for valid, Red for invalid
    cv2.rectangle(
        canvas,
        (x_offset-5, y_offset-5),
        (x_offset+width+5, y_offset+height+5),
        border_color,
        3
    )
    
    # Add validation result header
    header_y = y_offset + height + 40
    confidence_text = f" (Confidence: {result['confidence']*100:.1f}%)" if "confidence" in result else ""
    header_text = f"✓ VALID{confidence_text}" if result["valid"] else f"✗ INVALID: {result.get('error', 'Not valid')}{confidence_text}"
    header_color = (0, 150, 0) if result["valid"] else (0, 0, 150)
    
    cv2.putText(
        canvas,
        header_text,
        (20, header_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        header_color,
        2
    )
    
    # Add detailed feedback
    y_pos = header_y + 40
    line_height = 30
    
    if "details" in result:
        details = result["details"]
        
        # Resolution
        if "resolution" in details:
            res_text = f"Resolution: {details['resolution']}"
            cv2.putText(canvas, res_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
            y_pos += line_height
        
        # Blur level
        if "blur_level" in details:
            blur_text = f"Blur level: {details['blur_level']:.1f}"
            blur_color = (0, 0, 150) if details['blur_level'] < 50 else (0, 150, 0)
            cv2.putText(canvas, blur_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, blur_color, 1)
            y_pos += line_height
        
        # Background
        if "background" in details:
            bg = details["background"]
            bg_text = f"Background uniformity: {bg['uniformity']:.1f}%"
            bg_color = (0, 0, 150) if bg['uniformity'] < 50 else (0, 150, 0)
            cv2.putText(canvas, bg_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bg_color, 1)
            y_pos += line_height
            
            bg_light_text = f"Background brightness: {bg['brightness']:.1f}"
            bg_light_color = (0, 0, 150) if bg['brightness'] < 180 else (0, 150, 0)
            cv2.putText(canvas, bg_light_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bg_light_color, 1)
            y_pos += line_height
        
        # Face
        if "face" in details:
            face = details["face"]
            face_text = f"Face detected: {'Yes' if face['detected'] else 'No'}"
            face_color = (0, 150, 0) if face['detected'] else (0, 0, 150)
            cv2.putText(canvas, face_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, face_color, 1)
            y_pos += line_height
            
            if face['detected']:
                ratio_text = f"Face size: {face['size_ratio']:.1f}% of image"
                ratio_color = (0, 150, 0) if 5 < face['size_ratio'] < 80 else (0, 0, 150)
                cv2.putText(canvas, ratio_text, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ratio_color, 1)
                y_pos += line_height
                
                center_text = f"Face centered: {'Yes' if face['centered'] else 'No'}"
                center_color = (0, 150, 0) if face['centered'] else (0, 0, 150)
                cv2.putText(canvas, center_text, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, center_color, 1)
                y_pos += line_height
                
                eyes_text = f"Eyes detected: {face['eyes_detected']}"
                eyes_color = (0, 150, 0) if face['eyes_detected'] >= 2 else (0, 0, 150)
                cv2.putText(canvas, eyes_text, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, eyes_color, 1)
                y_pos += line_height
    
    # Draw face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            # Draw rectangle on the original image position in canvas
            cv2.rectangle(
                canvas,
                (x_offset + x, y_offset + y),
                (x_offset + x + w, y_offset + y + h),
                (255, 0, 0),
                2
            )
    
    # Save or display the result
    if output_path:
        cv2.imwrite(output_path, canvas)
        print(f"Validation visualization saved to: {output_path}")
    else:
        cv2.imshow("Validation Result", canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Test the trainable photo validator')
    parser.add_argument('--model', required=True, help='Path to the trained model file')
    parser.add_argument('--image', required=True, help='Path to the image to validate')
    parser.add_argument('--output', help='Path to save the visualization (optional)')
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.isfile(args.model):
        print(f"Error: Model file not found: {args.model}")
        return
        
    if not os.path.isfile(args.image):
        print(f"Error: Image file not found: {args.image}")
        return
    
    # Load the validator with the trained model
    validator = TrainablePhotoValidator(model_path=args.model)
    
    # Validate and visualize
    visualize_validation(validator, args.image, args.output)

if __name__ == "__main__":
    main()

