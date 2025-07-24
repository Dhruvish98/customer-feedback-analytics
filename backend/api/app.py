# backend/api/app.py - Updated CORS configuration
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import timedelta
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import blueprints
from routes.auth import bp as auth_bp
from routes.reviews import bp as reviews_bp
from routes.analytics import bp as analytics_bp
from routes.admin import bp as admin_bp
from routes.advanced_analytics import bp as advanced_analytics_bp
from routes.users import bp as users_bp
from routes.products import bp as products_bp
from routes.insights import bp as insights_bp

# Import database and websocket
from database.connection import init_db
from websocket.live_updates import register_socketio_handlers

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Configure CORS with specific settings
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:3000", "http://localhost:3001"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }},
         supports_credentials=True)
    
    # Handle preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add('Access-Control-Allow-Credentials', "true")
            return response
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    register_socketio_handlers(socketio)
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(advanced_analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return {'message': 'E-commerce Review Analytics API', 'version': '2.0'}, 200
    
    return app, socketio

if __name__ == '__main__':
    from flask import request, make_response  # Add these imports
    app, socketio = create_app()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)