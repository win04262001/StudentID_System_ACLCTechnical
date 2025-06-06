from PIL import Image, ImageOps
import io
import os
import cv2
import numpy as np

def fix_signature_processing(signature_path, width=80, height=40):
    """
    Enhanced signature processing for Excel export
    Handles transparency and ensures proper contrast
    """
    try:
        # Open the signature image
        with Image.open(signature_path) as img:
            print(f"Original image mode: {img.mode}")
            print(f"Original image size: {img.size}")
            
            # Convert RGBA to RGB with white background for signatures
            if img.mode in ('RGBA', 'LA'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode == 'P':
                img = img.convert('RGB')
            elif img.mode == 'L':
                img = img.convert('RGB')
            
            # For signatures, enhance contrast to make them more visible
            img_array = np.array(img)
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply threshold to make signature more prominent
            _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            
            # Convert back to RGB
            signature_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
            
            # Invert so signature is black on white
            signature_rgb = 255 - signature_rgb
            
            # Convert back to PIL Image
            processed_img = Image.fromarray(signature_rgb)
            
            # Resize maintaining aspect ratio
            processed_img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Create final image with white background
            final_img = Image.new('RGB', (width, height), 'white')
            
            # Center the signature
            x = (width - processed_img.width) // 2
            y = (height - processed_img.height) // 2
            final_img.paste(processed_img, (x, y))
            
            return final_img
            
    except Exception as e:
        print(f"Error processing signature {signature_path}: {e}")
        return None

# Test the function with a sample signature
def test_signature_fix():
    # Test with existing signature files
    signature_files = [
        "static/uploads/21000602400_signature.png",
        "static/uploads/12000602400_signature.png",
        "static/uploads/21000607071_signature.png"
    ]
    
    for sig_file in signature_files:
        if os.path.exists(sig_file):
            print(f"\nTesting {sig_file}:")
            fixed_img = fix_signature_processing(sig_file)
            if fixed_img:
                # Save test output
                output_path = f"test_fixed_{os.path.basename(sig_file)}"
                fixed_img.save(output_path)
                print(f"✅ Fixed signature saved as {output_path}")
            else:
                print(f"❌ Failed to process {sig_file}")

# Run the test
test_signature_fix()
