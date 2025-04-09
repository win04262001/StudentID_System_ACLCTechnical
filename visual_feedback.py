import cv2
import numpy as np
import os
import argparse
from face_validation import FaceValidator

def visualize_validation(image_path, output_path=None):
    """
    Create a visual representation of validation results to help users understand
    why their photo passed or failed validation.
    """
    # Initialize validator
    validator = FaceValidator()
    
    # Validate image
    result = validator.validate_from_file(image_path)
    
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
    header_text = "✓ VALID: Photo meets all requirements" if result["valid"] else "✗ INVALID: " + result["error"]
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
        # Blur check
        if "blur" in result["details"]:
            blur = result["details"]["blur"]
            blur_text = f"Blur check: {'FAILED' if blur['is_blurry'] else 'PASSED'} - Sharpness score: {blur['laplacian_variance']:.1f}/{blur['threshold']}"
            blur_color = (0, 0, 150) if blur["is_blurry"] else (0, 150, 0)
            cv2.putText(canvas, blur_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, blur_color, 1)
            y_pos += line_height
        
        # Background check
        if "background" in result["details"]:
            bg = result["details"]["background"]
            bg_text = f"Background check: {'FAILED' if not bg['is_plain_background'] else 'PASSED'} - Uniformity: {bg['background_percentage']:.1f}%"
            bg_color = (0, 0, 150) if not bg["is_plain_background"] else (0, 150, 0)
            cv2.putText(canvas, bg_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bg_color, 1)
            y_pos += line_height
            
            bg_light_text = f"Background color: {'FAILED' if not bg['is_light_background'] else 'PASSED'} - Should be white/light"
            bg_light_color = (0, 0, 150) if not bg["is_light_background"] else (0, 150, 0)
            cv2.putText(canvas, bg_light_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bg_light_color, 1)
            y_pos += line_height
        
        # Face check
        if "face" in result["details"]:
            face = result["details"]["face"]
            if not isinstance(face, dict) or not face.get("valid", True):
                face_text = f"Face check: FAILED - {face.get('error', 'Face validation failed') if isinstance(face, dict) else 'Face validation failed'}"
                cv2.putText(canvas, face_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 150), 1)
            else:
                face_text = f"Face check: PASSED - Face properly detected and positioned"
                cv2.putText(canvas, face_text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 1)
            y_pos += line_height
            
            # Add face details if available
            if isinstance(face, dict) and "face_ratio" in face:
                ratio_text = f"Face size: {face['face_ratio']*100:.1f}% of image (should be between {validator.min_face_size*100:.1f}% and {validator.max_face_size*100:.1f}%)"
                ratio_color = (0, 150, 0)
                if face["face_ratio"] < validator.min_face_size or face["face_ratio"] > validator.max_face_size:
                    ratio_color = (0, 0, 150)
                cv2.putText(canvas, ratio_text, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ratio_color, 1)
                y_pos += line_height
            
            if isinstance(face, dict) and "horizontal_offset" in face and "vertical_offset" in face:
                pos_text = f"Face position: {face['horizontal_offset']*100:.1f}% horizontal, {face['vertical_offset']*100:.1f}% vertical offset"
                pos_color = (0, 150, 0)
                if face["horizontal_offset"] > validator.position_tolerance or face["vertical_offset"] > validator.position_tolerance:
                    pos_color = (0, 0, 150)
                cv2.putText(canvas, pos_text, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, pos_color, 1)
                y_pos += line_height
    
    # Add guidelines for improvement
    y_pos += 20
    cv2.putText(canvas, "Guidelines for a valid ID photo:", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
    y_pos += line_height
    
    guidelines = [
        "- Use a high-resolution camera (minimum 300x300 pixels)",
        "- Ensure good lighting with no shadows on face",
        "- Use a plain white or light-colored background",
        "- Look directly at the camera with a neutral expression",
        "- Keep your head straight (not tilted)",
        "- Ensure your face is centered and takes up 10-70% of the image"
    ]
    
    for guideline in guidelines:
        cv2.putText(canvas, guideline, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
        y_pos += line_height
    
    # Draw face detection if available
    if not result.get("valid", False) and "details" in result and "face" in result["details"]:
        # Try to detect face for visualization
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
    parser = argparse.ArgumentParser(description='Visualize face validation results')
    parser.add_argument('image_path', help='Path to the image file to validate')
    parser.add_argument('--output', '-o', help='Path to save the visualization (optional)')
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return
    
    visualize_validation(args.image_path, args.output)

if __name__ == "__main__":
    main()

