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


# ✅ Define Flask App
app = Flask(__name__, static_folder="static")
app.secret_key = "123"
app.permanent_session_lifetime = timedelta(hours=2)

# ✅ Configure File Uploads
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

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

# ✅ Validate Image (Profile & Signature)
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
    data = request.json
    new_status = data.get("status")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch student details (barcode should already exist in students table)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    barcode_filename = student.get('barcode')  # ✅ Keep existing barcode

    if new_status == "receive":
        # ✅ Insert into student history while keeping the barcode
        cursor.execute("""
            INSERT INTO student_history (student_id, name, course, contact, guardian_name, address, profile_picture, signature, barcode, received_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (student["student_id"], student["name"], student["course"], student["contact"], student["guardian_name"],
              student["address"], student["profile_picture"], student["signature"], barcode_filename))

    # ✅ Update student status without changing barcode
    cursor.execute("UPDATE students SET application_status = %s WHERE student_id = %s", (new_status, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "barcode": barcode_filename})




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

    # Perform validation for profile picture
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

