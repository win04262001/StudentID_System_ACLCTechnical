import mysql.connector
import re
from typing import Tuple, Optional

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "studentid"
}

def parse_full_name(full_name: str) -> Tuple[str, Optional[str], str]:
    """
    Parse a full name into first, middle, and last name components.
    
    Args:
        full_name: The full name string to parse
        
    Returns:
        Tuple of (first_name, middle_name, last_name)
    """
    if not full_name or not full_name.strip():
        return "", None, ""
    
    # Clean the name: remove extra spaces, handle special characters
    name = re.sub(r'\s+', ' ', full_name.strip())
    
    # Split by spaces
    parts = name.split()
    
    if len(parts) == 1:
        # Only one name - treat as first name
        return parts[0], None, ""
    elif len(parts) == 2:
        # Two names - first and last
        return parts[0], None, parts[1]
    elif len(parts) == 3:
        # Three names - first, middle, last
        return parts[0], parts[1], parts[2]
    else:
        # More than 3 names - first, combine middle parts, last
        first_name = parts[0]
        last_name = parts[-1]
        middle_name = " ".join(parts[1:-1])
        return first_name, middle_name, last_name

def migrate_student_names():
    """Migrate names in the students table"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all students with names
        cursor.execute("SELECT id, student_id, name FROM students WHERE name IS NOT NULL AND name != ''")
        students = cursor.fetchall()
        
        print(f"Found {len(students)} students to migrate")
        
        successful_migrations = 0
        failed_migrations = 0
        
        for student in students:
            try:
                full_name = student['name']
                first_name, middle_name, last_name = parse_full_name(full_name)
                
                # Update the student record
                cursor.execute("""
                    UPDATE students 
                    SET first_name = %s, middle_name = %s, last_name = %s 
                    WHERE id = %s
                """, (first_name, middle_name, last_name, student['id']))
                
                print(f"✅ {student['student_id']}: '{full_name}' → First: '{first_name}', Middle: '{middle_name or 'N/A'}', Last: '{last_name}'")
                successful_migrations += 1
                
            except Exception as e:
                print(f"❌ Error migrating {student['student_id']}: {e}")
                failed_migrations += 1
        
        conn.commit()
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successful: {successful_migrations}")
        print(f"   ❌ Failed: {failed_migrations}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def migrate_student_history_names():
    """Migrate names in the student_history table"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all student history records with names
        cursor.execute("SELECT id, student_id, name FROM student_history WHERE name IS NOT NULL AND name != ''")
        history_records = cursor.fetchall()
        
        print(f"Found {len(history_records)} student history records to migrate")
        
        for record in history_records:
            try:
                full_name = record['name']
                first_name, middle_name, last_name = parse_full_name(full_name)
                
                # Update the history record
                cursor.execute("""
                    UPDATE student_history 
                    SET first_name = %s, middle_name = %s, last_name = %s 
                    WHERE id = %s
                """, (first_name, middle_name, last_name, record['id']))
                
                print(f"✅ History {record['student_id']}: '{full_name}' → First: '{first_name}', Middle: '{middle_name or 'N/A'}', Last: '{last_name}'")
                
            except Exception as e:
                print(f"❌ Error migrating history {record['student_id']}: {e}")
        
        conn.commit()
        print("✅ Student history migration completed")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def migrate_user_names():
    """Migrate names in the users table"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all users with names
        cursor.execute("SELECT id, student_id, name FROM users WHERE name IS NOT NULL AND name != '' AND role = 'student'")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} user records to migrate")
        
        for user in users:
            try:
                full_name = user['name']
                first_name, middle_name, last_name = parse_full_name(full_name)
                
                # Update the user record
                cursor.execute("""
                    UPDATE users 
                    SET first_name = %s, middle_name = %s, last_name = %s 
                    WHERE id = %s
                """, (first_name, middle_name, last_name, user['id']))
                
                print(f"✅ User {user['student_id']}: '{full_name}' → First: '{first_name}', Middle: '{middle_name or 'N/A'}', Last: '{last_name}'")
                
            except Exception as e:
                print(f"❌ Error migrating user {user['student_id']}: {e}")
        
        conn.commit()
        print("✅ User migration completed")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def test_name_parsing():
    """Test the name parsing function with various name formats"""
    test_names = [
        "Zarwin K. Villaro",
        "Devine Grace G. Pacaña",
        "Ruperto Bernales",
        "Mark Joseph",
        "Alejandro Bataluna",
        "marjore marj",
        "Gino Abatayo",
        "Juan dela Cruz Santos",
        "Maria Cristina Santos-Reyes",
        "Jose Rizal",
        "Ana Marie Santos Cruz"
    ]
    
    print("🧪 Testing name parsing:")
    print("-" * 60)
    
    for name in test_names:
        first, middle, last = parse_full_name(name)
        print(f"'{name}' → First: '{first}', Middle: '{middle or 'N/A'}', Last: '{last}'")

# Run the migration
if __name__ == "__main__":
    print("🚀 Starting Name Migration Process")
    print("=" * 50)
    
    # Test name parsing first
    test_name_parsing()
    
    print("\n" + "=" * 50)
    print("📋 Migrating Students Table...")
    migrate_student_names()
    
    print("\n" + "=" * 50)
    print("📋 Migrating Student History Table...")
    migrate_student_history_names()
    
    print("\n" + "=" * 50)
    print("📋 Migrating Users Table...")
    migrate_user_names()
    
    print("\n🎉 Migration completed!")
