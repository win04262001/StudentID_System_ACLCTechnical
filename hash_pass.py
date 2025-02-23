from werkzeug.security import generate_password_hash
import mysql.connector

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="studentid"
)
cursor = conn.cursor()

# Generate hashed password
hashed_password = generate_password_hash("admin123")

# Update admin password
try:
    cursor.execute("""
        UPDATE users SET password = %s WHERE student_id = 'admin001'
    """, (hashed_password,))

    conn.commit()
    print("✅ Admin password updated successfully!")

except mysql.connector.Error as e:
    print(f"⚠️ Error updating admin password: {str(e)}")

cursor.close()
conn.close()
