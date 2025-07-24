#!/usr/bin/env python3
"""
Fix PostgreSQL sequence issue for users table
This script resets the sequence to the correct value after manual data insertion
"""

import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import get_db, engine
from database.models import User
from sqlalchemy import text

def fix_users_sequence():
    """Fix the users table sequence"""
    try:
        db = get_db()
        
        # Get the maximum user ID
        max_id = db.query(User.id).order_by(User.id.desc()).first()
        if max_id:
            max_id = max_id[0]
        else:
            max_id = 0
        
        print(f"Current maximum user ID: {max_id}")
        
        # Reset the sequence to the correct value
        # PostgreSQL sequence should be set to max_id + 1
        reset_query = text(f"SELECT setval('users_id_seq', {max_id}, true)")
        result = db.execute(reset_query)
        
        # Verify the sequence value
        verify_query = text("SELECT currval('users_id_seq')")
        result = db.execute(verify_query)
        current_seq_value = result.scalar()
        
        print(f"Sequence reset to: {current_seq_value}")
        print("Database sequence fixed successfully!")
        
        # Test creating a new user
        test_user = User(
            email="test_sequence@example.com",
            password_hash="test_hash",
            name="Test Sequence User",
            role="customer"
        )
        
        db.add(test_user)
        db.commit()
        
        print(f"Test user created with ID: {test_user.id}")
        
        # Clean up test user
        db.delete(test_user)
        db.commit()
        print("Test user cleaned up")
        
    except Exception as e:
        print(f"Error fixing sequence: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Fixing PostgreSQL sequence for users table...")
    fix_users_sequence()
    print("Done!") 