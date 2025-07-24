# backend/api/routes/admin.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import pandas as pd
from datetime import datetime, timedelta
from database.models import User, Review, ProcessingLog
from utils.auth_decorator import simple_auth_required, get_current_user_id
from database.connection import get_db
import traceback

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @simple_auth_required
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_current_user_id()
            db = get_db()
            user = db.query(User).filter_by(id=user_id).first()
            
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Admin auth error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    return decorated_function

@bp.route('/processing-queue', methods=['GET'])
@admin_required
def get_processing_queue():
    """Get real-time processing queue status"""
    try:
        # Get recent processing logs
        db = get_db()
        recent_logs = db.query(ProcessingLog).order_by(
            ProcessingLog.created_at.desc()
        ).limit(50).all()
        
        # Calculate statistics
        total_processed = db.query(ProcessingLog).count()
        successful = db.query(ProcessingLog).filter(
            ProcessingLog.error.is_(None)
        ).count()
        
        # Format response
        return jsonify({
            'queue_status': 'active',
            'pipeline_stats': {
                'total_processed': total_processed,
                'successful': successful,
                'failed': total_processed - successful
            },
            'recent_processing': [
                {
                    'review_id': log.review_id,
                    'processing_time': log.processing_time,
                    'status': 'success' if not log.error else 'failed',
                    'created_at': log.created_at.isoformat() if log.created_at else None
                }
                for log in recent_logs
            ]
        })
        
    except Exception as e:
        print(f"Processing queue error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'queue_status': 'error',
            'pipeline_stats': {
                'total_processed': 0,
                'successful': 0,
                'failed': 0
            },
            'recent_processing': [],
            'error': str(e)
        }), 200

@bp.route('/retrain-models', methods=['POST'])
@admin_required
def retrain_models():
    """Trigger model retraining with new data"""
    try:
        # Get all reviews for retraining
        db = get_db()
        reviews = db.query(Review).all()
        
        if len(reviews) < 100:
            return jsonify({
                'error': 'Insufficient data for retraining. Need at least 100 reviews.'
            }), 400
        
        # Convert to DataFrame
        reviews_df = pd.DataFrame([r.to_dict() for r in reviews])
        
        # Trigger retraining (simplified for demo)
        training_stats = {
            'total_samples': len(reviews_df),
            'sentiment_distribution': reviews_df['sentiment'].value_counts().to_dict() if 'sentiment' in reviews_df else {},
            'start_time': datetime.now().isoformat(),
            'status': 'initiated'
        }
        
        return jsonify({
            'success': True,
            'message': 'Model retraining initiated',
            'training_stats': training_stats
        })
        
    except Exception as e:
        print(f"Retrain models error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/system-health', methods=['GET'])
@admin_required
def get_system_health():
    """Get overall system health metrics"""
    try:
        db = get_db()
        
        # Get various metrics
        total_reviews = db.query(Review).count()
        total_users = db.query(User).count()
        recent_reviews = db.query(Review).filter(
            Review.review_date >= datetime.now() - timedelta(days=1)
        ).count()
        
        # Get processing performance
        recent_logs = db.query(ProcessingLog).order_by(
            ProcessingLog.created_at.desc()
        ).limit(100).all()
        
        avg_processing_time = sum(log.processing_time for log in recent_logs) / len(recent_logs) if recent_logs else 0
        
        # Check for recent errors
        recent_errors = db.query(ProcessingLog).filter(
            ProcessingLog.error.isnot(None),
            ProcessingLog.created_at >= datetime.now() - timedelta(hours=1)
        ).count()
        
        status = 'healthy' if recent_errors < 5 else 'degraded'
        
        health_metrics = {
            'status': status,
            'metrics': {
                'total_reviews': total_reviews,
                'total_users': total_users,
                'reviews_last_24h': recent_reviews,
                'avg_processing_time': round(avg_processing_time, 2),
                'error_rate': round(recent_errors / max(len(recent_logs), 1), 2),
                'recent_errors': recent_errors
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(health_metrics)
        
    except Exception as e:
        print(f"System health error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'metrics': {
                'total_reviews': 0,
                'total_users': 0,
                'reviews_last_24h': 0,
                'avg_processing_time': 0,
                'error_rate': 0,
                'recent_errors': 0
            },
            'error': str(e)
        }), 200

@bp.route('/export-data', methods=['POST'])
@admin_required
def export_data():
    """Export analytics data for reporting"""
    try:
        data = request.get_json() or {}
        data_type = data.get('type', 'all')
        format_type = data.get('format', 'csv')
        date_range = data.get('date_range', {})
        
        db = get_db()
        
        # Build query based on parameters
        query = db.query(Review)
        
        if date_range.get('start'):
            start_date = datetime.fromisoformat(date_range['start'])
            query = query.filter(Review.review_date >= start_date)
        if date_range.get('end'):
            end_date = datetime.fromisoformat(date_range['end'])
            query = query.filter(Review.review_date <= end_date)
        
        reviews = query.all()
        
        # Convert to list of dicts
        export_data = []
        for review in reviews:
            review_dict = {
                'id': review.id,
                'product_id': review.product_id,
                'product_name': review.product_name,
                'category': review.category,
                'brand': review.brand,
                'rating': review.rating,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'review_date': review.review_date.isoformat() if review.review_date else None
            }
            export_data.append(review_dict)
        
        # Generate summary if requested
        if data_type == 'summary' and export_data:
            reviews_df = pd.DataFrame(export_data)
            summary_data = {
                'total_reviews': len(reviews_df),
                'sentiment_distribution': reviews_df['sentiment'].value_counts().to_dict() if 'sentiment' in reviews_df else {},
                'category_breakdown': reviews_df['category'].value_counts().to_dict() if 'category' in reviews_df else {},
                'average_ratings': reviews_df.groupby('category')['rating'].mean().to_dict() if 'category' in reviews_df and 'rating' in reviews_df else {}
            }
            export_data = summary_data
        
        return jsonify({
            'success': True,
            'data': export_data,
            'export_date': datetime.now().isoformat(),
            'record_count': len(reviews) if data_type != 'summary' else 1
        })
        
    except Exception as e:
        print(f"Export data error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500