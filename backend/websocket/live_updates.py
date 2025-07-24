# backend/websocket/live_updates.py - Add the missing import
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta  # Add timedelta import here
import random
import time
import threading
import json
from requests import request

def register_socketio_handlers(socketio):
    """Register Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        emit('connection_response', {'status': 'Connected to live updates'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_updates')
    def handle_join_updates(data):
        room = data.get('room', 'general')
        join_room(room)
        emit('joined', {'room': room}, room=room)
    
    # Start background thread for broadcasting updates
    def broadcast_updates():
        """Broadcast fake updates for demo purposes"""
        while True:
            try:
                # Generate fake review update
                update = {
                    'type': 'new_review',
                    'data': {
                        'product_id': f'PROD{random.randint(1, 100):05d}',
                        'rating': random.randint(1, 5),
                        'sentiment': random.choice(['positive', 'negative', 'neutral']),
                        'timestamp': datetime.utcnow().isoformat(),
                        'time_ago': 'just now'
                    }
                }
                
                socketio.emit('live_update', update, room='general')
                
                # Generate processing update
                if random.random() > 0.7:
                    processing_update = {
                        'type': 'processing_status',
                        'data': {
                            'reviews_in_queue': random.randint(0, 50),
                            'avg_processing_time': random.uniform(0.5, 3.0),
                            'status': 'healthy'
                        }
                    }
                    socketio.emit('live_update', processing_update, room='general')
                
                time.sleep(random.uniform(2, 5))  # Random delay between updates
                
            except Exception as e:
                print(f"Error broadcasting updates: {e}")
                time.sleep(5)  # Wait before retrying
    
    # Start the background thread
    thread = threading.Thread(target=broadcast_updates)
    thread.daemon = True
    thread.start()