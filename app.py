from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import mysql.connector
from functools import wraps
from werkzeug.utils import secure_filename
import os
import barcode
from barcode.writer import ImageWriter
from flask import send_from_directory
import cv2
import numpy as np
import easyocr
from concurrent.futures import ThreadPoolExecutor
import base64
import re
from PIL import Image
import io
import json
# Add this import at the top of the file with your other imports
import jinja2
from markupsafe import Markup

# Import the OpenCV-based face validation module
from face_validation import FaceValidator, process_profile_picture

# Import the trainable validator
from trainable_validator import TrainablePhotoValidator
from datetime import datetime

# ✅ Define Flask App
app = Flask(__name__, static_folder="static")
app.secret_key = "123"
app.permanent_session_lifetime = timedelta(hours=2)

# Add this code after your app initialization (after app = Flask(...))
@app.template_filter('nl2br')
def nl2br_filter(s):
  if s is None:
      return ''
  return Markup(s.replace('\n', '<br>'))

# ✅ Configure File Uploads
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Create directories for training data
TRAINING_FOLDER = "training"
VALID_PHOTOS_DIR = os.path.join(TRAINING_FOLDER, "valid")
INVALID_PHOTOS_DIR = os.path.join(TRAINING_FOLDER, "invalid")
MODEL_PATH = os.path.join(TRAINING_FOLDER, "photo_validator_model.joblib")

os.makedirs(VALID_PHOTOS_DIR, exist_ok=True)
os.makedirs(INVALID_PHOTOS_DIR, exist_ok=True)

# ✅ Initialize the trainable validator
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

# ✅ Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "studentid"
}

# ✅ Database Connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ✅ Authentication Middleware
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

# ✅ Load EasyOCR model once to avoid reloading every request
reader = easyocr.Reader(['en'], gpu=False)

# ✅ Check if an image is blurry
def is_blurry(image, threshold=80):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

# ✅ Check if a face is detected using OpenCV's Haar cascade
def is_face_detected(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0

# ✅ Check if the background is plain using edge detection
def is_plain_background(image_path, edge_threshold=5000):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 50, 150)
    return np.count_nonzero(edges) < edge_threshold

# ✅ Check if a signature is valid using OCR
def is_signature_valid(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
    white_pixels = np.count_nonzero(binary)
    return 1000 < white_pixels < 20000  # Adjust values if necessary

# ✅ Process Electronic Signature
def process_esignature(base64_data, student_id):
    """
    Process electronic signature from canvas:
    1. Convert base64 to image
    2. Remove background
    3. Auto-correct signature (enhance contrast, smooth edges)
    4. Save processed signature
    """
    try:
        # Extract the base64 data (remove the data:image/png;base64, prefix)
        base64_data = re.sub('^data:image/.+;base64,', '', base64_data)
        
        # Convert base64 to image
        img_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(img)
        
        # If image has alpha channel, use it for transparency
        if img_array.shape[2] == 4:
            # Extract alpha channel
            alpha = img_array[:, :, 3]
            # Convert to RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        else:
            # Create mask based on white background
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            _, alpha = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Remove background (make white pixels transparent)
        # Create a new RGBA image
        height, width = img_array.shape[:2]
        rgba = np.zeros((height, width, 4), dtype=np.uint8)
        rgba[:, :, 0:3] = img_array
        rgba[:, :, 3] = alpha
        
        # Enhance contrast to make signature more visible
        alpha_enhanced = cv2.equalizeHist(alpha)
        
        # Apply slight Gaussian blur to smooth edges
        alpha_enhanced = cv2.GaussianBlur(alpha_enhanced, (3, 3), 0)
        
        # Update alpha channel with enhanced version
        rgba[:, :, 3] = alpha_enhanced
        
        # Convert back to PIL Image
        processed_img = Image.fromarray(rgba)
        
        # Save the processed signature
        filename = f"{student_id}_signature.png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        processed_img.save(filepath)
        
        return filename
    except Exception as e:
        print(f"Error processing signature: {str(e)}")
        return None

# Create a global instance of the validator
face_validator = FaceValidator()

# ✅ Validate Image (Profile & Signature) - UPDATED to use trainable validator
@app.route('/validate_image/<image_type>', methods=['POST'])
def validate_image(image_type):
    if image_type not in ["profile", "signature"]:
        return jsonify({"valid": False, "error": "Invalid image type"}), 400

    file = request.files.get(image_type)
    if not file:
        return jsonify({"valid": False, "error": "No image uploaded"}), 400

    # Save the file before processing
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(image_path)

    # Use ThreadPoolExecutor to process the image in parallel
    with ThreadPoolExecutor() as executor:
        if image_type == "profile":
            # Check if we have a trained model
            if photo_validator and photo_validator.model:
                # Use the trainable validator
                file_content = file.read()
                file.seek(0)  # Reset file pointer
                
                # Validate using the trained model
                result = photo_validator.validate(image_path=image_path)
                
                # Make result JSON serializable
                result = make_json_serializable(result)
                
                return jsonify(result)
            else:
                # Fall back to the original validation if no model is available
                face_result = executor.submit(is_face_detected, image_path)
                bg_result = executor.submit(is_plain_background, image_path)
                blur_result = executor.submit(is_blurry, cv2.imread(image_path))

                if not face_result.result():
                    return jsonify({"valid": False, "error": "Profile picture must contain a visible face."})

                if not bg_result.result():
                    return jsonify({"valid": False, "error": "Profile picture must have a plain background."})

                if blur_result.result():
                    return jsonify({"valid": False, "error": "Profile picture is blurry."})

        elif image_type == "signature":
            signature_result = executor.submit(is_signature_valid, image_path)
            if not signature_result.result():
                return jsonify({"valid": False, "error": "Signature is not clear or readable."})

    return jsonify({"valid": True})

# Helper function to make objects JSON serializable
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

# ✅ Process and Save Electronic Signature
@app.route('/process_signature', methods=['POST'])
def process_signature():
    if 'student_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    data = request.json
    signature_data = data.get('signature')
    student_id = session.get('student_id')
    
    if not signature_data:
        return jsonify({"success": False, "error": "No signature data provided"}), 400
    
    # Process the signature
    filename = process_esignature(signature_data, student_id)
    
    if not filename:
        return jsonify({"success": False, "error": "Failed to process signature"}), 500
    
    # Update the database with the new signature
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE students SET signature = %s WHERE student_id = %s", 
                      (filename, student_id))
        conn.commit()
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# NEW: Admin route to train the photo validator model
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

# NEW: Admin route to upload training data
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

# ---------- Home Page ----------
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/ID_section')
def ID_section():
    return render_template("ID_section.html")

@app.route('/sample_layout')
@login_required("admin")
def sample_layout():
    return render_template("sample_layout.html")
# ---------- User Authentication ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        usn = request.form.get('usn').strip()  # USN must be unique
        password = request.form.get('password').strip()
        confirm_password = request.form.get('confirm_password').strip()

        # ✅ Validate required fields
        if not all([name, usn, password, confirm_password]):
            flash("⚠️ All fields are required!", "danger")
            return redirect(url_for('register'))

        # ✅ Validate USN format (must be exactly 11 digits)
        if len(usn) != 11 or not usn.isdigit():
            flash("⚠️ USN must be exactly 11 digits!", "danger")
            return redirect(url_for('register'))

        # ✅ Validate password match
        if password != confirm_password:
            flash("⚠️ Passwords do not match!", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # ✅ Check if the USN already exists in `users`
            cursor.execute("SELECT id FROM users WHERE student_id = %s", (usn,))
            if cursor.fetchone():
                flash("⚠️ USN already exists! Try a different one.", "danger")
                return redirect(url_for('register'))

            # ✅ Insert student into `users` table (For login access)
            cursor.execute("""
                INSERT INTO users (student_id, name, password, role) 
                VALUES (%s, %s, %s, 'student')
            """, (usn, name, hashed_password))

            # ✅ Insert student into `students` table (For profile completion)
            cursor.execute("""
                INSERT INTO students (student_id, name, application_status, barcode) 
                VALUES (%s, %s, 'pending', %s)
            """, (usn, name, f"{usn}.png")) 

            conn.commit()
            flash("✅ Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))

        except mysql.connector.Error as e:
            flash(f"⚠️ Database Error: {str(e)}", "danger")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form.get('student_id')  # Ensure form sends student_id
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE student_id = %s", (student_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session['student_id'] = user['student_id']  # ✅ Set student_id in session

            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("❌ Invalid USN or password!", "danger")

    return render_template("login.html")



#---------- Admin Login ----------
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

    conn.close()

    # Debugging Output
    print(f"DEBUG - Pending: {pending}, Processing: {processing}, Done: {done}, receive: {receive}")

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        pending=pending,
        processing=processing,
        done=done,
        receive=receive
    )


@app.route('/admin/applications')
def admin_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")  # Ensure all students are fetched
    applications = cursor.fetchall()

    conn.close()
    return render_template("admin_applications.html", applications=applications)



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



@app.route('/download/<filename>')
@login_required("admin")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)



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
        code128 = barcode.get_barcode_class('code128')
        generated_barcode = code128(student_id, writer=ImageWriter())
        generated_barcode.save(barcode_path.replace(".png", ""), {"format": "PNG"})  # ✅ Save PNG format

    # ✅ Set barcode path for frontend
    if barcode_filename:
        student["barcode"] = f"/{barcode_path}"  # ✅ Correct barcode path
    else:
        student["barcode"] = "/static/default_barcode.jpg"  # Default barcode if missing

    cursor.close()
    conn.close()
    
    return jsonify(student)





@app.route('/get_all_students', methods=['GET'])
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")  # Make sure this returns ALL students
    students = cursor.fetchall()

    conn.close()
    return jsonify(students)


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

        # Fetch student details
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
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

            # Only insert if no existing receive record or if we want to force a new one
            if not existing_history:
                cursor.execute("""
                    INSERT INTO student_history (
                        student_id, name, course, contact, guardian_name, 
                        address, profile_picture, signature, barcode, received_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    student["student_id"], student["name"], student["course"], 
                    student["contact"], student["guardian_name"], student["address"],
                    student["profile_picture"], student["signature"], student["barcode"]
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

        conn.commit()
        return jsonify({'success': True, 'barcode': student.get('barcode')})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()




@app.route('/student_id_history')
@login_required("admin")
def student_id_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student_history") 
    received_students = cursor.fetchall()

    conn.close()
    return render_template("student_id_history.html", student_history=received_students)




@app.route('/get_student_history/<student_id>')
@login_required("admin")
def get_student_history(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student_history WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    conn.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student)

# ---------- Admin User Management ----------
@app.route('/admin/manage_users')
@login_required("admin")
def admin_manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all users
    cursor.execute("""
        SELECT u.id, u.student_id, u.name, u.role, 
               CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END as has_profile,
               s.application_status
        FROM users u
        LEFT JOIN students s ON u.student_id = s.student_id
        ORDER BY u.role DESC, u.name ASC
    """)
    users = cursor.fetchall()
    
    # Get admin profile if exists
    admin_id = session.get('user_id')
    cursor.execute("SELECT * FROM admin_profiles WHERE user_id = %s", (admin_id,))
    admin_profile = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template("admin_manage_users.html", users=users, admin_profile=admin_profile)

@app.route('/admin/create_user', methods=['POST'])
@login_required("admin")
def admin_create_user():
    if request.method == 'POST':
        student_id = request.form.get('student_id').strip()
        name = request.form.get('name').strip()
        password = request.form.get('password').strip()
        role = request.form.get('role')
        
        # Validate required fields
        if not all([student_id, name, password, role]):
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
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (student_id, name, password, role) 
                VALUES (%s, %s, %s, %s)
            """, (student_id, name, hashed_password, role))
            
            # If student role, create student record
            if role == 'student':
                cursor.execute("""
                    INSERT INTO students (student_id, name, application_status) 
                    VALUES (%s, %s, 'pending')
                """, (student_id, name))
            
            conn.commit()
            flash("✅ User created successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"⚠️ Error creating user: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_manage_users'))

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

# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ---------- Student Dashboard ----------
@app.route('/student_dashboard')
@login_required("student")
def student_dashboard():
    if 'student_id' not in session:
        flash("⚠️ Session expired or invalid. Please log in again.", "danger")
        return redirect(url_for("login"))

    student_id = session.get('student_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
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
        "course": student["course"],
        "contact": student["contact"],
        "guardian_name": student["guardian_name"],
        "address": student["address"],
        "profile_picture": student["profile_picture"],
        "signature": student["signature"]
    })

    return render_template("student_dashboard.html", student=student)







# ---------- Apply for Student ID ----------
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
        code128 = barcode.get_barcode_class('code128')
        generated_barcode = code128(student_id, writer=ImageWriter())
        generated_barcode.save(barcode_path.replace(".png", ""), {"format": "PNG"})  # ✅ Save PNG format

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







# ---------- Update Student Info ----------
@app.route('/update_student_info', methods=['POST'])
def update_student_info():
    user_id = session.get('user_id')
    student_id = session.get('student_id')

    if not student_id:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for("login"))

    name = request.form.get("name")
    course = request.form.get("course")
    contact = request.form.get("contact")
    guardian_name = request.form.get("guardian_name")
    address = request.form.get("address")

    profile_picture = request.files.get("profile_picture")
    signature_data = request.form.get("signature")  # This will be base64 data from canvas

    if not profile_picture:
        flash("Profile picture is required.", "danger")
        return redirect(url_for("complete_student_profile"))

    # Process profile picture
    profile_picture_filename = secure_filename(profile_picture.filename)
    profile_path = os.path.join(app.config["UPLOAD_FOLDER"], profile_picture_filename)
    profile_picture.save(profile_path)

    # Process signature from canvas
    signature_filename = None
    if signature_data:
        signature_filename = process_esignature(signature_data, student_id)
    
    if not signature_filename:
        flash("Signature is required. Please draw your signature.", "danger")
        return redirect(url_for("complete_student_profile"))

    # Validate profile picture using trainable validator if available
    if photo_validator and photo_validator.model:
        result = photo_validator.validate(image_path=profile_path)
        if not result["valid"]:
            flash(f"Profile picture validation failed: {result.get('error', 'Unknown error')}", "danger")
            return redirect(url_for("complete_student_profile"))
    else:
        # Fall back to original validation
        with ThreadPoolExecutor() as executor:
            blur_result = executor.submit(is_blurry, cv2.imread(profile_path))
            face_result = executor.submit(is_face_detected, profile_path)
            bg_result = executor.submit(is_plain_background, profile_path)

            if blur_result.result():
                flash("Profile picture is blurry. Please upload a clear image.", "danger")
                return redirect(url_for("complete_student_profile"))

            if not face_result.result():
                flash("Profile picture must contain a visible face.", "danger")
                return redirect(url_for("complete_student_profile"))

            if not bg_result.result():
                flash("Profile picture must have a plain background.", "danger")
                return redirect(url_for("complete_student_profile"))

    # Save to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students 
        SET name=%s, course=%s, contact=%s, guardian_name=%s, address=%s, 
            profile_picture=%s, signature=%s, application_status='pending'
        WHERE student_id=%s
    """, (name, course, contact, guardian_name, address, profile_picture_filename, signature_filename, student_id))
    
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Profile updated successfully!", "success")
    return redirect(url_for("student_dashboard"))


# ---------- Complete Info ----------
@app.route('/complete_student_profile', methods=['GET'])
@login_required("student")
def complete_student_profile():
    user_id = session.get('user_id')
    name = session.get('name')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (session['student_id'],))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("complete_student_profile.html", student=student, name=student['name'])

# ---------- Student Application Status ----------
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

# ---------- Contact Support ----------
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

# ---------- Admin Support Messages ----------
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
        SELECT h.*, u.name as responder_name, u.role as responder_role
        FROM support_message_history h
        JOIN users u ON h.response_by = u.student_id
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

@app.route('/admin/respond_message/<int:message_id>', methods=['POST'])
@login_required("admin")
def admin_respond_message(message_id):
    if request.method == 'POST':
        response = request.form.get('response')
        status = request.form.get('status')
        
        if not response:
            flash("Response cannot be empty", "danger")
            return redirect(url_for('admin_view_message', message_id=message_id))
        
        # Get admin ID - use student_id if available, otherwise use a default format
        admin_id = session.get('student_id')
        if not admin_id:
            # Fallback to user_id if student_id is not available
            admin_id = f"ADMIN_{session.get('user_id')}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Add response to history
            cursor.execute("""
                INSERT INTO support_message_history (message_id, response_by, response, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (message_id, admin_id, response))
            
            # Update message status and admin response
            cursor.execute("""
                UPDATE support_messages 
                SET status = %s, admin_response = %s, updated_at = NOW()
                WHERE id = %s
            """, (status, response, message_id))
            
            conn.commit()
            flash("Response sent successfully", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"Error sending response: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_view_message', message_id=message_id))

# ---------- Student Support Messages ----------
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
        SELECT h.*, u.name as responder_name, u.role as responder_role
        FROM support_message_history h
        JOIN users u ON h.response_by = u.student_id
        WHERE h.message_id = %s
        ORDER BY h.created_at ASC
    """, (message_id,))
    history = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("student_view_message.html", message=message, history=history)

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
        cursor = conn.cursor()
        
        try:
            # Verify message belongs to student
            cursor.execute("SELECT id FROM support_messages WHERE id = %s AND student_id = %s", 
                          (message_id, student_id))
            if not cursor.fetchone():
                flash("Message not found", "danger")
                return redirect(url_for('student_support_messages'))
            
            # Add response to history
            cursor.execute("""
                INSERT INTO support_message_history (message_id, response_by, response, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (message_id, student_id, response))
            
            # Update message status to pending if it was resolved
            cursor.execute("""
                UPDATE support_messages 
                SET status = CASE WHEN status = 'resolved' THEN 'pending' ELSE status END,
                    updated_at = NOW()
                WHERE id = %s
            """, (message_id,))
            
            conn.commit()
            flash("Reply sent successfully", "success")
            
        except Exception as e:
            conn.rollback()
            flash(f"Error sending reply: {str(e)}", "danger")
            
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('student_view_message', message_id=message_id))

# Add a route to check for new messages (for real-time updates)
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
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

