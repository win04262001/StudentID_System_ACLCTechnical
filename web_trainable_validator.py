from flask import Flask, request, render_template, jsonify, send_file
import os
import cv2
import numpy as np
import io
from PIL import Image
from trainable_validator import TrainablePhotoValidator
from test_trainable_validator import visualize_validation

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to the trained model
MODEL_PATH = 'photo_validator_model.joblib'

# Create validator instance
if os.path.exists(MODEL_PATH):
    validator = TrainablePhotoValidator(model_path=MODEL_PATH)
    print(f"Loaded model from {MODEL_PATH}")
else:
    validator = None
    print(f"Warning: Model file {MODEL_PATH} not found. Please train a model first.")

@app.route('/')
def index():
    return render_template('trainable_validator.html', model_loaded=validator is not None)

@app.route('/validate', methods=['POST'])
def validate():
    if validator is None:
        return jsonify({'valid': False, 'error': 'No trained model available. Please train a model first.'})
    
    if 'photo' not in request.files:
        return jsonify({'valid': False, 'error': 'No file uploaded'})
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'No file selected'})
    
    # Save the uploaded file
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
    file.save(filename)
    
    # Validate the image
    result = validator.validate(image_path=filename)
    
    # Create visualization
    vis_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'validation_result.jpg')
    visualize_validation(validator, filename, vis_filename)
    
    # Add visualization URL to result
    result['visualization_url'] = '/visualization'
    
    # Convert numpy arrays and other non-serializable objects to serializable types
    result = make_json_serializable(result)
    
    return jsonify(result)

@app.route('/train', methods=['POST'])
def train():
    if 'valid_photos' not in request.files or 'invalid_photos' not in request.files:
        return jsonify({'success': False, 'error': 'Both valid and invalid photos must be provided'})
    
    valid_photos = request.files.getlist('valid_photos')
    invalid_photos = request.files.getlist('invalid_photos')
    
    if not valid_photos or not invalid_photos:
        return jsonify({'success': False, 'error': 'Both valid and invalid photos must be provided'})
    
    # Create directories for training data
    valid_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'valid')
    invalid_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'invalid')
    
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)
    
    # Save valid photos
    for file in valid_photos:
        if file.filename:
            file.save(os.path.join(valid_dir, file.filename))
    
    # Save invalid photos
    for file in invalid_photos:
        if file.filename:
            file.save(os.path.join(invalid_dir, file.filename))
    
    # Create and train the validator
    global validator
    validator = TrainablePhotoValidator()
    validator.train(valid_dir, invalid_dir, MODEL_PATH)
    
    return jsonify({'success': True, 'message': 'Model trained successfully'})

@app.route('/visualization')
def get_visualization():
    vis_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'validation_result.jpg')
    return send_file(vis_filename, mimetype='image/jpeg')

def make_json_serializable(obj):
    """Convert a dictionary with potentially non-serializable values to a JSON-serializable dict"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, (bool, int, float, str)) or obj is None:
        return obj
    else:
        return str(obj)  # Convert any other types to strings

if __name__ == '__main__':
    app.run(debug=True)

