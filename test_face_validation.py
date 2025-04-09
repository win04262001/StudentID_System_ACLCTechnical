import os
import argparse
from face_validation import FaceValidator

def test_directory(directory_path):
    """Test all images in a directory"""
    validator = FaceValidator()
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return
    
    print(f"Testing all images in: {directory_path}")
    print("-" * 50)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = [
        os.path.join(directory_path, f) for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f)) and 
        os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    if not image_files:
        print("No image files found in the directory.")
        return
    
    # Test each image
    results = {
        "valid": 0,
        "invalid": 0,
        "errors": {}
    }
    
    for image_path in image_files:
        print(f"Testing: {os.path.basename(image_path)}")
        result = validator.validate_from_file(image_path)
        
        if result["valid"]:
            print("  ✅ VALID")
            results["valid"] += 1
        else:
            print(f"  ❌ INVALID: {result['error']}")
            results["invalid"] += 1
            
            # Track error types
            error_type = result["error"]
            if error_type in results["errors"]:
                results["errors"][error_type] += 1
            else:
                results["errors"][error_type] = 1
        
        print()
    
    # Print summary
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total images tested: {len(image_files)}")
    print(f"Valid images: {results['valid']} ({results['valid']/len(image_files)*100:.1f}%)")
    print(f"Invalid images: {results['invalid']} ({results['invalid']/len(image_files)*100:.1f}%)")
    
    if results["errors"]:
        print("\nError breakdown:")
        for error_type, count in results["errors"].items():
            print(f"- {error_type}: {count} ({count/results['invalid']*100:.1f}% of errors)")

def main():
    parser = argparse.ArgumentParser(description='Test face validation on a directory of images')
    parser.add_argument('directory', help='Path to directory containing test images')
    args = parser.parse_args()
    
    test_directory(args.directory)

if __name__ == "__main__":
    main()

