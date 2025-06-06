# Add these helper functions to your app.py

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
        name_data: Dictionary with name information
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

# Test the helper functions
def test_helper_functions():
    """Test the helper functions"""
    print("🧪 Testing Helper Functions")
    print("-" * 40)
    
    # Test get_full_name
    test_records = [
        {'first_name': 'Zarwin', 'middle_name': 'K.', 'last_name': 'Villaro'},
        {'first_name': 'Mark', 'middle_name': None, 'last_name': 'Joseph'},
        {'name': 'Ruperto Bernales'},  # Old format
        {'first_name': 'Ana', 'last_name': 'Cruz'},  # No middle name
    ]
    
    for record in test_records:
        full_name = get_full_name(record)
        print(f"Record: {record} → Full Name: '{full_name}'")
    
    print("\n" + "-" * 40)
    
    # Test parse_name_input
    test_inputs = [
        "Zarwin K. Villaro",
        "Mark Joseph",
        "Ana",
        "Juan dela Cruz Santos"
    ]
    
    for name_input in test_inputs:
        parsed = parse_name_input(name_input)
        print(f"Input: '{name_input}' → {parsed}")

# Run tests
test_helper_functions()
