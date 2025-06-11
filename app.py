from binascii import Error
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import mysql.connector
from functools import wraps
from werkzeug.utils import secure_filename
import os
from barcode import Code39, get_barcode_class
from barcode.writer import ImageWriter
from flask import send_from_directory
import cv2
import numpy as np
import easyocr
import base64
import re
from PIL import Image, ImageOps
import io
from markupsafe import Markup
import random
import time
from math import ceil
import pandas as pd


# Import the OpenCV-based face validation module
from face_validation import FaceValidator

# Import the trainable validator
from trainable_validator import TrainablePhotoValidator
from datetime import datetime

#for email sending
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os


# Import necessary libraries for file handling and Excel generation
import zipfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.utils.dataframe import dataframe_to_rows
from PIL import Image as PILImage
import base64
import uuid


import tempfile
from flask import Response, stream_template
import shutil
from werkzeug.wsgi import FileWrapper


from collections import defaultdict
import sqlite3


#------------------------------------------------------------------------------------
# Define Flask App
# Purpose: Initialize the Flask application with configuration settings
# This is the main entry point of the web application
app = Flask(__name__, static_folder="static")
app.secret_key = "123"  # Used for session encryption and security
app.permanent_session_lifetime = timedelta(hours=2)  # Sets how long a user session lasts


#-----------------------------------------------------------------------------------# Configure Flask-Mail for sending emails
# Purpose: Set up email configuration for sending notifications

# Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aclc.id.system@gmail.com'  # your Gmail
app.config['MAIL_PASSWORD'] = 'jikt daqr xvur rwdt'        # the app password
app.config['MAIL_DEFAULT_SENDER'] = ('Technical Support Department', 'aclc.id.system@gmail.com')
app.config['SECRET_KEY'] = '123'


mail = Mail(app)

# Token serializer
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

#-----------------------------------------------------------------------------------

# Purpose: Create a custom template filter to convert newlines to HTML line breaks
# This helps with displaying multi-line text properly in HTML templates
@app.template_filter('nl2br')
def nl2br_filter(s):
  if s is None:
      return ''
  return Markup(s.replace('\n', '<br>'))

#-----------------------------------------------------------------------------------

# Configure File Uploads
# Purpose: Set up file upload configuration for profile pictures and signatures
# This defines where uploaded files will be stored and what file types are allowed
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Create upload directory if it doesn't exist

#-----------------------------------------------------------------------------------

# Create directories for training data
# Purpose: Set up directories for storing training data for the photo validator model
# These directories will store valid and invalid photos for machine learning training
TRAINING_FOLDER = "training"
VALID_PHOTOS_DIR = os.path.join(TRAINING_FOLDER, "valid")
INVALID_PHOTOS_DIR = os.path.join(TRAINING_FOLDER, "invalid")
MODEL_PATH = os.path.join(TRAINING_FOLDER, "photo_validator_model.joblib")

os.makedirs(VALID_PHOTOS_DIR, exist_ok=True)
os.makedirs(INVALID_PHOTOS_DIR, exist_ok=True)

#-----------------------------------------------------------------------------------

# Initialize the trainable validator
# Purpose: Load or create the machine learning model for photo validation
# This model will be used to automatically validate student profile pictures
try:
    if os.path.exists(MODEL_PATH):
        photo_validator = TrainablePhotoValidator(model_path=MODEL_PATH)
        print(f"Loaded photo validator model from {MODEL_PATH}")
    else:
        photo_validator = TrainablePhotoValidator()
        print("No pre-trained model found. Using basic validation.")
except Exception as e:
    print(f"Error initializing photo validator: {str(e)}")
    photo_validator = None

#-----------------------------------------------------------------------------------

# Database Configuration
# Purpose: Define database connection parameters
# This configuration is used to connect to the MySQL database
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "studentid"
}

# Database Connection
# Purpose: Create a function to establish database connections
# This function is used throughout the application whenever database access is needed
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

#-----------------------------------------------------------------------------------

# Authentication Middleware
# Purpose: Create a decorator to protect routes that require authentication
# This ensures only logged-in users with appropriate roles can access certain pages
def login_required(role="student"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in first.", "danger")
                return redirect(url_for('login'))
            if role == "admin" and session.get('user_role') != "admin":
                flash("Access denied.", "danger")
                return redirect(url_for('home'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Load EasyOCR model once to avoid reloading every request
# Purpose: Initialize the OCR engine for text recognition in images
# Loading this once improves performance as it's a resource-intensive operation
reader = easyocr.Reader(['en'], gpu=False)




#----------------------------------------------------------------VALIDATION PROCESS SIDE-----------------------------------------------------------------------------------------------

# # Check if an image is blurry
# # Purpose: Determine if an uploaded image is too blurry to be acceptable
# # Used during profile picture validation to ensure image quality
# def is_blurry(image, threshold=80):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
#     return laplacian_var < threshold

# # Check if a face is detected using OpenCV's Haar cascade
# # Purpose: Verify that a profile picture contains a face
# # This ensures that profile pictures actually show the student's face
# def is_face_detected(image_path):
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#     return len(faces) > 0

# # Check if the background is plain using edge detection
# # Purpose: Verify that a profile picture has a plain background
# # This ensures professional-looking ID photos with minimal distractions
# def is_plain_background(image_path, edge_threshold=5000):
#     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     edges = cv2.Canny(image, 50, 150)
#     return np.count_nonzero(edges) < edge_threshold

# # Check if a signature is valid using OCR
# # Purpose: Validate that an uploaded signature meets quality requirements
# # This ensures signatures are clear and properly formed
# def is_signature_valid(image_path):
#     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
#     white_pixels = np.count_nonzero(binary)
#     return 1000 < white_pixels < 20000  # Adjust values if necessary

# Process Electronic Signature
# Purpose: Process and enhance electronic signatures drawn on a canvas
# This function converts base64 data to an image, removes background, enhances contrast, and saves the signature
def process_esignature(base64_data, student_id):
    """
    Process electronic signature from canvas:
    1. Convert base64 to image
    2. Remove background
    3. Enhance signature visibility
    4. Save as transparent PNG
    """
    try:
        import base64, re, io
        from PIL import Image
        import numpy as np
        import cv2
        import os

        # Remove base64 prefix if present
        base64_data = re.sub(r'^data:image/[^;]+;base64,', '', base64_data)

        # Decode base64 → binary → PIL image
        img_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")

        # Convert to OpenCV format
        img_array = np.array(img)
        bgr = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGBA2RGB)
        alpha = img_array[:, :, 3]

        # If no alpha, generate it from brightness
        if alpha is None or np.max(alpha) == 0:
            gray = cv2.cvtColor(bgr, cv2.COLOR_RGB2GRAY)
            _, alpha = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

        # Enhance and smooth alpha mask
        enhanced_alpha = cv2.equalizeHist(alpha)
        enhanced_alpha = cv2.GaussianBlur(enhanced_alpha, (3, 3), 0)

        # Merge BGR + updated alpha → RGBA
        result_rgba = cv2.merge([bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2], enhanced_alpha])

        # Save image using PIL
        result_img = Image.fromarray(result_rgba, 'RGBA')
        filename = f"{student_id}_signature.png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        result_img.save(filepath)

        return filename

    except Exception as e:
        print(f"❌ Error processing signature: {str(e)}")
        return None


# Create a global instance of the validator
# Purpose: Initialize the face validator for use throughout the application
face_validator = FaceValidator()




def generate_barcode(usn):
    """Generate a Code39 barcode PNG from the student's USN"""
    barcode_dir = os.path.join("static", "barcodes")
    os.makedirs(barcode_dir, exist_ok=True)

    barcode_filename = f"{usn}.png"
    barcode_path = os.path.join(barcode_dir, barcode_filename)

    # Generate the barcode
    code39 = Code39(usn, writer=ImageWriter(), add_checksum=False)
    code39.save(os.path.splitext(barcode_path)[0])  # remove .png from filename

    return barcode_filename


# Helper function to get semester start date
def get_semester_start_date(academic_year, semester):
    if not academic_year or '-' not in academic_year:
        return datetime.now()
        
    start_year = int(academic_year.split('-')[0])
    
    if semester == 1:  # First semester starts in June
        return datetime(start_year, 6, 1)
    else:  # Second semester starts in January of the next year
        return datetime(start_year + 1, 1, 1)

# Calculate status for a student record
def calculate_student_status(student):
    if student['received_date']:
        received_date = student['received_date']
        semester_start = get_semester_start_date(student['academic_year'], student['semester'])
        
        # If received date is within 16 weeks of semester start, it's "New", otherwise "Old"
        sixteen_weeks = timedelta(weeks=16)
        return "New" if received_date <= (semester_start + sixteen_weeks) else "Old"
    else:
        return "New"  # Default to New if no date
    

# Test Email Route

@app.route('/test-email')
def test_email():
    msg = Message("Baho kag tae zar",
                  recipients=['zarwin.villaro@aclcbutuan.edu.ph'])
    msg.body = "This is a test email sent from Flask using Brevo SMTP."
    try:
        mail.send(msg)
        return "✅ Test email sent!"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"


#-----------------------------------------------------------------------------------


def get_full_name(student_record):
    """
    Get full name from student record, supporting both old and new formats
    
    Args:
        student_record: Dictionary containing student data
        
    Returns:
        str: Full name of the student
    """
    # Check if we have separate name fields
    if student_record.get('first_name') or student_record.get('last_name'):
        parts = []
        
        if student_record.get('first_name'):
            parts.append(student_record['first_name'])
        
        if student_record.get('middle_name'):
            parts.append(student_record['middle_name'])
        
        if student_record.get('last_name'):
            parts.append(student_record['last_name'])
        
        return ' '.join(parts) if parts else student_record.get('name', '')
    
    # Fallback to original name field
    return student_record.get('name', '')

def parse_name_input(full_name_input):
    """
    Parse name input from forms into separate components
    
    Args:
        full_name_input: Full name string from form input
        
    Returns:
        dict: Dictionary with first_name, middle_name, last_name
    """
    if not full_name_input or not full_name_input.strip():
        return {'first_name': '', 'middle_name': None, 'last_name': ''}
    
    import re
    name = re.sub(r'\s+', ' ', full_name_input.strip())
    parts = name.split()
    
    if len(parts) == 1:
        return {'first_name': parts[0], 'middle_name': None, 'last_name': ''}
    elif len(parts) == 2:
        return {'first_name': parts[0], 'middle_name': None, 'last_name': parts[1]}
    elif len(parts) == 3:
        return {'first_name': parts[0], 'middle_name': parts[1], 'last_name': parts[2]}
    else:
        return {
            'first_name': parts[0], 
            'middle_name': ' '.join(parts[1:-1]), 
            'last_name': parts[-1]
        }

def update_student_with_names(cursor, student_id, name_data, **other_fields):
    """
    Update student record with name data, supporting both formats
    
    Args:
        cursor: Database cursor
        student_id: Student ID
        name_data: Dictionary with name information or full name string
        **other_fields: Other fields to update
    """
    # Prepare the update query
    update_fields = []
    update_values = []
    
    # Handle name fields
    if isinstance(name_data, dict) and ('first_name' in name_data or 'last_name' in name_data):
        # New format with separate fields
        update_fields.extend(['first_name = %s', 'middle_name = %s', 'last_name = %s'])
        update_values.extend([
            name_data.get('first_name', ''),
            name_data.get('middle_name'),
            name_data.get('last_name', '')
        ])
        
        # Also update the full name field for backward compatibility
        full_name = get_full_name(name_data)
        update_fields.append('name = %s')
        update_values.append(full_name)
    else:
        # Old format - just update name field and parse into components
        full_name = str(name_data) if name_data else ''
        parsed = parse_name_input(full_name)
        
        update_fields.extend(['name = %s', 'first_name = %s', 'middle_name = %s', 'last_name = %s'])
        update_values.extend([
            full_name,
            parsed['first_name'],
            parsed['middle_name'],
            parsed['last_name']
        ])
    
    # Add other fields
    for field, value in other_fields.items():
        update_fields.append(f'{field} = %s')
        update_values.append(value)
    
    # Add student_id for WHERE clause
    update_values.append(student_id)
    
    # Execute update
    query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = %s"
    cursor.execute(query, update_values)

def insert_student_with_names(cursor, student_id, name_data, **other_fields):
    """
    Insert student record with name data, supporting both formats
    
    Args:
        cursor: Database cursor
        student_id: Student ID
        name_data: Dictionary with name information or full name string
        **other_fields: Other fields to insert
    """
    # Prepare the insert query
    fields = ['student_id']
    values = [student_id]
    
    # Handle name fields
    if isinstance(name_data, dict) and ('first_name' in name_data or 'last_name' in name_data):
        # New format with separate fields
        fields.extend(['first_name', 'middle_name', 'last_name'])
        values.extend([
            name_data.get('first_name', ''),
            name_data.get('middle_name'),
            name_data.get('last_name', '')
        ])
        
        # Also add the full name field for backward compatibility
        full_name = get_full_name(name_data)
        fields.append('name')
        values.append(full_name)
    else:
        # Old format - parse into components
        full_name = str(name_data) if name_data else ''
        parsed = parse_name_input(full_name)
        
        fields.extend(['name', 'first_name', 'middle_name', 'last_name'])
        values.extend([
            full_name,
            parsed['first_name'],
            parsed['middle_name'],
            parsed['last_name']
        ])
    
    # Add other fields
    for field, value in other_fields.items():
        fields.append(field)
        values.append(value)
    
    # Execute insert
    placeholders = ', '.join(['%s'] * len(values))
    query = f"INSERT INTO students ({', '.join(fields)}) VALUES ({placeholders})"
    cursor.execute(query, values)

print("✅ Helper functions for name handling added successfully!")



#-----------------------------------------------------------------------------------

# ✅ Validate Image (Profile & Signature) - UPDATED to use trainable validator
# Purpose: API endpoint to validate uploaded images (profile pictures and signatures)
# This route is called via AJAX when students upload images during application
@app.route('/validate_image/<image_type>', methods=['POST'])
def validate_image(image_type):
    if image_type not in ["profile", "signature"]:
        return jsonify({"valid": False, "error": "Invalid image type"}), 400

    file = request.files.get(image_type)
    if not file:
        return jsonify({"valid": False, "error": "No image uploaded"}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(image_path)

    if image_type == "profile":
        # Use ML validator if trained model exists
        if photo_validator and photo_validator.model:
            result = photo_validator.validate(image_path=image_path)
        else:
            result = face_validator.validate_from_file(image_path)

        return jsonify(make_json_serializable(result))

    elif image_type == "signature":
        # Optional: add simple pixel-based validation if needed
        return jsonify({"valid": True})

    return jsonify({"valid": False, "error": "Unhandled image type"}), 400


# Helper function to make objects JSON serializable
# Purpose: Convert complex Python objects to JSON-compatible format
# This is needed when returning validation results that contain numpy arrays or other non-serializable objects
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

#-----------------------------------------------------------------------------------

# ✅ Process and Save Electronic Signature
# Purpose: API endpoint to process and save signatures drawn on a canvas
# This route is called when a student draws a signature using the electronic signature pad
@app.route('/process_signature', methods=['POST'])
@login_required("student")
def process_signature():
    if 'student_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    try:
        data = request.get_json()
        signature_data = data.get('signature')
        student_id = session.get('student_id')

        if not signature_data:
            return jsonify({"success": False, "error": "No signature data provided"}), 400

        # ✅ Process signature (base64 to PNG)
        filename = process_esignature(signature_data, student_id)

        if not filename:
            return jsonify({"success": False, "error": "Failed to process signature"}), 500

        # ✅ Update the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET signature = %s WHERE student_id = %s", 
                       (filename, student_id))
        conn.commit()

        return jsonify({"success": True, "filename": filename})

    except Exception as e:
        print("❌ Signature Processing Error:", str(e))  # Debug log
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

        
        
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------


# ---------- User Authentication ----------
# Purpose: Handle student registration
# This route allows new students to create accounts in the system
@app.route('/register', methods=['GET', 'POST'])
def register():
    email_sent = False
    otp_verified = False
    entered_email = session.get('otp_email')

    if request.method == 'POST':
        form_stage = request.form.get('form_stage')

        # STEP 1: Email entered → Send OTP
        if form_stage == 'email_stage':
            email = request.form.get('email', '').strip().lower()
            entered_email = email

            if not email or not email.endswith('@aclcbutuan.edu.ph'):
                flash("⚠️ Please use your institutional email.", "danger")
            else:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                # Check if email already registered in users table
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("⚠️ Email is already registered. Please log in.", "warning")
                    return redirect(url_for('login'))

                # Check if email exists in the preloaded students table
                cursor.execute("SELECT student_id FROM students WHERE email = %s", (email,))
                student = cursor.fetchone()
                if not student:
                    flash("❌ Your email is not found in the official student records. Please contact the registrar.", "danger")
                else:
                    otp = str(random.randint(100000, 999999))
                    session['otp'] = otp
                    session['otp_email'] = email
                    session['otp_time'] = int(time.time())

                    msg = Message("Your ACLC OTP Code", recipients=[email])
                    msg.body = f"Your ACLC ID registration code is: {otp}"
                    mail.send(msg)

                    flash("✅ OTP sent to your email.", "success")
                    email_sent = True

                cursor.close()
                conn.close()

        # STEP 2: OTP entered → Verify
        elif form_stage == 'otp_stage':
            entered_email = session.get('otp_email')
            user_otp = request.form.get('otp')

            if request.form.get('resend_otp') == '1':
                otp = str(random.randint(100000, 999999))
                session['otp'] = otp
                session['otp_time'] = int(time.time())

                msg = Message("Your ACLC OTP Code (Resent)", recipients=[entered_email])
                msg.body = f"Your new ACLC ID registration code is: {otp}"
                mail.send(msg)

                flash("🔁 OTP resent to your email.", "info")
                return render_template("register.html", email_sent=True, otp_verified=False, email=entered_email)

            otp_valid = session.get('otp')
            otp_time = session.get('otp_time')
            current_time = int(time.time())

            if not user_otp or otp_valid != user_otp:
                flash("❌ Invalid OTP!", "danger")
                email_sent = True
            elif current_time - otp_time > 300:
                flash("❌ OTP has expired. Please request a new one.", "danger")
                session.pop('otp', None)
                session.pop('otp_time', None)
                email_sent = False
            else:
                otp_verified = True
                email_sent = True
                flash("✅ OTP verified. Set your password.", "success")

        # STEP 3: Password set → Create account with linked student_id
        elif form_stage == 'password_stage':
            email = session.get('otp_email')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

            if password != confirm:
                flash("❌ Passwords do not match!", "danger")
                otp_verified = True
                email_sent = True
            else:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                # Check again to be sure
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("⚠️ Email is already registered. Please log in.", "warning")
                    return redirect(url_for('login'))

                # Get the student_id from the student record
                cursor.execute("SELECT student_id FROM students WHERE email = %s", (email,))
                student = cursor.fetchone()

                if not student:
                    flash("❌ Student record not found. Contact registrar.", "danger")
                else:
                    student_id = student['student_id']
                    hashed_password = generate_password_hash(password)

                    try:
                        cursor.execute("""
                            INSERT INTO users (email, password, is_verified, role, student_id)
                            VALUES (%s, %s, TRUE, 'student', %s)
                        """, (email, hashed_password, student_id))
                        conn.commit()

                        session.pop('otp', None)
                        session.pop('otp_email', None)
                        session.pop('otp_time', None)

                        flash("✅ Account created! Please log in.", "success")
                        return redirect(url_for('login'))

                    except Error as e:
                        conn.rollback()
                        flash(f"❌ Database error: {str(e)}", "danger")
                    finally:
                        cursor.close()
                        conn.close()

    return render_template("register.html", email_sent=email_sent, otp_verified=otp_verified, email=entered_email)






@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except:
        flash("❌ Invalid or expired verification link.", "danger")
        return redirect(url_for('register'))

    return redirect(url_for('set_password', email=email))






# Purpose: Handle user login (both students and admins)
# This route authenticates users and redirects them to the appropriate dashboard
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Check email in users table
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            if not user['is_verified']:
                flash("⚠️ Please verify your email first.", "warning")
                return redirect(url_for('login'))

            session['user_id'] = user['id']
            session['user_role'] = user.get('role', 'student')
            session['user_email'] = user['email']

            # Get name from user record or construct from name fields
            user_name = get_full_name(user)
            session['user_name'] = user_name

            # ✅ Step 2: Check if student record exists
            cursor.execute("""
                SELECT student_id, application_status, first_name, middle_name, last_name, name 
                FROM students WHERE email = %s
            """, (email,))
            student = cursor.fetchone()

            if not student:
                flash("❌ Your email is not found in the registrar's student list. Please contact TSD.", "danger")
                return redirect(url_for('login'))

            # ✅ Set student_id and name in session
            session['student_id'] = student['student_id']
            session['student_name'] = get_full_name(student)

            # ✅ Step 3: Check application_status
            if student['application_status'] in ['pending', 'processing', 'done', 'receive']:
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('complete_student_profile'))

        else:
            flash("❌ Invalid email or password.", "danger")

        cursor.close()
        conn.close()

    return render_template("login.html")




    

@app.route('/usn_finder', methods=['GET', 'POST'])
@login_required("student")
def usn_finder():
    
    print("🔍 SESSION =", dict(session))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ If already linked → skip to dashboard
    cursor.execute("SELECT student_id FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user and user['student_id']:
        return redirect(url_for('student_dashboard'))

    # ✅ USN Submission
    if request.method == 'POST':
        usn = request.form.get('usn', '').strip()

        if not usn or len(usn) != 11 or not usn.isdigit():
            flash("❌ USN must be 11 digits.", "danger")
        else:
            # (Optional) check if USN exists in `students` table
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (usn,))
            if not cursor.fetchone():
                flash("❌ USN not found. Please contact the registrar.", "danger")
            else:
                cursor.execute("UPDATE users SET student_id = %s WHERE id = %s", (usn, user_id))
                conn.commit()
                session['student_id'] = usn
                flash("✅ USN linked successfully!", "success")
                return redirect(url_for('student_dashboard'))

    cursor.close()
    conn.close()
    return render_template("usn_finder.html")






# ---------- Home Page ----------
# Purpose: Display the main landing page of the application
# This is the first page users see when visiting the site
@app.route('/')
def home():
    return render_template("home.html")

# Purpose: Display information about the ID section
# This route provides general information about student IDs
@app.route('/ID_section')
def ID_section():
    return render_template("ID_section.html")





#----------------------------------------------------ADMIN SIDE---------------------------------------------------------------------------------------------------------

# NEW: Admin route to train the photo validator model
# Purpose: Allow admins to train the machine learning model for photo validation
# This route handles both displaying the training interface and processing training requests
@app.route('/admin/train_validator', methods=['GET', 'POST'])
@login_required("admin")
def train_validator():
    if request.method == 'POST':
        # Check if we have enough training data
        valid_count = len([f for f in os.listdir(VALID_PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        invalid_count = len([f for f in os.listdir(INVALID_PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        if valid_count < 5 or invalid_count < 5:
            flash("⚠️ Not enough training data. Need at least 5 valid and 5 invalid photos.", "warning")
            return redirect(url_for('train_validator'))
        
        # Train the model
        global photo_validator
        photo_validator = TrainablePhotoValidator()
        
        try:
            photo_validator.train(VALID_PHOTOS_DIR, INVALID_PHOTOS_DIR, MODEL_PATH)
            flash("✅ Model trained successfully!", "success")
        except Exception as e:
            flash(f"❌ Error training model: {str(e)}", "danger")
        
        return redirect(url_for('train_validator'))
    
    # Count training data
    valid_count = len([f for f in os.listdir(VALID_PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    invalid_count = len([f for f in os.listdir(INVALID_PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    # Check if model exists
    model_exists = os.path.exists(MODEL_PATH)
    
    return render_template(
        "train_validator.html", 
        valid_count=valid_count, 
        invalid_count=invalid_count,
        model_exists=model_exists
    )



# Fixed bulk import route - make sure this route exists and works
@app.route('/admin/bulk_import_students', methods=['POST'])
@login_required("admin")
def admin_bulk_import_students():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    try:
        # Handle different file types
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format. Please use CSV or Excel files.'})
        
        print(f"📊 File columns: {list(df.columns)}")
        print(f"📊 File shape: {df.shape}")
        
        # Validate required columns - FIXED
        required_columns = ['student_id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        # Check for name columns - either 'name' OR ('first_name' AND 'last_name')
        has_full_name = 'name' in df.columns
        has_separate_names = 'first_name' in df.columns and 'last_name' in df.columns
        
        if not (has_full_name or has_separate_names):
            missing_columns.append('name or first_name/last_name')
        
        if missing_columns:
            return jsonify({'success': False, 'error': f"Missing required columns: {', '.join(missing_columns)}"})
        
        # Process the data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            for index, row in df.iterrows():
                try:
                    # Validate required fields
                    if pd.isna(row['student_id']):
                        error_count += 1
                        errors.append(f"Row {index + 2}: Missing student_id")
                        continue
                    
                    student_id = str(row['student_id']).strip()
                    
                    # Determine name format and parse
                    if has_full_name and not pd.isna(row['name']):
                        # Using full name column - parse it
                        full_name = str(row['name']).strip()
                        parsed_names = parse_name_input(full_name)
                        first_name = parsed_names['first_name']
                        middle_name = parsed_names['middle_name']
                        last_name = parsed_names['last_name']
                    elif has_separate_names and not pd.isna(row['first_name']) and not pd.isna(row['last_name']):
                        # Using separate name columns
                        first_name = str(row['first_name']).strip()
                        middle_name = str(row['middle_name']).strip() if 'middle_name' in row and not pd.isna(row['middle_name']) else None
                        last_name = str(row['last_name']).strip()
                        # Construct full name
                        name_parts = [first_name]
                        if middle_name:
                            name_parts.append(middle_name)
                        name_parts.append(last_name)
                        full_name = ' '.join(name_parts)
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 2}: Missing name information")
                        continue
                    
                    # Get other fields
                    email = str(row['email']).strip().lower() if 'email' in row and not pd.isna(row['email']) else ''
                    course = str(row['course']) if 'course' in row and not pd.isna(row['course']) else ''
                    contact = str(row['contact']) if 'contact' in row and not pd.isna(row['contact']) else ''
                    guardian_name = str(row['guardian_name']) if 'guardian_name' in row and not pd.isna(row['guardian_name']) else ''
                    address = str(row['address']) if 'address' in row and not pd.isna(row['address']) else ''
                    
                    # Check for duplicate student_id
                    cursor.execute("SELECT 1 FROM students WHERE student_id = %s", (student_id,))
                    if cursor.fetchone():
                        error_count += 1
                        errors.append(f"Row {index + 2}: Student with ID {student_id} already exists")
                        continue
                    
                    # Insert student with explicit name fields
                    cursor.execute("""
                        INSERT INTO students (
                            student_id, name, first_name, middle_name, last_name,
                            email, course, contact, guardian_name, address
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        student_id, full_name, first_name, middle_name, last_name,
                        email, course, contact, guardian_name, address
                    ))
                    
                    success_count += 1
                    print(f"✅ Imported: {student_id} - {full_name} (First: {first_name}, Middle: {middle_name}, Last: {last_name})")
                    
                except Exception as row_error:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(row_error)}")
                    print(f"❌ Row error: {str(row_error)}")
            
            conn.commit()
            
            result = {
                'success': True,
                'imported': success_count,
                'errors': error_count,
                'total': len(df)
            }
            
            if errors:
                result['error_details'] = errors[:10]  # Limit to first 10 errors
            
            return jsonify(result)
            
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'})
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ File processing error: {str(e)}")
        return jsonify({'success': False, 'error': f'File processing error: {str(e)}'})




# Add this new route for admin import page
# Fixed manual import route
@app.route('/admin/import_students', methods=['GET', 'POST'])
@login_required("admin")
def admin_import_students():
    if request.method == 'POST':
        student_id = request.form.get("student_id", "").strip()
        
        # Check for separate name fields first
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip() or None
        last_name = request.form.get("last_name", "").strip()
        
        # For backward compatibility, also check for full name
        full_name = request.form.get("name", "").strip()
        
        email = request.form.get("email", "").strip().lower()
        course = request.form.get("course", "").strip()
        contact = request.form.get("contact", "").strip()
        guardian_name = request.form.get("guardian_name", "").strip()
        address = request.form.get("address", "").strip()

        # Basic validation
        if not student_id or len(student_id) != 11 or not student_id.isdigit():
            flash("Invalid USN. Must be 11 digits.", "danger")
            return redirect(url_for("admin_import_students"))

        # Determine name format and ensure parsing happens
        if first_name or last_name:
            # Using separate name fields
            name_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name
            }
            # Also create full name for backward compatibility
            full_name_for_db = get_full_name(name_data)
        elif full_name:
            # Parse the full name into components
            parsed_names = parse_name_input(full_name)
            name_data = {
                'first_name': parsed_names['first_name'],
                'middle_name': parsed_names['middle_name'],
                'last_name': parsed_names['last_name']
            }
            full_name_for_db = full_name
        else:
            flash("Name is required.", "danger")
            return redirect(url_for("admin_import_students"))

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("admin_import_students"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check for duplicate USN or email
            cursor.execute("SELECT 1 FROM students WHERE student_id = %s OR email = %s", (student_id, email))
            if cursor.fetchone():
                flash("Student with this USN or email already exists.", "danger")
                return redirect(url_for("admin_import_students"))

            # Insert with explicit name fields - FIXED VERSION
            cursor.execute("""
                INSERT INTO students (
                    student_id, name, first_name, middle_name, last_name,
                    email, course, contact, guardian_name, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id, 
                full_name_for_db,
                name_data['first_name'],
                name_data['middle_name'],
                name_data['last_name'],
                email, course, contact, guardian_name, address
            ))

            conn.commit()
            flash("Student record added successfully!", "success")
            print(f"✅ Added student: {student_id} - {full_name_for_db}")
            print(f"   First: {name_data['first_name']}, Middle: {name_data['middle_name']}, Last: {name_data['last_name']}")

        except Exception as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "danger")
            print(f"❌ Error adding student: {str(e)}")

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("admin_import_students"))

    return render_template("admin_import_students.html")


    

# NEW: Admin route to upload training data
# Purpose: Allow admins to upload photos for training the validator model
# This route handles file uploads for both valid and invalid photo categories
@app.route('/admin/upload_training_data', methods=['POST'])
@login_required("admin")
def upload_training_data():
    data_type = request.form.get('data_type')
    
    if data_type not in ['valid', 'invalid']:
        flash("❌ Invalid data type", "danger")
        return redirect(url_for('train_validator'))
    
    files = request.files.getlist('photos')
    
    if not files or not files[0].filename:
        flash("❌ No files selected", "danger")
        return redirect(url_for('train_validator'))
    
    # Determine target directory
    target_dir = VALID_PHOTOS_DIR if data_type == 'valid' else INVALID_PHOTOS_DIR;
    
    # Save files
    count = 0
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(target_dir, filename))
            count += 1
    
    flash(f"✅ Uploaded {count} {data_type} photos for training", "success")
    return redirect(url_for('train_validator'))



# NEW: Admin route to test the validator on a specific image
# Purpose: Allow admins to test the trained model on individual photos
# This helps verify that the model is working correctly before using it in production
@app.route('/admin/test_validator', methods=['POST'])
@login_required("admin")
def test_validator():
    if not photo_validator or not photo_validator.model:
        flash("❌ No trained model available", "danger")
        return redirect(url_for('train_validator'))
    
    file = request.files.get('test_photo')
    
    if not file or not file.filename:
        flash("❌ No file selected", "danger")
        return redirect(url_for('train_validator'))
    
    # Save the file
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], "test_" + filename)
    file.save(image_path)
    
    # Validate the image
    result = photo_validator.validate(image_path=image_path)
    
    # Make result JSON serializable
    result = make_json_serializable(result)
    
    # Flash result
    if result["valid"]:
        confidence = result.get("confidence", 0) * 100
        flash(f"✅ Image is valid (Confidence: {confidence:.1f}%)", "success")
    else:
        confidence = result.get("confidence", 0) * 100
        flash(f"❌ Image is invalid: {result.get('error', 'Unknown error')} (Confidence: {confidence:.1f}%)", "danger")
    
    return redirect(url_for('train_validator'))


# Purpose: Display a sample ID card layout
# This route shows administrators what the final ID cards will look like
@app.route('/sample_layout')
@login_required("admin")
def sample_layout():
    return render_template("sample_layout.html")




#---------- Admin Login ----------
# Purpose: Handle admin-specific login
# This route provides a separate login page for administrators
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['student_id']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE student_id = %s AND role = 'admin'", (admin_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            print("Stored Hash:", user['password'])  # Debug: Print stored password hash
            print("Entered Password:", password)  # Debug: Print entered password

            if check_password_hash(user['password'], password):
                print("✅ Password match!")
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_role'] = user['role']
                return redirect(url_for('admin_dashboard'))
            else:
                print("❌ Password mismatch!")

        flash("❌ Invalid Admin ID or password!", "danger")

    return render_template("admin_login.html")




# ---------- Admin Dashboard ----------
# Purpose: Display the main admin dashboard with application statistics
# This is the central hub for administrators to monitor the system
@app.route('/admin_dashboard')
@login_required("admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch total applications
    cursor.execute("SELECT COUNT(*) as total_students FROM students")
    total_students = cursor.fetchone()["total_students"]

    # Fetch pending applications
    cursor.execute("SELECT COUNT(*) as pending FROM students WHERE application_status = 'pending'")
    pending = cursor.fetchone()["pending"]

    # Fetch processing applications
    cursor.execute("SELECT COUNT(*) as processing FROM students WHERE application_status = 'processing'")
    processing = cursor.fetchone()["processing"]

    # Fetch done applications
    cursor.execute("SELECT COUNT(*) as done FROM students WHERE application_status = 'done'")
    done = cursor.fetchone()["done"]

    # Fetch receive applications
    cursor.execute("SELECT COUNT(*) as receive FROM students WHERE application_status = 'receive'")
    receive = cursor.fetchone()["receive"]

    cursor.close()
    conn.close()

    # Debugging Output
    print(f"DEBUG - Total: {total_students}, Pending: {pending}, Processing: {processing}, Done: {done}, Receive: {receive}")

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        pending=pending,
        processing=processing,
        done=done,
        receive=receive
    )

# Purpose: Display all student applications for admin review
# This route lists all applications in the system for administrators to manage
@app.route('/admin/applications')
def admin_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")  # Ensure all students are fetched
    applications = cursor.fetchall()

    conn.close()
    return render_template("admin_applications.html", applications=applications)

# Admin routes for Lost ID requests

@app.route('/admin/lost_id_requests')
@login_required("admin")
def admin_lost_id_requests():
    """Display all lost ID requests for admin review"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all lost ID requests with student information
    cursor.execute("""
        SELECT lr.*, u.name as student_name, s.course, s.email, s.contact
        FROM lost_id_requests lr
        JOIN users u ON lr.student_id = u.student_id
        JOIN students s ON lr.student_id = s.student_id
        ORDER BY 
            CASE 
                WHEN lr.status = 'pending' THEN 1
                WHEN lr.status = 'verified' THEN 2
                WHEN lr.status = 'approved' THEN 3
                WHEN lr.status = 'rejected' THEN 4
            END,
            lr.created_at DESC
    """)
    requests = cursor.fetchall()
    
    # Get count of new requests
    cursor.execute("SELECT COUNT(*) as new_count FROM lost_id_requests WHERE status = 'pending'")
    new_count = cursor.fetchone()['new_count']
    
    cursor.close()
    conn.close()
    
    return render_template("admin_lost_id_requests.html", requests=requests, new_count=new_count)

@app.route('/admin/view_lost_id_request/<int:request_id>')
@login_required("admin")
def admin_view_lost_id_request(request_id):
    """View details of a specific lost ID request"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get request details with student information
    cursor.execute("""
        SELECT lr.*, u.name as student_name, s.course, s.email, s.contact
        FROM lost_id_requests lr
        JOIN users u ON lr.student_id = u.student_id
        JOIN students s ON lr.student_id = s.student_id
        WHERE lr.id = %s
    """, (request_id,))
    request = cursor.fetchone()
    
    if not request:
        cursor.close()
        conn.close()
        flash("Request not found", "danger")
        return redirect(url_for('admin_lost_id_requests'))
    
    cursor.close()
    conn.close()
    
    return render_template("admin_view_lost_id_request.html", request=request)

@app.route('/admin/update_lost_id_notes/<int:request_id>', methods=['POST'])
@login_required("admin")
def update_lost_id_notes(request_id):
    """Update admin notes for a lost ID request"""
    try:
        data = request.json
        notes = data.get('notes')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE lost_id_requests 
            SET admin_notes = %s, updated_at = NOW()
            WHERE id = %s
        """, (notes, request_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/update_lost_id_osas/<int:request_id>', methods=['POST'])
@login_required("admin")
def update_lost_id_osas(request_id):
    """Update OSAS verification status for a lost ID request"""
    try:
        data = request.json
        verified = data.get('verified')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE lost_id_requests 
            SET osas_verified = %s, updated_at = NOW()
            WHERE id = %s
        """, (verified, request_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/update_lost_id_status/<int:request_id>', methods=['POST'])
@login_required("admin")
def update_lost_id_status(request_id):
    """Update status for a lost ID request"""
    try:
        data = request.json
        status = data.get('status')
        
        if status not in ['pending', 'verified', 'approved', 'rejected']:
            return jsonify({"success": False, "error": "Invalid status"})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE lost_id_requests 
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, request_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/approve_lost_id/<int:request_id>', methods=['POST'])
@login_required("admin")
def approve_lost_id(request_id):
    """Approve a lost ID request and initiate ID reprinting process"""
    try:
        admin_id = session.get('student_id') or f"ADMIN_{session.get('user_id')}"
        admin_name = session.get('user_name', 'Admin')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get request details
        cursor.execute("""
            SELECT lr.*, u.name as student_name, s.email
            FROM lost_id_requests lr
            JOIN users u ON lr.student_id = u.student_id
            JOIN students s ON lr.student_id = s.student_id
            WHERE lr.id = %s
        """, (request_id,))
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({"success": False, "error": "Request not found"})
        
        # Check if OSAS verification is completed
        if not request_data.get('osas_verified'):
            return jsonify({"success": False, "error": "OSAS verification is required before approval"})
        
        # Update request status
        cursor.execute("""
            UPDATE lost_id_requests 
            SET status = 'approved', 
                processed_by = %s,
                processed_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
        """, (admin_name, request_id))
        
        # Create a new student ID application with 'processing' status
        cursor.execute("""
            UPDATE students
            SET application_status = 'processing'
            WHERE student_id = %s
        """, (request_data['student_id'],))
        
        # Send email notification to student
        if request_data.get('email'):
            try:
                msg = Message(
                    subject="Your Lost ID Request Has Been Approved",
                    recipients=[request_data['email']],
                    body=f"""Dear {request_data['student_name']},

We are pleased to inform you that your request for a replacement student ID (Request #{request_id}) has been approved.

Your new ID card is now being processed and will be ready for pickup soon. You will receive another notification when it is ready.

Thank you for your patience.

Best regards,
Technical Support Department
ACLC College
"""
                )
                mail.send(msg)
            except Exception as email_error:
                print(f"Failed to send approval email: {email_error}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/reject_lost_id/<int:request_id>', methods=['POST'])
@login_required("admin")
def reject_lost_id(request_id):
    """Reject a lost ID request"""
    try:
        data = request.json
        reason = data.get('reason')
        
        if not reason:
            return jsonify({"success": False, "error": "Rejection reason is required"})
        
        admin_id = session.get('student_id') or f"ADMIN_{session.get('user_id')}"
        admin_name = session.get('user_name', 'Admin')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get request details
        cursor.execute("""
            SELECT lr.*, u.name as student_name, s.email
            FROM lost_id_requests lr
            JOIN users u ON lr.student_id = u.student_id
            JOIN students s ON lr.student_id = s.student_id
            WHERE lr.id = %s
        """, (request_id,))
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({"success": False, "error": "Request not found"})
        
        # Update request status
        cursor.execute("""
            UPDATE lost_id_requests 
            SET status = 'rejected', 
                rejection_reason = %s,
                processed_by = %s,
                processed_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
        """, (reason, admin_name, request_id))
        
        # Send email notification to student
        if request_data.get('email'):
            try:
                msg = Message(
                    subject="Update on Your Lost ID Request",
                    recipients=[request_data['email']],
                    body=f"""Dear {request_data['student_name']},

We regret to inform you that your request for a replacement student ID (Request #{request_id}) could not be approved at this time.

Reason: {reason}

If you have any questions or need further assistance, please contact the Technical Support Department.

Best regards,
Technical Support Department
ACLC College
"""
                )
                mail.send(msg)
            except Exception as email_error:
                print(f"Failed to send rejection email: {email_error}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/email_student/<int:request_id>', methods=['POST'])
@login_required("admin")
def email_student(request_id):
    """Send email to student regarding their lost ID request"""
    try:
        data = request.json
        subject = data.get('subject')
        body = data.get('body')
        
        if not subject or not body:
            return jsonify({"success": False, "error": "Subject and body are required"})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get student email
        cursor.execute("""
            SELECT s.email, u.name as student_name
            FROM lost_id_requests lr
            JOIN students s ON lr.student_id = s.student_id
            JOIN users u ON lr.student_id = u.student_id
            WHERE lr.id = %s
        """, (request_id,))
        student = cursor.fetchone()
        
        if not student or not student.get('email'):
            return jsonify({"success": False, "error": "Student email not found"})
        
        # Send email
        msg = Message(
            subject=subject,
            recipients=[student['email']],
            body=body
        )
        mail.send(msg)
        
        # Log the email in the database
        cursor.execute("""
            INSERT INTO communication_logs 
            (request_id, type, subject, message, sent_by, sent_at)
            VALUES (%s, 'email', %s, %s, %s, NOW())
        """, (request_id, subject, body, session.get('user_name', 'Admin')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download_affidavit/<int:file_id>')
@login_required("admin")
def download_affidavit(file_id):
    """Download the affidavit file for a lost ID request"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get file information
    cursor.execute("SELECT affidavit_file FROM lost_id_requests WHERE id = %s", (file_id,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not result or not result['affidavit_file']:
        flash("File not found", "danger")
        return redirect(url_for('admin_lost_id_requests'))
    
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], result['affidavit_file'])
    
    if not os.path.exists(file_path):
        flash("File not found on server", "danger")
        return redirect(url_for('admin_lost_id_requests'))
    
    return send_file(file_path, as_attachment=True)

@app.route('/admin/get_new_lost_id_count')
@login_required("admin")
def get_new_lost_id_count():
    """Get count of new lost ID requests"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as new_count FROM lost_id_requests WHERE status = 'pending'")
    new_count = cursor.fetchone()['new_count']
    
    cursor.close()
    conn.close()
    
    return jsonify({"new_count": new_count})


@app.route('/api/analytics/<period>')
@login_required("admin")
def get_analytics_data(period):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if period == 'day':
            # Get hourly data for today
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT HOUR(created_at) as hour, COUNT(*) as count
                FROM students 
                WHERE DATE(created_at) = %s
                GROUP BY HOUR(created_at)
                ORDER BY hour
            """, (today,))
            
            results = cursor.fetchall()
            
            # Create hourly data (6 AM to 7 PM)
            hourly_data = {row['hour']: row['count'] for row in results}
            
            # Format for chart (6 AM to 7 PM)
            values = []
            for hour in range(6, 20):  # 6 AM to 7 PM
                values.append(hourly_data.get(hour, 0))
            
        elif period == 'week':
            # Get daily data for this week
            cursor.execute("""
                SELECT DAYOFWEEK(created_at) as day_of_week, COUNT(*) as count
                FROM students 
                WHERE YEARWEEK(created_at, 1) = YEARWEEK(CURDATE(), 1)
                GROUP BY DAYOFWEEK(created_at)
                ORDER BY day_of_week
            """)
            
            results = cursor.fetchall()
            
            # Create weekly data (Monday = 2, Sunday = 1 in MySQL DAYOFWEEK)
            weekly_data = {row['day_of_week']: row['count'] for row in results}
            
            # Format for chart (Monday to Sunday)
            # MySQL DAYOFWEEK: Sunday=1, Monday=2, ..., Saturday=7
            values = []
            for day in [2, 3, 4, 5, 6, 7, 1]:  # Monday to Sunday
                values.append(weekly_data.get(day, 0))
            
        elif period == 'month':
            # Get weekly data for this month
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN DAY(created_at) <= 7 THEN 1
                        WHEN DAY(created_at) <= 14 THEN 2
                        WHEN DAY(created_at) <= 21 THEN 3
                        ELSE 4
                    END as week_num,
                    COUNT(*) as count
                FROM students 
                WHERE YEAR(created_at) = YEAR(CURDATE()) 
                AND MONTH(created_at) = MONTH(CURDATE())
                GROUP BY week_num
                ORDER BY week_num
            """)
            
            results = cursor.fetchall()
            
            # Create monthly data
            monthly_data = {row['week_num']: row['count'] for row in results}
            
            # Format for chart (4 weeks)
            values = []
            for week in range(1, 5):
                values.append(monthly_data.get(week, 0))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'values': values,
            'period': period
        })
        
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Display detailed information about a specific student application
# This route allows administrators to view all details of a student's application
@app.route('/view_application/<student_id>')
@login_required("admin")  # Only admins can access
def view_application(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get student application details
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not student:
        flash("⚠️ Student record not found!", "danger")
        return redirect(url_for('admin_applications'))

    return render_template("view_application.html", student=student)

#----------------------------------------------------------------------------------------------------------------------------------


# Purpose: Allow downloading of uploaded files
# This route enables administrators to download student-uploaded files like profile pictures and signatures
@app.route('/download/<filename>')
@login_required("admin")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: API endpoint to get student details
# This route returns student information in JSON format for AJAX requests
@app.route('/get_student/<student_id>')
@login_required("admin")
def get_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch student details from students table
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # ✅ Get barcode filename from database
    barcode_filename = student.get("barcode")
    barcode_path = os.path.join("static", "barcodes", barcode_filename)

    # ✅ If barcode file does NOT exist in `static/barcodes/`, generate it
    if barcode_filename and not os.path.exists(barcode_path):
        os.makedirs("static/barcodes", exist_ok=True)  # Ensure directory exists

        # ✅ Generate barcode again
        CODE39 = get_barcode_class('code39')
        generated_barcode = Code39(student_id.strip(), writer=ImageWriter(), add_checksum=False)
        generated_barcode.save(barcode_path.replace(".png", ""), {"format": "PNG"})


    # ✅ Set barcode path for frontend
    if barcode_filename:
        student["barcode"] = f"/{barcode_path}"  # ✅ Correct barcode path
    else:
        student["barcode"] = "/static/default_barcode.jpg"  # Default barcode if missing

    cursor.close()
    conn.close()
    
    return jsonify(student)



#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Update a student's application status
# This route handles status changes, sends notifications, and maintains a history of status updates
# Fixed status update function to properly handle name fields
@app.route('/update_application_status/<student_id>', methods=['POST'])
@login_required("admin")
def update_application_status(student_id):
    try:
        data = request.json
        new_status = data.get('status')
        previous_status = data.get('previousStatus')
        update_history = data.get('updateHistory', False)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch student details with all name fields
        cursor.execute("""
            SELECT *, first_name, middle_name, last_name, name 
            FROM students WHERE student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        if not student:
            return jsonify({'success': False, 'error': 'Student not found'}), 404

        # Check if status is actually changing
        if student['application_status'] == new_status:
            return jsonify({'success': True, 'message': 'Status unchanged'})

        # If new status is 'receive', check if already exists in history
        if new_status == 'receive':
            cursor.execute("""
                SELECT * FROM student_history 
                WHERE student_id = %s 
                ORDER BY received_date DESC 
                LIMIT 1
            """, (student_id,))
            existing_history = cursor.fetchone()

            # Only insert if no existing receive record
            if not existing_history:
                # Get full name for history record
                full_name = get_full_name(student)
                
                # FIXED: Insert with proper name fields
                cursor.execute("""
                    INSERT INTO student_history (
                        student_id, name, first_name, middle_name, last_name,
                        course, contact, guardian_name, address, 
                        profile_picture, signature, barcode, received_date,
                        academic_year, semester
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                """, (
                    student["student_id"], 
                    full_name,
                    student.get("first_name"), 
                    student.get("middle_name"), 
                    student.get("last_name"),
                    student["course"], 
                    student["contact"], 
                    student["guardian_name"], 
                    student["address"],
                    student["profile_picture"], 
                    student["signature"], 
                    student["barcode"],
                    student.get("academic_year", "2025-2026"), 
                    student.get("semester", 1)
                ))
                
                print(f"✅ Added to history: {student_id} - {full_name}")
                print(f"   First: {student.get('first_name')}, Middle: {student.get('middle_name')}, Last: {student.get('last_name')}")

        # Update student status
        cursor.execute("""
            UPDATE students 
            SET application_status = %s 
            WHERE student_id = %s
        """, (new_status, student_id))

        # Add to status history if requested
        if update_history:
            admin_username = session.get('user_name', 'Admin')

            cursor.execute("""
                INSERT INTO status_history (
                    student_id, status, changed_by, previous_status, changed_at
                ) VALUES (%s, %s, %s, %s, NOW())
            """, (
                student_id, new_status, admin_username, previous_status
            ))

        # Send email if status is set to 'done'
        if new_status == 'done' and student.get('email'):
            student_email = student["email"]
            student_name = get_full_name(student)

            try:
                msg = Message(
                    subject="🎉 Your Student ID is Ready for Pickup!",
                    recipients=[student_email],
                    body=f"Hello {student_name},\n\nYour student ID has been processed and is now ready for pickup at the TSD office.\n\nThank you!"
                )
                mail.send(msg)
            except Exception as email_error:
                print("Failed to send email:", email_error)

        conn.commit()
        return jsonify({'success': True, 'barcode': student.get('barcode')})

    except Exception as e:
        conn.rollback()
        print(f"❌ Status update error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


#----------------------------------------------------------------------------------------------------------------------------------


# Purpose: Display history of student IDs that have been received
# This route shows a list of all student IDs that have been marked as received
@app.route('/student_id_history')
@login_required("admin")
def student_id_history():
    # Get current academic year
    current_year = datetime.now().year
    if datetime.now().month < 6:  # Before June, use previous year
        current_year -= 1
    current_academic_year = f"{current_year}-{current_year + 1}"
    
    # Get list of academic years (current and 4 previous)
    academic_years = []
    for i in range(5):
        year = current_year - i
        academic_years.append(f"{year}-{year + 1}")
    
    # Get semester (1 for June-December, 2 for January-May)
    current_month = datetime.now().month
    current_semester = 1 if 6 <= current_month <= 12 else 2
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query with filtering
    query = """
        SELECT * FROM student_history 
        WHERE semester = %s AND academic_year = %s
        ORDER BY received_date DESC
        LIMIT 10
    """
    cursor.execute(query, (current_semester, current_academic_year))
    student_history = cursor.fetchall()
    
    # Update status for each record based on received_date
    for student in student_history:
        if student['received_date']:
            received_date = student['received_date']
            semester_start = get_semester_start_date(student['academic_year'], student['semester'])
            
            # If received date is within 16 weeks of semester start, it's "New", otherwise "Old"
            sixteen_weeks = timedelta(weeks=16)
            student['status'] = "New" if received_date <= (semester_start + sixteen_weeks) else "Old"
        else:
            student['status'] = "New"  # Default to New if no date
    
    cursor.close()
    conn.close()
    
    return render_template(
        "student_id_history.html", 
        student_history=student_history,
        current_semester=current_semester,
        current_academic_year=current_academic_year,
        academic_years=academic_years
    )

# Helper function to get semester start date
def get_semester_start_date(academic_year, semester):
    if not academic_year or '-' not in academic_year:
        return datetime.now()
        
    start_year = int(academic_year.split('-')[0])
    
    if semester == 1:  # First semester starts in June
        return datetime(start_year, 6, 1)
    else:  # Second semester starts in January of the next year
        return datetime(start_year + 1, 1, 1)

#----------------------------------------------------------------------------------------------------------------------------------


# Purpose: API endpoint to get a student's history
# This route returns the history of a student's ID in JSON format
@app.route('/get_student_history/<student_id>')
@login_required("admin")
def get_student_history(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student_history WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # Calculate status based on received_date
    if student['received_date']:
        received_date = student['received_date']
        semester_start = get_semester_start_date(student['academic_year'], student['semester'])
        
        # If received date is within 16 weeks of semester start, it's "New", otherwise "Old"
        sixteen_weeks = timedelta(weeks=16)
        student['status'] = "New" if received_date <= (semester_start + sixteen_weeks) else "Old"
    else:
        student['status'] = "New"  # Default to New if no date

    # Ensure barcode path is correct
    barcode_filename = student.get("barcode")
    if barcode_filename:
        barcode_path = os.path.join("static", "barcodes", barcode_filename)
        if not os.path.exists(barcode_path):
            # Generate barcode if it doesn't exist
            os.makedirs("static/barcodes", exist_ok=True)
            CODE39 = get_barcode_class('code39')
            generated_barcode = Code39(student_id.strip(), writer=ImageWriter(), add_checksum=False)
            generated_barcode.save(barcode_path.replace(".png", ""), {"format": "PNG"})

    cursor.close()
    conn.close()
    
    return jsonify(student)

#----------------------------------------------------------------------------------------------------------------------------------


@app.route('/api/student_history')
@login_required("admin")
def api_student_history():
    semester = request.args.get('semester', 1, type=int)
    academic_year = request.args.get('academic_year', '2025-2026')
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = 10
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Build query with search
    query = """
        SELECT * FROM student_history 
        WHERE semester = %s AND academic_year = %s
    """
    count_query = """
        SELECT COUNT(*) as total FROM student_history 
        WHERE semester = %s AND academic_year = %s
    """
    params = [semester, academic_year]
    
    if search:
        query += " AND (student_id LIKE %s OR name LIKE %s)"
        count_query += " AND (student_id LIKE %s OR name LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    # Add pagination
    query += " ORDER BY received_date DESC LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    query_params = params + [per_page, offset]
    
    # Get total count
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get paginated results
    cursor.execute(query, query_params)
    students = cursor.fetchall()
    
    # Calculate status for each record
    for student in students:
        if student['received_date']:
            received_date = student['received_date']
            semester_start = get_semester_start_date(student['academic_year'], student['semester'])
            
            # If received date is within 16 weeks of semester start, it's "New", otherwise "Old"
            sixteen_weeks = timedelta(weeks=16)
            student['status'] = "New" if received_date <= (semester_start + sixteen_weeks) else "Old"
        else:
            student['status'] = "New"  # Default to New if no date
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'students': students,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': (page * per_page) < total
    })



def create_excel_export_with_names(students, semester, academic_year):
    """Create Excel export with separate name columns"""
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.close()
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = f"Semester {semester} - {academic_year}"
        
        # Add title and metadata
        ws['A1'] = f"Student ID History - {semester}{'st' if semester == 1 else 'nd'} Semester {academic_year}"
        ws['A2'] = f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(students)}"
        
        # Style the title
        title_cell = ws['A1']
        title_cell.font = Font(bold=True, size=14)
        ws.merge_cells('A1:O1')  # Adjusted for more columns
        
        # Style the metadata
        meta_cell = ws['A2']
        meta_cell.font = Font(size=10, italic=True)
        ws.merge_cells('A2:O2')
        
        # Updated headers with separate name columns
        headers = [
            'Student ID', 'Full Name', 'First Name', 'Middle Name/Initial', 'Last Name',
            'Course', 'Contact Number', 'Guardian Name', 'Address', 
            'Profile Image', 'Signature', 'Received Date', 'Status', 'Academic Year', 'Semester'
        ]
        
        # Add headers starting from row 4
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.font = Font(bold=True, size=10)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Set column widths
        column_widths = [15, 25, 15, 15, 15, 35, 15, 20, 30, 15, 15, 18, 10, 12, 10]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width
        
        # Add data with separate name fields
        for row_idx, student in enumerate(students, 5):
            # Set row height for images
            ws.row_dimensions[row_idx].height = 60
            
            # Get full name using helper function
            full_name = get_full_name(student)
            
            # Add text data
            ws.cell(row=row_idx, column=1, value=student['student_id'])
            ws.cell(row=row_idx, column=2, value=full_name)
            ws.cell(row=row_idx, column=3, value=student.get('first_name', ''))
            ws.cell(row=row_idx, column=4, value=student.get('middle_name', ''))
            ws.cell(row=row_idx, column=5, value=student.get('last_name', ''))
            ws.cell(row=row_idx, column=6, value=student['course'])
            ws.cell(row=row_idx, column=7, value=student['contact'])
            ws.cell(row=row_idx, column=8, value=student['guardian_name'])
            ws.cell(row=row_idx, column=9, value=student['address'])
            
            # Add profile image
            if student.get('profile_picture'):
                profile_path = os.path.join("static", "uploads", student['profile_picture'])
                if os.path.exists(profile_path):
                    try:
                        profile_img = resize_image_for_excel(profile_path, 50, 50)
                        if profile_img:
                            profile_img.anchor = f'J{row_idx}'
                            ws.add_image(profile_img)
                    except Exception as e:
                        print(f"Error adding profile image: {e}")
                        ws.cell(row=row_idx, column=10, value="Image Error")
            
            # Add signature image
            if student.get('signature'):
                signature_path = os.path.join("static", "uploads", student['signature'])
                if os.path.exists(signature_path):
                    try:
                        signature_img = resize_image_for_excel(signature_path, 80, 40)
                        if signature_img:
                            signature_img.anchor = f'K{row_idx}'
                            ws.add_image(signature_img)
                    except Exception as e:
                        print(f"Error adding signature image: {e}")
                        ws.cell(row=row_idx, column=11, value="Image Error")
            
            # Add remaining data
            ws.cell(row=row_idx, column=12, value=student['received_date'])
            ws.cell(row=row_idx, column=13, value=student.get('status', 'New'))
            ws.cell(row=row_idx, column=14, value=student.get('academic_year', academic_year))
            ws.cell(row=row_idx, column=15, value=semester)
            
            # Center align all cells in this row
            for col in range(1, 16):
                cell = ws.cell(row=row_idx, column=col)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Add borders to header row
        for col in range(1, 16):
            cell = ws.cell(row=4, column=col)
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Save workbook
        wb.save(temp_file.name)
        
        filename = f"student_history_{academic_year}_sem{semester}_with_names.xlsx"
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error creating Excel with names: {e}")
        return None


# Purpose: Export student history as Excel or ZIP file
# Add export functionality
@app.route('/export_student_history')
@login_required("admin")
def export_student_history():
    semester = request.args.get('semester', 1, type=int)
    academic_year = request.args.get('academic_year', '2025-2026')
    include_images = request.args.get('include_images', 'false').lower() == 'true'
    export_format = request.args.get('format', 'excel')  # excel or csv
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Updated query to include name fields
        query = """
            SELECT student_id, name, first_name, middle_name, last_name, 
                   course, contact, guardian_name, address, 
                   received_date, academic_year, semester, profile_picture, signature, barcode
            FROM student_history 
            WHERE semester = %s AND academic_year = %s
            ORDER BY received_date DESC
        """
        cursor.execute(query, (semester, academic_year))
        students = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not students:
            return jsonify({'error': 'No data found for the selected semester and academic year'}), 404
        
        # Calculate status for each record and ensure full names
        for student in students:
            student['status'] = calculate_student_status(student)
            # Ensure we have a full name for display
            if not student.get('name'):
                student['name'] = get_full_name(student)
            # Format received_date
            if student['received_date']:
                student['received_date'] = student['received_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        if export_format == 'csv':
            # CSV export with separate name fields
            return create_csv_export_with_names(students, semester, academic_year)
        else:
            # Excel export with separate name fields
            return create_excel_export_with_names(students, semester, academic_year)
            
    except Exception as e:
        print(f"Export error: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

def create_csv_export_with_names(students, semester, academic_year):
    """Create CSV export with separate name columns"""
    try:
        # Prepare data with separate name fields
        export_data = []
        
        for student in students:
            # Ensure we have a full name
            full_name = get_full_name(student)
            
            export_data.append({
                'Student ID': student['student_id'],
                'Full Name': full_name,
                'First Name': student.get('first_name', ''),
                'Middle Name/Initial': student.get('middle_name', ''),
                'Last Name': student.get('last_name', ''),
                'Course': student['course'],
                'Contact Number': student['contact'],
                'Guardian Name': student['guardian_name'],
                'Address': student['address'],
                'Received Date': student['received_date'],
                'Status': student.get('status', 'New'),
                'Academic Year': student.get('academic_year', academic_year),
                'Semester': semester
            })
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
        df.to_csv(temp_file.name, index=False)
        
        filename = f"student_history_{academic_year}_sem{semester}_with_names.csv"
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        print(f"Error creating CSV with names: {e}")
        return None

print("✅ Updated export functions for separate name fields completed!")





@app.context_processor
def inject_name_helpers():
    """Inject name helper functions into all templates"""
    return {
        'get_full_name': get_full_name,
        'parse_name_input': parse_name_input
    }

# Updated status history insertion to handle names properly
def update_application_status_with_names(student_id, new_status, previous_status, update_history=False):
    """Updated function to handle status updates with proper name handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch student details with all name fields
        cursor.execute("""
            SELECT *, first_name, middle_name, last_name, name 
            FROM students WHERE student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        if not student:
            return {'success': False, 'error': 'Student not found'}

        # Check if status is actually changing
        if student['application_status'] == new_status:
            return {'success': True, 'message': 'Status unchanged'}

        # If new status is 'receive', check if already exists in history
        if new_status == 'receive':
            cursor.execute("""
                SELECT * FROM student_history 
                WHERE student_id = %s 
                ORDER BY received_date DESC 
                LIMIT 1
            """, (student_id,))
            existing_history = cursor.fetchone()

            # Only insert if no existing receive record
            if not existing_history:
                # Get full name for history record
                full_name = get_full_name(student)
                
                cursor.execute("""
                    INSERT INTO student_history (
                        student_id, name, first_name, middle_name, last_name,
                        course, contact, guardian_name, address, 
                        profile_picture, signature, barcode, received_date,
                        academic_year, semester
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                """, (
                    student["student_id"], full_name, 
                    student.get("first_name"), student.get("middle_name"), student.get("last_name"),
                    student["course"], student["contact"], student["guardian_name"], student["address"],
                    student["profile_picture"], student["signature"], student["barcode"],
                    student.get("academic_year", "2025-2026"), student.get("semester", 1)
                ))

        # Update student status
        cursor.execute("""
            UPDATE students 
            SET application_status = %s 
            WHERE student_id = %s
        """, (new_status, student_id))

        # Add to status history if requested
        if update_history:
            admin_username = session.get('user_name', 'Admin')

            cursor.execute("""
                INSERT INTO status_history (
                    student_id, status, changed_by, previous_status, changed_at
                ) VALUES (%s, %s, %s, %s, NOW())
            """, (
                student_id, new_status, admin_username, previous_status
            ))

        # Send email if status is set to 'done'
        if new_status == 'done' and student.get('email'):
            student_email = student["email"]
            student_name = get_full_name(student)

            try:
                msg = Message(
                    subject="🎉 Your Student ID is Ready for Pickup!",
                    recipients=[student_email],
                    body=f"Hello {student_name},\n\nYour student ID has been processed and is now ready for pickup at the TSD office.\n\nThank you!"
                )
                mail.send(msg)
            except Exception as email_error:
                print("Failed to send email:", email_error)

        conn.commit()
        return {'success': True, 'barcode': student.get('barcode')}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': str(e)}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

print("✅ Template context processor and updated status functions added!")
print("📋 Summary of changes:")
print("   • Added helper functions for name handling")
print("   • Updated registration and login routes")
print("   • Updated student dashboard and profile routes")
print("   • Updated admin import and user creation")
print("   • Updated export functions with separate name columns")
print("   • Added template context processor")
print("   • Updated status history with proper name handling")
print("\n🔧 Next steps:")
print("   1. Add these functions to your app.py file")
print("   2. Update your HTML templates to use separate name fields")
print("   3. Test the registration and login process")
print("   4. Test the export functionality")
print("   5. Verify backward compatibility with existing data")












# Updated resize_image_for_excel function in your app.py
def resize_image_for_excel(image_path, width, height):
    """Resize image for Excel embedding with proper signature handling"""
    try:
        # Check if this is a signature file
        is_signature = 'signature' in os.path.basename(image_path).lower()
        
        with Image.open(image_path) as img:
            print(f"Processing {'signature' if is_signature else 'image'}: {image_path}")
            print(f"Original mode: {img.mode}, size: {img.size}")
            
            if is_signature:
                # Special processing for signatures
                if img.mode in ('RGBA', 'LA'):
                    # Create white background for signatures
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        # Use alpha channel as mask
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode == 'P':
                    img = img.convert('RGB')
                elif img.mode == 'L':
                    img = img.convert('RGB')
                
                # Enhance signature contrast
                import numpy as np
                import cv2
                
                img_array = np.array(img)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Apply adaptive threshold for better signature visibility
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                             cv2.THRESH_BINARY, 11, 2)
                
                # Invert so signature is black on white
                thresh = 255 - thresh
                
                # Convert back to RGB
                signature_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
                img = Image.fromarray(signature_rgb)
                
            else:
                # Regular processing for profile pictures
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
            
            # Resize image maintaining aspect ratio
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Create new image with white background
            new_img = Image.new('RGB', (width, height), 'white')
            
            # Paste the resized image centered
            x = (width - img.width) // 2
            y = (height - img.height) // 2
            new_img.paste(img, (x, y))
            
            # Save to bytes for Excel
            img_bytes = io.BytesIO()
            new_img.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            
            # Create openpyxl image
            from openpyxl.drawing.image import Image as OpenpyxlImage
            excel_img = OpenpyxlImage(img_bytes)
            excel_img.width = width
            excel_img.height = height
            
            print(f"✅ Successfully processed {'signature' if is_signature else 'image'}")
            return excel_img
            
    except Exception as e:
        print(f"❌ Error resizing image {image_path}: {e}")
        return None

# Test the updated function
def test_excel_image_processing():
    test_files = [
        ("static/uploads/i6.png", "profile"),
        ("static/uploads/21000602400_signature.png", "signature")
    ]
    
    for file_path, file_type in test_files:
        if os.path.exists(file_path):
            print(f"\nTesting {file_type}: {file_path}")
            if file_type == "signature":
                result = resize_image_for_excel(file_path, 80, 40)
            else:
                result = resize_image_for_excel(file_path, 50, 50)
            
            if result:
                print(f"✅ {file_type} processed successfully")
            else:
                print(f"❌ Failed to process {file_type}")

test_excel_image_processing()


def process_signature_for_excel(signature_path, width=80, height=40):
    """
    Alternative signature processing method
    Focuses on preserving signature strokes while removing transparency
    """
    try:
        from PIL import Image, ImageEnhance, ImageOps
        import numpy as np
        
        with Image.open(signature_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Extract alpha channel
            alpha = img.split()[-1]
            
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            
            # Convert image to RGB
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=alpha)
            
            # Convert to grayscale for processing
            gray = rgb_img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)  # Increase contrast
            
            # Apply threshold to make signature more visible
            threshold = 200  # Adjust this value as needed
            enhanced_array = np.array(enhanced)
            binary = np.where(enhanced_array < threshold, 0, 255)
            
            # Convert back to PIL Image
            binary_img = Image.fromarray(binary.astype(np.uint8), mode='L')
            
            # Convert to RGB
            final_img = binary_img.convert('RGB')
            
            # Resize
            final_img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Create final canvas
            canvas = Image.new('RGB', (width, height), 'white')
            x = (width - final_img.width) // 2
            y = (height - final_img.height) // 2
            canvas.paste(final_img, (x, y))
            
            return canvas
            
    except Exception as e:
        print(f"Error in alternative signature processing: {e}")
        return None

# Test the alternative method
def test_alternative_method():
    signature_files = [
        "static/uploads/21000602400_signature.png",
        "static/uploads/12000602400_signature.png"
    ]
    
    for sig_file in signature_files:
        if os.path.exists(sig_file):
            print(f"\nTesting alternative method with {sig_file}:")
            result = process_signature_for_excel(sig_file)
            if result:
                output_path = f"alt_fixed_{os.path.basename(sig_file)}"
                result.save(output_path)
                print(f"✅ Alternative method result saved as {output_path}")

test_alternative_method()






def create_basic_excel_export(students, semester, academic_year):
    """Fallback Excel export without images"""
    try:
        # Create DataFrame
        df = pd.DataFrame(students)
        
        # Select and reorder columns
        columns = ['student_id', 'name', 'course', 'contact', 'guardian_name', 
                  'address', 'received_date', 'status', 'academic_year', 'semester']
        df = df[columns]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.close()
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = f"Semester {semester} - {academic_year}"
        
        # Add title
        ws['A1'] = f"Student ID History - {semester}{'st' if semester == 1 else 'nd'} Semester {academic_year}"
        ws['A2'] = f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(df)}"
        
        # Add headers starting from row 4
        headers = ['Student ID', 'Full Name', 'Course', 'Contact Number', 'Guardian Name', 
                  'Address', 'Received Date', 'Status', 'Academic Year', 'Semester']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.font = Font(bold=True)
        
        # Add data
        for row_idx, (_, row_data) in enumerate(df.iterrows(), 5):
            for col_idx, column in enumerate(columns, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = row_data.get(column, '')
        
        # Auto-adjust column widths
        for column_cells in ws.columns:
            length = max(len(str(cell.value or '')) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50)
        
        # Save workbook
        wb.save(temp_file.name)
        
        filename = f"student_history_{academic_year}_sem{semester}.xlsx"
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error creating basic Excel: {e}")
        # Final fallback to CSV
        df = pd.DataFrame(students)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
        df.to_csv(temp_file.name, index=False)
        
        filename = f"student_history_{academic_year}_sem{semester}.csv"
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )

def create_zip_export_simple(students, semester, academic_year):
    """Create a simple ZIP export with Excel and images"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Create Excel file first
        df = pd.DataFrame(students)
        excel_filename = f"student_history_{academic_year}_sem{semester}.xlsx"
        excel_path = os.path.join(temp_dir, excel_filename)
        
        # Simple Excel creation
        wb = Workbook()
        ws = wb.active
        ws.title = f"Semester {semester}"
        
        # Add headers
        headers = ['Student ID', 'Name', 'Course', 'Contact', 'Guardian', 'Address', 'Received Date', 'Status']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Add data
        for row_idx, student in enumerate(students, 2):
            ws.cell(row=row_idx, column=1, value=student['student_id'])
            ws.cell(row=row_idx, column=2, value=student['name'])
            ws.cell(row=row_idx, column=3, value=student['course'])
            ws.cell(row=row_idx, column=4, value=student['contact'])
            ws.cell(row=row_idx, column=5, value=student['guardian_name'])
            ws.cell(row=row_idx, column=6, value=student['address'])
            ws.cell(row=row_idx, column=7, value=student['received_date'])
            ws.cell(row=row_idx, column=8, value=student['status'])
        
        wb.save(excel_path)
        
        # Create ZIP file
        zip_filename = f"student_history_{academic_year}_sem{semester}_with_images.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Excel file
            zipf.write(excel_path, excel_filename)
            
            # Add images
            images_added = 0
            for student in students:
                student_id = student['student_id']
                
                # Add profile picture
                if student.get('profile_picture'):
                    profile_path = os.path.join("static", "uploads", student['profile_picture'])
                    if os.path.exists(profile_path):
                        zipf.write(profile_path, f"images/{student_id}/profile_{student['profile_picture']}")
                        images_added += 1
                
                # Add signature
                if student.get('signature'):
                    signature_path = os.path.join("static", "uploads", student['signature'])
                    if os.path.exists(signature_path):
                        zipf.write(signature_path, f"images/{student_id}/signature_{student['signature']}")
                        images_added += 1
                
                # Add barcode
                if student.get('barcode'):
                    barcode_path = os.path.join("static", "barcodes", student['barcode'])
                    if os.path.exists(barcode_path):
                        zipf.write(barcode_path, f"images/{student_id}/barcode_{student['barcode']}")
                        images_added += 1
            
            # Add README
            readme_content = f"""Student ID History Export
Academic Year: {academic_year}
Semester: {semester}
Total Students: {len(students)}
Images Included: {images_added}
Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Files:
- {excel_filename}: Student data
- images/[student_id]/: Student images
"""
            zipf.writestr("README.txt", readme_content)
        
        # Send the ZIP file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        # Fallback to Excel only
        return create_basic_excel_export(students, semester, academic_year)
    
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

# Add error handling middleware for large file downloads
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error during export'}), 500



# Add import functionality
@app.route('/import_student_history', methods=['POST'])
@login_required("admin")
def import_student_history():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    semester = request.form.get('semester', 1, type=int)
    academic_year = request.form.get('academic_year', '2025-2026')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    try:
        # Handle different file types
        if file.filename.endswith('.zip'):
            return handle_zip_import(file, semester, academic_year)
        elif file.filename.endswith(('.xlsx', '.xls')):
            return handle_excel_import(file, semester, academic_year)
        elif file.filename.endswith('.csv'):
            return handle_csv_import(file, semester, academic_year)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format. Please use CSV, Excel, or ZIP files.'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Import failed: {str(e)}'})

def handle_zip_import(file, semester, academic_year):
    """Handle ZIP file import with images"""
    # Create temporary directory
    temp_dir = os.path.join("static", "temp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Save and extract ZIP file
        zip_path = os.path.join(temp_dir, "import.zip")
        file.save(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find Excel/CSV file in extracted contents
        data_file = None
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.endswith(('.xlsx', '.xls', '.csv')) and not f.startswith('~'):
                    data_file = os.path.join(root, f)
                    break
            if data_file:
                break
        
        if not data_file:
            return jsonify({'success': False, 'error': 'No Excel or CSV file found in ZIP archive'})
        
        # Process the data file
        if data_file.endswith('.csv'):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)
        
        # Process images and data
        result = process_import_data(df, semester, academic_year, temp_dir)
        
        return jsonify(result)
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def handle_excel_import(file, semester, academic_year):
    """Handle Excel file import"""
    # Save file temporarily
    temp_dir = os.path.join("static", "temp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        file_path = os.path.join(temp_dir, "import.xlsx")
        file.save(file_path)
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        result = process_import_data(df, semester, academic_year)
        
        return jsonify(result)
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def handle_csv_import(file, semester, academic_year):
    """Handle CSV file import"""
    try:
        # Read CSV directly from memory
        df = pd.read_csv(file)
        
        result = process_import_data(df, semester, academic_year)
        
        return jsonify(result)
        
    except Exception as e:
        return {'success': False, 'error': f'CSV processing failed: {str(e)}'}

def process_import_data(df, semester, academic_year, image_dir=None):
    """Process the imported data and handle images"""
    # Validate required columns
    required_columns = ['student_id', 'name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {'success': False, 'error': f"Missing required columns: {', '.join(missing_columns)}"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        for index, row in df.iterrows():
            try:
                # Validate required fields
                if pd.isna(row['student_id']) or pd.isna(row['name']):
                    error_count += 1
                    errors.append(f"Row {index + 1}: Missing student_id or name")
                    continue
                
                student_id = str(row['student_id']).strip()
                name = str(row['name']).strip()
                
                # Get optional fields
                course = str(row.get('course', '')) if not pd.isna(row.get('course', '')) else ''
                contact = str(row.get('contact', '')) if not pd.isna(row.get('contact', '')) else ''
                guardian_name = str(row.get('guardian_name', '')) if not pd.isna(row.get('guardian_name', '')) else ''
                address = str(row.get('address', '')) if not pd.isna(row.get('address', '')) else ''
                
                # Handle images if image directory is provided
                profile_picture = None
                signature = None
                barcode = None
                
                if image_dir:
                    profile_picture, signature, barcode = process_student_images(student_id, image_dir)
                
                # Insert or update record
                query = """
                    INSERT INTO student_history 
                    (student_id, name, course, contact, guardian_name, address, 
                     received_date, academic_year, semester, profile_picture, signature, barcode)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    course = VALUES(course),
                    contact = VALUES(contact),
                    guardian_name = VALUES(guardian_name),
                    address = VALUES(address),
                    received_date = NOW(),
                    academic_year = VALUES(academic_year),
                    semester = VALUES(semester)
                """
                
                cursor.execute(query, (
                    student_id, name, course, contact, guardian_name, address,
                    academic_year, semester, profile_picture, signature, barcode
                ))
                
                success_count += 1
                
            except Exception as row_error:
                error_count += 1
                errors.append(f"Row {index + 1}: {str(row_error)}")
        
        conn.commit()
        
        result = {
            'success': True,
            'imported': success_count,
            'errors': error_count,
            'total': len(df)
        }
        
        if errors:
            result['error_details'] = errors[:10]  # Limit to first 10 errors
        
        return result
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': f'Database error: {str(e)}'}
        
    finally:
        cursor.close()
        conn.close()

def process_student_images(student_id, image_dir):
    """Process and copy student images from import directory"""
    profile_picture = None
    signature = None
    barcode = None
    
    # Look for student images in the extracted directory
    student_image_dir = os.path.join(image_dir, "images", student_id)
    
    if os.path.exists(student_image_dir):
        for filename in os.listdir(student_image_dir):
            file_path = os.path.join(student_image_dir, filename)
            
            if filename.startswith('profile_'):
                profile_picture = copy_image_to_uploads(file_path, f"{student_id}_profile")
            elif filename.startswith('signature_'):
                signature = copy_image_to_uploads(file_path, f"{student_id}_signature")
            elif filename.startswith('barcode_'):
                barcode = copy_image_to_barcodes(file_path, f"{student_id}_barcode")
    
    return profile_picture, signature, barcode

def copy_image_to_uploads(source_path, base_name):
    """Copy image to uploads directory with proper naming"""
    if not os.path.exists(source_path):
        return None
    
    # Get file extension
    _, ext = os.path.splitext(source_path)
    if not ext:
        ext = '.png'  # Default extension
    
    # Create unique filename
    filename = f"{base_name}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join("static", "uploads", filename)
    
    # Ensure uploads directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    
    return filename

def copy_image_to_barcodes(source_path, base_name):
    """Copy barcode image to barcodes directory"""
    if not os.path.exists(source_path):
        return None
    
    # Get file extension
    _, ext = os.path.splitext(source_path)
    if not ext:
        ext = '.png'  # Default extension
    
    # Create unique filename
    filename = f"{base_name}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join("static", "barcodes", filename)
    
    # Ensure barcodes directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    
    return filename

#----------------------------------------------------------------------------------------------------------------------------------


# ---------- Admin User Management ----------
# Purpose: Display and manage all users in the system
# This route provides an interface for administrators to manage user accounts

@login_required("admin")
def admin_get_users():
    try:
        # Get page number from query parameters (default to 1)
        page = int(request.args.get('page', 1))
        per_page = 10  # Number of users per page
        
        # Calculate offset for SQL query
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total count of users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Calculate total pages
        total_pages = ceil(total_users / per_page)
        
        # Get paginated users
        cursor.execute("""
            SELECT u.id, u.student_id, u.name, u.role, 
                   CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END as has_profile,
                   s.application_status
            FROM users u
            LEFT JOIN students s ON u.student_id = s.student_id
            ORDER BY u.role DESC, u.name ASC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Calculate range values (e.g., "Showing 1-10 of 100")
        start_range = offset + 1 if users else 0
        end_range = min(offset + per_page, total_users)
        
        return jsonify({
            'success': True,
            'users': users,
            'current_page': page,
            'total_pages': total_pages,
            'total_users': total_users,
            'start_range': start_range,
            'end_range': end_range
        })
        
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Update the existing admin_manage_users route to include pagination
@app.route('/admin/manage_users')
@login_required("admin")
def admin_manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of users per page
    offset = (page - 1) * per_page
    
    # Get total count of users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    
    # Calculate total pages
    total_pages = ceil(total_users / per_page)
    
    # Get paginated users
    cursor.execute("""
        SELECT u.id, u.student_id, u.name, u.role, 
               CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END as has_profile,
               s.application_status
        FROM users u
        LEFT JOIN students s ON u.student_id = s.student_id
        ORDER BY u.role DESC, u.name ASC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    users = cursor.fetchall()
    
    # Get admin profile if exists
    admin_id = session.get('user_id')
    cursor.execute("SELECT * FROM admin_profiles WHERE user_id = %s", (admin_id,))
    admin_profile = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template(
        "admin_manage_users.html", 
        users=users, 
        admin_profile=admin_profile,
        current_page=page,
        total_pages=total_pages,
        total_users=total_users
    )
#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Create a new user account
# This route allows administrators to create new student or admin accounts
@app.route('/admin/create_user', methods=['POST'])
@login_required("admin")
def admin_create_user():
    if request.method == 'POST':
        student_id = request.form.get('student_id').strip()
        
        # Check for separate name fields first
        first_name = request.form.get('first_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip() or None
        last_name = request.form.get('last_name', '').strip()
        
        # For backward compatibility, also check for full name
        full_name = request.form.get('name', '').strip()
        
        password = request.form.get('password').strip()
        role = request.form.get('role')
        
        # Determine name format
        if first_name or last_name:
            name_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name
            }
            display_name = get_full_name(name_data)
        elif full_name:
            name_data = full_name
            display_name = full_name
        else:
            flash("⚠️ Name is required!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        # Validate required fields
        if not all([student_id, display_name, password, role]):
            flash("⚠️ All fields are required!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        # Validate student ID format for students
        if role == 'student' and (len(student_id) != 11 or not student_id.isdigit()):
            flash("⚠️ Student ID must be exactly 11 digits!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if the ID already exists
            cursor.execute("SELECT id FROM users WHERE student_id = %s", (student_id,))
            if cursor.fetchone():
                flash("⚠️ User ID already exists!", "danger")
                return redirect(url_for('admin_manage_users'))
            
            # Insert user with name fields
            if isinstance(name_data, dict):
                cursor.execute("""
                    INSERT INTO users (student_id, name, first_name, middle_name, last_name, password, role) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (student_id, display_name, name_data.get('first_name'), 
                      name_data.get('middle_name'), name_data.get('last_name'), hashed_password, role))
            else:
                parsed = parse_name_input(name_data)
                cursor.execute("""
                    INSERT INTO users (student_id, name, first_name, middle_name, last_name, password, role) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (student_id, display_name, parsed['first_name'], 
                      parsed['middle_name'], parsed['last_name'], hashed_password, role))
            
            # If student role, create student record
            if role == 'student':
                insert_student_with_names(
                    cursor,
                    student_id,
                    name_data,
                    application_status='pending'
                )
            
            conn.commit()
            flash("✅ User created successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"⚠️ Error creating user: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_manage_users'))

print("✅ Updated student routes for name handling completed!")

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Update an existing user's information
# This route allows administrators to modify user details and passwords
@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
@login_required("admin")
def admin_update_user(user_id):
    if request.method == 'POST':
        name = request.form.get('name').strip()
        role = request.form.get('role')
        password = request.form.get('password').strip()
        
        # Validate required fields
        if not all([name, role]):
            flash("⚠️ Name and role are required!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if password:
                # Update with new password
                hashed_password = generate_password_hash(password)
                cursor.execute("""
                    UPDATE users SET name = %s, role = %s, password = %s
                    WHERE id = %s
                """, (name, role, hashed_password, user_id))
            else:
                # Update without changing password
                cursor.execute("""
                    UPDATE users SET name = %s, role = %s
                    WHERE id = %s
                """, (name, role, user_id))
            
            conn.commit()
            flash("✅ User updated successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"⚠️ Error updating user: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_manage_users'))
    
#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Delete a user account
# This route allows administrators to remove users from the system
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required("admin")
def admin_delete_user(user_id):
    if request.method == 'POST':
        # Prevent admin from deleting themselves
        if user_id == session.get('user_id'):
            flash("⚠️ You cannot delete your own account!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get user details before deletion
            cursor.execute("SELECT student_id, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                flash("⚠️ User not found!", "danger")
                return redirect(url_for('admin_manage_users'))
            
            # Delete user (cascade will handle related records)
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            
            conn.commit()
            flash("✅ User deleted successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"⚠️ Error deleting user: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_manage_users'))
    
    
#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Update admin profile information
# This route allows administrators to update their own profile details
@app.route('/admin/update_profile', methods=['POST'])
@login_required("admin")
def admin_update_profile():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        phone = request.form.get('phone').strip()
        position = request.form.get('position').strip()
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Validate email
        if not email or '@' not in email:
            flash("⚠️ Valid email is required!", "danger")
            return redirect(url_for('admin_manage_users'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check if changing password
            if current_password and new_password:
                # Verify current password
                cursor.execute("SELECT password FROM users WHERE id = %s", (session.get('user_id'),))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user['password'], current_password):
                    flash("⚠️ Current password is incorrect!", "danger")
                    return redirect(url_for('admin_manage_users'))
                
                # Update password
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                              (hashed_password, session.get('user_id')))
            
            # Check if admin profile exists
            cursor.execute("SELECT id FROM admin_profiles WHERE user_id = %s", (session.get('user_id'),))
            profile = cursor.fetchone()
            
            if profile:
                # Update existing profile
                cursor.execute("""
                    UPDATE admin_profiles 
                    SET email = %s, phone = %s, position = %s, updated_at = NOW()
                    WHERE user_id = %s
                """, (email, phone, position, session.get('user_id')))
            else:
                # Create new profile
                cursor.execute("""
                    INSERT INTO admin_profiles (user_id, email, phone, position, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (session.get('user_id'), email, phone, position))
            
            conn.commit()
            flash("✅ Profile updated successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"⚠️ Error updating profile: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_manage_users'))


#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: API endpoint to get all students
# This route returns a list of all students in JSON format for AJAX requests
@app.route('/get_all_students', methods=['GET'])
@login_required("admin")
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")  # Make sure this returns ALL students
    students = cursor.fetchall()

    conn.close()
    return jsonify(students)


#----------------------------------------------------------------------------------------------------------------------------------

# ---------- Admin Support Messages ----------
# Purpose: Display all support messages for admin review
# This route provides an interface for administrators to manage support tickets
@app.route('/admin/support_messages')
@login_required("admin")
def admin_support_messages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all support messages with student information
    cursor.execute("""
        SELECT sm.*, u.name as student_name 
        FROM support_messages sm
        JOIN users u ON sm.student_id = u.student_id
        ORDER BY 
            CASE 
                WHEN sm.status = 'pending' THEN 1
                WHEN sm.status = 'in_progress' THEN 2
                WHEN sm.status = 'resolved' THEN 3
            END,
            sm.created_at DESC
    """)
    messages = cursor.fetchall()
    
    # Get count of unread messages
    cursor.execute("SELECT COUNT(*) as unread FROM support_messages WHERE status = 'pending'")
    unread_count = cursor.fetchone()['unread']
    
    cursor.close()
    conn.close()
    
    return render_template("admin_support_messages.html", messages=messages, unread_count=unread_count)

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: API endpoint to get count of unread support messages
# This route returns the number of pending support messages for real-time notifications
@app.route('/admin/get_unread_count')
@login_required("admin")
def get_unread_count():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as unread FROM support_messages WHERE status = 'pending'")
    unread_count = cursor.fetchone()['unread']
    
    cursor.close()
    conn.close()
    
    return jsonify({"unread_count": unread_count})

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Display a specific support message and its history
# This route allows administrators to view and respond to support tickets
@app.route('/admin/view_message/<int:message_id>')
@login_required("admin")
def admin_view_message(message_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get message details
    cursor.execute("""
        SELECT sm.*, u.name as student_name 
        FROM support_messages sm
        JOIN users u ON sm.student_id = u.student_id
        WHERE sm.id = %s
    """, (message_id,))
    message = cursor.fetchone()
    
    if not message:
        cursor.close()
        conn.close()
        flash("Message not found", "danger")
        return redirect(url_for('admin_support_messages'))
    
    # Get message history
    cursor.execute("""
               SELECT 
                    h.*,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'Admin'
                        ELSE COALESCE(u.name, 'Unknown')
                    END as responder_name,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'admin'
                        ELSE COALESCE(u.role, 'unknown')
                    END as responder_role
                FROM support_message_history h
                LEFT JOIN users u ON 
                    (h.response_by NOT LIKE 'ADMIN_%%' AND h.response_by = u.student_id)
                WHERE h.message_id = %s
                ORDER BY h.created_at ASC
    """, (message_id,))
    history = cursor.fetchall()
    
    # If message is pending, mark as in_progress
    if message['status'] == 'pending':
        cursor.execute("UPDATE support_messages SET status = 'in_progress' WHERE id = %s", (message_id,))
        conn.commit()
        message['status'] = 'in_progress'
    
    cursor.close()
    conn.close()
    
    return render_template("admin_view_message.html", message=message, history=history)

#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Handle admin responses to support messages
# This route processes admin replies and updates message status
@app.route('/admin/respond_message/<int:message_id>', methods=['POST'])
@login_required("admin")
def admin_respond_message(message_id):
    if request.method == 'POST':
        try:
            response = request.form.get('response')
            status = request.form.get('status')
            
            if not response:
                return jsonify({"success": False, "error": "Response cannot be empty"}), 400
            
            admin_id = session.get('student_id') or f"ADMIN_{session.get('user_id')}"
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Insert new response
            cursor.execute("""
                INSERT INTO support_message_history 
                (message_id, response_by, response, responder_role, created_at)
                VALUES (%s, %s, %s, 'admin', NOW())
            """, (message_id, admin_id, response))
            
            # Update message status
            cursor.execute("""
                UPDATE support_messages 
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """, (status, message_id))
            
            # Get updated message history
            cursor.execute("""
               SELECT 
                    h.*,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'Admin'
                        ELSE COALESCE(u.name, 'Unknown')
                    END as responder_name,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'admin'
                        ELSE COALESCE(u.role, 'unknown')
                    END as responder_role
                FROM support_message_history h
                LEFT JOIN users u ON 
                    (h.response_by NOT LIKE 'ADMIN_%%' AND h.response_by = u.student_id)
                WHERE h.message_id = %s
                ORDER BY h.created_at ASC
            """, (message_id,))
            history = cursor.fetchall()
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'status': status,
                'history': [{
                    'id': item['id'],
                    'response': item['response'],
                    'responder_name': item['responder_name'],
                    'responder_role': item['responder_role'],
                    'created_at': item['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                } for item in history]
            })
            
        except Exception as e:
            conn.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
        finally:
            cursor.close()
            conn.close()



# ---------- Auto-reply and Seen Status ----------

# Purpose: Mark a message as seen by admin
# This route updates the seen status when an admin views a message
@app.route('/admin/mark_message_seen/<int:message_id>', methods=['POST'])
@login_required("admin")
def mark_message_seen(message_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the main message
        cursor.execute("""
            UPDATE support_messages 
            SET is_seen = TRUE 
            WHERE id = %s
        """, (message_id,))
        
        # Update all student responses in history
        cursor.execute("""
            UPDATE support_message_history 
            SET is_seen = TRUE 
            WHERE message_id = %s AND responder_role = 'student'
        """, (message_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error marking message as seen: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Purpose: Generate auto-reply for new student messages
# This function creates an AI-like response when a student submits a new message
# Enhanced auto-reply function with more keywords and better detection
def generate_auto_reply(subject, message):
    """Generate an automated response based on the message content"""
    # Convert to lowercase for case-insensitive matching
    message_text = (subject + " " + message).lower()
    
    # Comprehensive keyword dictionary with targeted responses
    keywords = {
        # ID-related keywords
        "id": "Thank you for your inquiry about student IDs. Your ID application status can be checked in your dashboard. If you're experiencing issues with your ID, please provide more details so we can assist you better.",
        "card": "Thank you for your message about your student card. If you need a replacement card or have issues with your current one, please provide your student number and the specific problem you're experiencing.",
        "identification": "Thank you for your inquiry about student identification. Our support team will assist you with your ID-related concerns shortly.",
        
        # Payment-related keywords
        "payment": "Thank you for your message about payments. For payment-related inquiries. Our finance team will review your concern as soon as possible.",
        "fee": "Thank you for your inquiry about fees. For fee-related questions, please specify which program or service you're asking about. We'll provide you with the most up-to-date information once an admin reviews your message.",
        "tuition": "Thank you for your message regarding tuition. Our finance department will review your inquiry and respond shortly. If you have a specific payment question, please include any relevant reference numbers.",
        "bill": "Thank you for your message about billing. Our finance team will review your inquiry and respond as soon as possible. For faster assistance, please include any relevant invoice numbers or payment details.",
        

        
        # Course-related keywords
        "course": "Thank you for your course-related inquiry. Please specify which course you're asking about and what information you need. An admin will provide you with detailed information soon.",
        "subject": "Thank you for your inquiry about subjects. Our academic advisors will review your message and respond shortly. For specific subject questions, please include the subject code if available.",
        "module": "Thank you for your message about modules. Our academic team will review your inquiry and respond as soon as possible. For faster assistance, please specify which module you're referring to.",
        

        # General help keywords
        "help": "Thank you for reaching out for help. To assist you better, please provide more specific details about your concern. Our support team will review your message and respond as soon as possible.",
        "support": "Thank you for contacting support. Our team will review your inquiry and respond shortly. For faster assistance, please provide specific details about your concern.",
        "assist": "Thank you for your message. Our support team is here to assist you and will respond to your inquiry as soon as possible. For faster assistance, please provide specific details about your concern.",
        
        # Follow-up keywords
        "follow up": "Thank you for your follow-up message. Our team will review your previous conversation and respond to your inquiry as soon as possible. For faster assistance, please provide your previous ticket number if available.",
        "followup": "Thank you for your follow-up inquiry. Our support team will review your message and respond shortly. If you're following up on a specific issue, please include any reference numbers from previous communications.",
        "status": "Thank you for your status inquiry. Our team will check on your request and provide you with an update as soon as possible. For faster assistance, please include any reference numbers from previous communications.",
        
        # Update keywords
        "update": "Thank you for requesting an update. Our team will review your inquiry and provide you with the latest information as soon as possible. For faster assistance, please specify which matter you need an update on.",
        "progress": "Thank you for your inquiry about progress. Our team will check on your request and provide you with an update as soon as possible. For faster assistance, please include any reference numbers from previous communications.",
        "news": "Thank you for your inquiry about updates. Our team will provide you with the latest information as soon as possible. For faster assistance, please specify which matter you need information on."
    }
    
    # Check for keywords in the message text
    for keyword, response in keywords.items():
        if keyword in message_text:
            return response
    
    # Default response if no keywords match
    return "Thank you for your message. Our support team will review your inquiry and respond as soon as possible. Please check back later for updates."




#------------------------------------------------------STUDENT SIDE-------------------------------------------------------------------------------------------------------------

# ---------- Student Dashboard ----------


# Purpose: Display the main student dashboard
# This is the central hub for students to access all system features
@app.route('/student_dashboard')
@login_required("student")
def student_dashboard():
    if 'student_id' not in session:
        flash("⚠️ Session expired or invalid. Please log in again.", "danger")
        return redirect(url_for("login"))

    student_id = session.get('student_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *, first_name, middle_name, last_name, name 
        FROM students WHERE student_id = %s
    """, (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student:
        flash("❌ No student record found. Please complete your student ID application.", "danger")
        return redirect(url_for("apply_student_id"))

    # Check if profile is incomplete (missing essential fields)
    required_fields = ["profile_picture", "signature"]
    if any(not student[field] for field in required_fields):
        flash("⚠️ Please complete your profile before accessing the dashboard.", "warning")
        return redirect(url_for("complete_student_profile"))

    # Store student details in session for quick access
    session.update({
        "application_status": student["application_status"],
        "name": get_full_name(student),  # Use helper function
        "course": student["course"],
        "contact": student["contact"],
        "guardian_name": student["guardian_name"],
        "address": student["address"],
        "profile_picture": student["profile_picture"],
        "signature": student["signature"]
    })

    # Add full name to student record for template
    student['full_name'] = get_full_name(student)

    return render_template("student_dashboard.html", student=student)

print("✅ Updated Flask routes for name handling completed!")


# Add these routes to your existing app.py file

# Student routes for Lost ID requests

@app.route('/lost_id_request')
@login_required("student")
def lost_id_request():
    """Display the lost ID request form"""
    student_id = session.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get student information
    cursor.execute("""
        SELECT s.*, u.name as student_name
        FROM students s
        JOIN users u ON s.student_id = u.student_id
        WHERE s.student_id = %s
    """, (student_id,))
    student = cursor.fetchone()
    
    # Check if student has any pending lost ID requests
    cursor.execute("""
        SELECT id, status, created_at
        FROM lost_id_requests
        WHERE student_id = %s AND status IN ('pending', 'verified')
        ORDER BY created_at DESC
        LIMIT 1
    """, (student_id,))
    pending_request = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template("lost_id_request.html", student=student, pending_request=pending_request)

@app.route('/submit_lost_id_request', methods=['POST'])
@login_required("student")
def submit_lost_id_request():
    """Process lost ID request submission"""
    try:
        student_id = session.get('student_id')
        reason = request.form.get('reason')
        affidavit = request.files.get('affidavit')
        
        # Validation
        if not reason or not reason.strip():
            return jsonify({'success': False, 'error': 'Reason is required'})
        
        if not affidavit or affidavit.filename == '':
            return jsonify({'success': False, 'error': 'Affidavit document is required'})
        
        # Check if student already has a pending request
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id FROM lost_id_requests
            WHERE student_id = %s AND status IN ('pending', 'verified')
        """, (student_id,))
        existing_request = cursor.fetchone()
        
        if existing_request:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'You already have a pending lost ID request'})
        
        # Validate file
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        file_ext = affidavit.filename.rsplit('.', 1)[1].lower() if '.' in affidavit.filename else ''
        
        if file_ext not in allowed_extensions:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload PDF or image files only.'})
        
        # Check file size
        affidavit.seek(0, 2)
        file_size = affidavit.tell()
        affidavit.seek(0)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'File size must be less than 10MB'})
        
        # Save file
        filename = secure_filename(f"{student_id}_affidavit_{int(time.time())}.{file_ext}")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        affidavit.save(file_path)
        
        # Insert request into database
        cursor.execute("""
            INSERT INTO lost_id_requests (student_id, reason, affidavit_file, status, created_at)
            VALUES (%s, %s, %s, 'pending', NOW())
        """, (student_id, reason, filename))
        
        request_id = cursor.lastrowid
        
        # Get student information for email
        cursor.execute("""
            SELECT s.email, u.name as student_name
            FROM students s
            JOIN users u ON s.student_id = u.student_id
            WHERE s.student_id = %s
        """, (student_id,))
        student = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send confirmation email
        if student and student.get('email'):
            try:
                msg = Message(
                    subject=f"Lost ID Request Submitted - Request #{request_id}",
                    recipients=[student['email']],
                    body=f"""Dear {student['student_name']},

Your Lost ID Request has been successfully submitted.

Request ID: {request_id}
Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your request will be reviewed by TSD after OSAS verifies your submitted documents. You will receive updates on the status of your request via email.

Please keep your Request ID for reference.

Thank you,
Technical Support Department
ACLC College"""
                )
                mail.send(msg)
            except Exception as email_error:
                print(f"Failed to send confirmation email: {email_error}")
        
        return jsonify({
            'success': True,
            'request_id': f"LID-{request_id:06d}",
            'message': 'Lost ID request submitted successfully'
        })
        
    except Exception as e:
        print(f"Error submitting lost ID request: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while submitting your request'})

@app.route('/my_lost_id_requests')
@login_required("student")
def my_lost_id_requests():
    """Display student's lost ID requests"""
    student_id = session.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all lost ID requests for this student
    cursor.execute("""
        SELECT * FROM lost_id_requests
        WHERE student_id = %s
        ORDER BY created_at DESC
    """, (student_id,))
    requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("my_lost_id_requests.html", requests=requests)



#----------------------------------------------------------------------------------------------------------------------------------




# ---------- Apply for Student ID ----------
# Purpose: Handle student ID application process
# This route collects all necessary information and files for ID creation
@app.route('/apply_student_id', methods=['GET', 'POST'])
@login_required("student")
def apply_student_id():
    user_id = session.get('user_id')
    student_id = session.get('student_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        course = request.form.get("course")
        contact = request.form.get("contact")
        guardian = request.form.get("guardian")
        address = request.form.get("address")

        profile_picture = request.files.get("profile_picture")
        signature = request.files.get("signature")

        if not all([course, contact, guardian, address, profile_picture, signature]):
            flash("⚠️ All fields are required!", "danger")
            return redirect(url_for("apply_student_id"))

        # ✅ Save profile picture and signature
        profile_picture_filename = secure_filename(profile_picture.filename)
        signature_filename = secure_filename(signature.filename)

        profile_picture.save(os.path.join(app.config["UPLOAD_FOLDER"], profile_picture_filename))
        signature.save(os.path.join(app.config["UPLOAD_FOLDER"], signature_filename))

        # ✅ Generate Barcode & Save to Static Directory
        barcode_filename = f"{student_id}.png"
        barcode_path = os.path.join("static", "barcodes", barcode_filename)

        # ✅ Ensure barcode folder exists
        os.makedirs("static/barcodes", exist_ok=True)

        # ✅ Generate barcode and save as image
        CODE39 = get_barcode_class('code39')
        generated_barcode = Code39(student_id.strip(), writer=ImageWriter(), add_checksum=False)
        generated_barcode.save(barcode_path.replace(".png", ""), {"format": "PNG"})


        # ✅ Store barcode filename in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students 
            SET course=%s, contact=%s, guardian_name=%s, address=%s, 
                profile_picture=%s, signature=%s, barcode=%s, application_status='Processing'
            WHERE student_id=%s
        """, (course, contact, guardian, address, profile_picture_filename, signature_filename, barcode_filename, student_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Profile updated successfully! Your application is now being processed.", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("apply_student_id.html", student=student)


#----------------------------------------------------------------------------------------------------------------------------------


# Purpose: Update student information
# This route processes form submissions to update student details
from barcode import Code39
from barcode.writer import ImageWriter
import os

def generate_barcode(usn):
    """Generate a Code39 barcode PNG from the student's USN"""
    barcode_dir = os.path.join("static", "barcodes")
    os.makedirs(barcode_dir, exist_ok=True)

    barcode_filename = f"{usn}.png"
    barcode_path = os.path.join(barcode_dir, barcode_filename)

    code39 = Code39(usn, writer=ImageWriter(), add_checksum=False)
    code39.save(os.path.splitext(barcode_path)[0])  # remove .png before saving

    return barcode_filename


@app.route('/update_student_info', methods=['POST'])
def update_student_info():
    user_id = session.get('user_id')
    student_id = session.get('student_id')

    if not student_id:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for("login"))

    # Get name data from form - check for separate fields first
    first_name = request.form.get("first_name", "").strip()
    middle_name = request.form.get("middle_name", "").strip() or None
    last_name = request.form.get("last_name", "").strip()
    
    # For backward compatibility, also check for full name
    full_name = request.form.get("name", "").strip()
    
    # Determine which format we're using
    if first_name or last_name:
        # New format with separate fields
        name_data = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name
        }
    elif full_name:
        # Old format - parse the full name
        name_data = full_name
    else:
        flash("Name is required.", "danger")
        return redirect(url_for("complete_student_profile"))

    # Get other form data
    course = request.form.get("course")
    contact = request.form.get("contact")
    guardian_name = request.form.get("guardian_name")
    address = request.form.get("address")

    profile_picture = request.files.get("profile_picture")
    signature_data = request.form.get("signature")

    if not profile_picture:
        flash("Profile picture is required.", "danger")
        return redirect(url_for("complete_student_profile"))

    # Save profile picture
    profile_picture_filename = secure_filename(profile_picture.filename)
    profile_path = os.path.join(app.config["UPLOAD_FOLDER"], profile_picture_filename)
    profile_picture.save(profile_path)

    # Process signature
    signature_filename = None
    if signature_data:
        signature_filename = process_esignature(signature_data, student_id)

    if not signature_filename:
        flash("Signature is required. Please draw your signature.", "danger")
        return redirect(url_for("complete_student_profile"))

    # Validate profile picture
    if photo_validator and photo_validator.model:
        result = photo_validator.validate(image_path=profile_path)
    else:
        result = face_validator.validate_from_file(profile_path)

    if not result.get("valid", False):
        flash(f"Profile picture validation failed: {result.get('error', 'Unknown error')}", "danger")
        return redirect(url_for("complete_student_profile"))

    # Generate barcode
    barcode_filename = generate_barcode(student_id)

    # Save to database using the new helper function
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        update_student_with_names(
            cursor, 
            student_id, 
            name_data,
            course=course,
            contact=contact,
            guardian_name=guardian_name,
            address=address,
            profile_picture=profile_picture_filename,
            signature=signature_filename,
            barcode=barcode_filename,
            application_status='pending'
        )
        
        conn.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for("student_dashboard"))
        
    except Exception as e:
        conn.rollback()
        flash(f"Error updating profile: {str(e)}", "danger")
        return redirect(url_for("complete_student_profile"))
    finally:
        cursor.close()
        conn.close()

#----------------------------------------------------------------------------------------------------------------------------------


# ---------- Complete Info ----------
# Purpose: Allow students to complete their profile information
# This route handles both displaying and processing the profile completion form

@app.route('/complete_student_profile', methods=['GET', 'POST'])
@login_required("student")
def complete_student_profile():
    if 'student_id' not in session:
        flash("Please log in again to continue your profile completion.", "danger")
        return redirect(url_for('login'))

    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    if request.method == 'POST':
        profile_picture = request.files.get("profile_picture")
        signature = request.files.get("signature")

        if not all([profile_picture, signature]):
            flash("Profile picture and signature are required", "danger")
            return redirect(url_for('complete_student_profile'))

        # Save profile picture
        profile_picture_filename = secure_filename(f"{student_id}_profile.png")
        profile_path = os.path.join(app.config["UPLOAD_FOLDER"], profile_picture_filename)
        profile_picture.save(profile_path)

        # Save signature
        signature_filename = secure_filename(f"{student_id}_signature.png")
        signature_path = os.path.join(app.config["UPLOAD_FOLDER"], signature_filename)
        signature.save(signature_path)

        # Validate profile picture
        if photo_validator and photo_validator.model:
            result = photo_validator.validate(image_path=profile_path)
        else:
            result = face_validator.validate_from_file(profile_path)

        if not result.get("valid", False):
            flash(f"Profile picture validation failed: {result.get('error', 'Unknown error')}", "danger")
            return redirect(url_for('complete_student_profile'))

        # ✅ Update student record
        cursor.execute("""
            UPDATE students 
            SET profile_picture = %s, 
                signature = %s,
                application_status = 'pending'
            WHERE student_id = %s
        """, (profile_picture_filename, signature_filename, student_id))
        conn.commit()

        flash("✅ Profile submitted successfully! Your application is now being processed.", "success")
        return redirect(url_for('student_dashboard'))

    cursor.close()
    conn.close()
    return render_template("complete_student_profile.html", student=student)

    

#----------------------------------------------------------------------------------------------------------------------------------


# ---------- Student Application Status ----------
# Purpose: Display the current status of a student's ID application
# This route shows students where their application is in the process
@app.route('/my_application_status')
@login_required("student")
def my_application_status():
    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT application_status FROM students WHERE student_id = %s", (session['student_id'],))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return render_template("my_application_status.html", status=student["application_status"])
    else:
        flash("❌ No application found.", "danger")
        return redirect(url_for("student_dashboard"))
    
#----------------------------------------------------------------------------------------------------------------------------------


# ---------- Contact Support ----------
# Purpose: API endpoint to submit support messages
# This route handles AJAX requests to create new support tickets
@app.route('/submit_support_message', methods=['POST'])
@login_required("student")
def submit_support_message():
    if request.method == 'POST':
        try:
            data = request.json
            subject = data.get('subject')
            message = data.get('message')
            student_id = session.get('student_id')
            
            if not all([subject, message, student_id]):
                return jsonify({"success": False, "error": "Missing required fields"}), 400
            
            # Connect to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert support message into database
            cursor.execute("""
                INSERT INTO support_messages (student_id, subject, message, status, created_at)
                VALUES (%s, %s, %s, 'pending', NOW())
            """, (student_id, subject, message))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": "Your message has been sent successfully!"})
            
        except Exception as e:
            print(f"Error submitting support message: {str(e)}")
            return jsonify({"success": False, "error": "An error occurred while sending your message"}), 500
    
    return jsonify({"success": False, "error": "Invalid request method"}), 405


#----------------------------------------------------------------------------------------------------------------------------------






# ---------- Student Support Messages ----------
# Purpose: Display all support messages for a student
# This route shows students their support ticket history
@app.route('/student/my_support_messages')
@login_required("student")
def student_support_messages():
    student_id = session.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all support messages for this student
    cursor.execute("""
        SELECT * FROM support_messages
        WHERE student_id = %s
        ORDER BY created_at DESC
    """, (student_id,))
    messages = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("student_support_messages.html", messages=messages)

#---------------------------------------------------------------------------------------------------------------------------------

# Purpose: Display a specific support message and its history
# This route allows students to view details of their support tickets
@app.route('/student/view_message/<int:message_id>')
@login_required("student")
def student_view_message(message_id):
    student_id = session.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get message details
    cursor.execute("""
        SELECT * FROM support_messages
        WHERE id = %s AND student_id = %s
    """, (message_id, student_id))
    message = cursor.fetchone()
    
    if not message:
        cursor.close()
        conn.close()
        flash("Message not found", "danger")
        return redirect(url_for('student_support_messages'))
    
    # Get message history
    cursor.execute("""
               SELECT 
                    h.*,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'Admin'
                        ELSE COALESCE(u.name, 'Unknown')
                    END as responder_name,
                    CASE 
                        WHEN h.response_by LIKE 'ADMIN_%%' THEN 'admin'
                        ELSE COALESCE(u.role, 'unknown')
                    END as responder_role
                FROM support_message_history h
                LEFT JOIN users u ON 
                    (h.response_by NOT LIKE 'ADMIN_%%' AND h.response_by = u.student_id)
                WHERE h.message_id = %s
                ORDER BY h.created_at ASC
    """, (message_id,))
    history = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("student_view_message.html", message=message, history=history)

#----------------------------------------------------------------------------------------------------------------------------------


# Purpose: Modified student_reply_message to add auto-reply
# This route handles student message submissions and generates auto-replies
@app.route('/student/reply_message/<int:message_id>', methods=['POST'])
@login_required("student")
def student_reply_message(message_id):
    if request.method == 'POST':
        response = request.form.get('response')
        student_id = session.get('student_id')
        
        if not response:
            flash("Response cannot be empty", "danger")
            return redirect(url_for('student_view_message', message_id=message_id))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Verify message belongs to student
            cursor.execute("SELECT id, subject FROM support_messages WHERE id = %s AND student_id = %s", 
                          (message_id, student_id))
            message = cursor.fetchone()
            
            if not message:
                flash("Message not found", "danger")
                return redirect(url_for('student_support_messages'))
            
            # Add response to history
            cursor.execute("""
                INSERT INTO support_message_history (message_id, response_by, response, created_at, is_seen)
                VALUES (%s, %s, %s, NOW(), FALSE)
            """, (message_id, student_id, response))
            
            # Update message status to pending if it was resolved
            cursor.execute("""
                UPDATE support_messages 
                SET status = CASE WHEN status = 'resolved' THEN 'pending' ELSE status END,
                    updated_at = NOW(),
                    is_seen = FALSE
                WHERE id = %s
            """, (message_id,))
            
            # Generate auto-reply if needed
            auto_reply = generate_auto_reply(message['subject'], response)
            
            # Add auto-reply to the database
            cursor.execute("""
                UPDATE support_messages
                SET auto_reply = %s
                WHERE id = %s
            """, (auto_reply, message_id))
            
            conn.commit()
            flash("Reply sent successfully", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"Error sending reply: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('student_view_message', message_id=message_id))
    
#----------------------------------------------------------------------------------------------------------------------------------

# Purpose: Check for new messages in real-time
# This route enables real-time updates of support conversations
@app.route('/check_new_messages/<int:message_id>/<timestamp>')
@login_required()
def check_new_messages(message_id, timestamp):
    """Check if there are new messages since the given timestamp"""
    try:
        # Convert timestamp to datetime
        last_check = datetime.fromtimestamp(int(timestamp))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if there are new messages in the history
        cursor.execute("""
            SELECT COUNT(*) as new_count 
            FROM support_message_history 
            WHERE message_id = %s AND created_at > %s
        """, (message_id, last_check))
        
        result = cursor.fetchone()
        new_count = result['new_count'] if result else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "has_new": new_count > 0,
            "new_count": new_count,
            "current_timestamp": int(datetime.now().timestamp())
        })
        
    except Exception as e:
        print(f"Error checking new messages: {str(e)}")
        return jsonify({
            "has_new": False,
            "error": str(e),
            "current_timestamp": int(datetime.now().timestamp())
        })
    




#----------------------------------------------------------------------------------------------------------------------------------

# ---------- Logout ----------
# Purpose: Handle user logout
# This route clears the session and redirects to the login page
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Purpose: Main entry point for the application
# This code runs the Flask application when the script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
