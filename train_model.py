import os
import argparse
from trainable_validator import TrainablePhotoValidator

def main():
    parser = argparse.ArgumentParser(description='Train a photo validator model')
    parser.add_argument('--valid', required=True, help='Directory containing valid ID photos')
    parser.add_argument('--invalid', required=True, help='Directory containing invalid ID photos')
    parser.add_argument('--output', default='photo_validator_model.joblib', help='Output path for the trained model')
    args = parser.parse_args()
    
    # Check if directories exist
    if not os.path.isdir(args.valid):
        print(f"Error: Valid photos directory not found: {args.valid}")
        return
        
    if not os.path.isdir(args.invalid):
        print(f"Error: Invalid photos directory not found: {args.invalid}")
        return
    
    # Create and train the validator
    validator = TrainablePhotoValidator()
    validator.train(args.valid, args.invalid, args.output)
    
    print(f"\nTraining complete! Model saved to {args.output}")
    print("\nYou can now use this model to validate new photos.")

if __name__ == "__main__":
    main()

