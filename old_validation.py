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










# Purpose: Update student information
# This route processes form submissions to update student details
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