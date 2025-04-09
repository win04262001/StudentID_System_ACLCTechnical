from flask import Flask, request, render_template, jsonify, send_file
import os
import cv2
import numpy as np
import io
import json
from PIL import Image
from face_validation import FaceValidator
from visual_feedback import visualize_validation

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create validator instance
validator = FaceValidator()

@app.route('/')
def index():
    return render_template('validator.html')

@app.route('/validate', methods=['POST'])
def validate():
    if 'photo' not in request.files:
        return jsonify({'valid': False, 'error': 'No file uploaded'})
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'No file selected'})
    
    # Save the uploaded file
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
    file.save(filename)
    
    # Validate the image
    result = validator.validate_from_file(filename)
    
    # Create visualization
    vis_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'validation_result.jpg')
    visualize_validation(filename, vis_filename)
    
    # Add visualization URL to result
    result['visualization_url'] = '/visualization'
    
    # Convert numpy arrays and other non-serializable objects to serializable types
    result = make_json_serializable(result)
    
    return jsonify(result)

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

@app.route('/visualization')
def get_visualization():
    vis_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'validation_result.jpg')
    return send_file(vis_filename, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)

