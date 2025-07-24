# backend/api/utils/auth_decorator.py
from functools import wraps
from flask import request, jsonify
from database.models import User
from database.connection import get_db

def simple_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Parse simple token
        if not token.startswith('user_'):
            return jsonify({'error': 'Invalid token'}), 401
        
        try:
            parts = token.split('_')
            user_id = int(parts[1])
            
            # Store user_id in request context
            request.current_user_id = user_id
            request.current_user_role = parts[2] if len(parts) > 2 else 'user'
            
            return f(*args, **kwargs)
            
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

def get_current_user_id():
    """Get current user ID from request context"""
    return getattr(request, 'current_user_id', None)

def get_current_user_role():
    """Get current user role from request context"""
    return getattr(request, 'current_user_role', 'user')