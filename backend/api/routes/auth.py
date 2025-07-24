# backend/api/routes/auth.py - Simplified version without JWT
from flask import Blueprint, request, jsonify, session
from database.models import User
from database.connection import get_db
import bcrypt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        db = get_db()
        user = db.query(User).filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create a simple token (just user ID encoded)
        simple_token = f"user_{user.id}_{user.role}"
        
        return jsonify({
            'access_token': simple_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        db = get_db()
        
        # Check if user exists
        if db.query(User).filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        new_user = User(
            name=data['name'],
            email=data['email'],
            password_hash=password_hash,
            role='user'
        )
        
        db.add(new_user)
        db.commit()
        
        # Create simple token
        simple_token = f"user_{new_user.id}_{new_user.role}"
        
        return jsonify({
            'access_token': simple_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        db.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Parse simple token
        if not token.startswith('user_'):
            return jsonify({'error': 'Invalid token'}), 401
        
        parts = token.split('_')
        if len(parts) < 3:
            return jsonify({'error': 'Invalid token format'}), 401
        
        user_id = int(parts[1])
        
        db = get_db()
        user = db.query(User).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500