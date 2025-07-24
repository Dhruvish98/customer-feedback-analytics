# backend/scripts/create_admin.py

from database.connection import get_db
from database.models import User
from werkzeug.security import generate_password_hash
import sys

def create_admin_user(email, password, name="Admin User"):
    """Create an admin user"""
    db = get_db()
    
    # Check if user exists
    existing_user = db.query(User).filter_by(email=email).first()
    if existing_user:
        print(f"User with email {email} already exists!")
        return
    
    # Create admin user
    admin_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
        role='admin'
    )
    
    db.add(admin_user)
    db.commit()
    
    print(f"Admin user created successfully!")
    print(f"Email: {email}")
    print(f"Password: {password}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [name]")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"
    
    create_admin_user(email, password, name)