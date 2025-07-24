# backend/api/routes/users.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from database.models import User, Review, CustomerJourney
from database.connection import get_db
import pandas as pd
from utils.auth_decorator import simple_auth_required, get_current_user_id

bp = Blueprint('users', __name__)

@bp.route('/stats', methods=['GET'])
@simple_auth_required
def get_user_stats():
    """Get comprehensive user statistics"""
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        # Get user
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get review statistics
        total_reviews = db.query(Review).filter_by(user_id=user_id).count()
        
        # Reviews this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        reviews_this_month = db.query(Review).filter(
            Review.user_id == user_id,
            Review.created_at >= start_of_month
        ).count()
        
        # Average rating given
        avg_rating = db.query(func.avg(Review.rating)).filter_by(user_id=user_id).scalar() or 0
        
        # Total helpful votes
        total_helpful = db.query(func.sum(Review.helpful_count)).filter_by(user_id=user_id).scalar() or 0
        
        # Category distribution
        categories = db.query(
            Review.category,
            func.count(Review.id)
        ).filter_by(user_id=user_id).group_by(Review.category).all()
        
        category_distribution = {cat: count for cat, count in categories}
        
        # Sentiment trend (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        reviews = db.query(Review).filter(
            Review.user_id == user_id,
            Review.created_at >= six_months_ago
        ).order_by(Review.created_at).all()
        
        # Group by month
        sentiment_trend = calculate_sentiment_trend(reviews)
        
        # Reviewer level calculation
        level_info = calculate_reviewer_level(total_reviews, total_helpful, avg_rating)
        
        # Achievements
        achievements = calculate_achievements(user, total_reviews, total_helpful, categories)
        
        return jsonify({
            'total_reviews': total_reviews,
            'reviews_this_month': reviews_this_month,
            'avg_rating_given': float(avg_rating),
            'total_helpful_votes': total_helpful,
            'category_distribution': category_distribution,
            'sentiment_trend': sentiment_trend,
            'reviewer_level': level_info['level'],
            'level_progress': level_info['progress'],
            'achievements': achievements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/activity', methods=['GET'])
@simple_auth_required
def get_user_activity():
    """Get recent user activity"""
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        activities = []
        
        # Recent reviews
        recent_reviews = db.query(Review).filter_by(user_id=user_id).order_by(
            Review.created_at.desc()
        ).limit(5).all()
        
        for review in recent_reviews:
            activities.append({
                'type': 'review',
                'description': f"Reviewed {review.product_name}",
                'time_ago': time_ago(review.created_at),
                'link': f'/reviews/{review.id}'
            })
        
        # Recent helpful votes (simulated)
        activities.append({
            'type': 'helpful',
            'description': '5 people found your review helpful',
            'time_ago': '2 days ago'
        })
        
        # Sort by time
        activities.sort(key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
        
        return jsonify({'activities': activities[:10]})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/insights', methods=['GET'])
@simple_auth_required
def get_user_insights():
    """Get personalized insights for user"""
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        insights = []
        
        # Get user's reviews
        reviews = db.query(Review).filter_by(user_id=user_id).all()
        
        if reviews:
            # Most reviewed category
            category_counts = {}
            for review in reviews:
                category_counts[review.category] = category_counts.get(review.category, 0) + 1
            
            top_category = max(category_counts, key=category_counts.get)
            insights.append({
                'type': 'info',
                'icon': '📊',
                'title': 'Your Favorite Category',
                'description': f"You've reviewed {category_counts[top_category]} products in {top_category}"
            })
            
            # Sentiment analysis
            positive_count = sum(1 for r in reviews if r.sentiment == 'positive')
            positive_ratio = positive_count / len(reviews)
            
            if positive_ratio > 0.7:
                insights.append({
                    'type': 'positive',
                    'icon': '😊',
                    'title': 'Positive Reviewer',
                    'description': f"{int(positive_ratio * 100)}% of your reviews are positive!"
                })
            
            # Review quality
            avg_quality = sum(r.quality_score for r in reviews if r.quality_score) / len(reviews)
            if avg_quality > 0.8:
                insights.append({
                    'type': 'achievement',
                    'icon': '⭐',
                    'title': 'High Quality Reviews',
                    'description': 'Your reviews are detailed and helpful to others'
                })
        
        return jsonify({'insights': insights})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_sentiment_trend(reviews):
    """Calculate sentiment trend over time"""
    if not reviews:
        return {'labels': [], 'values': []}
    
    df = pd.DataFrame([{
        'date': r.created_at,
        'sentiment_score': r.sentiment_scores.get('positive', 0) - r.sentiment_scores.get('negative', 0)
    } for r in reviews])
    
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly = df.groupby('month')['sentiment_score'].mean()
    
    return {
        'labels': [str(month) for month in monthly.index],
        'values': monthly.tolist()
    }

def calculate_reviewer_level(total_reviews, helpful_votes, avg_rating):
    """Calculate reviewer level based on activity"""
    points = total_reviews * 10 + helpful_votes * 5 + avg_rating * 20
    
    levels = [
        (0, 'Novice'),
        (100, 'Contributor'),
        (500, 'Expert'),
        (1000, 'Master'),
        (5000, 'Elite')
    ]
    
    current_level = 'Novice'
    next_threshold = 100
    
    for threshold, level in levels:
        if points >= threshold:
            current_level = level
        else:
            next_threshold = threshold
            break
    
    progress = min(100, (points % next_threshold) / next_threshold * 100)
    
    return {
        'level': current_level,
        'progress': progress,
        'points': points
    }

def calculate_achievements(user, total_reviews, helpful_votes, categories):
    """Calculate user achievements"""
    achievements = [
        {
            'icon': '🎯',
            'name': 'First Review',
            'description': 'Write your first review',
            'unlocked': total_reviews >= 1
        },
        {
            'icon': '📚',
            'name': 'Prolific Reviewer',
            'description': 'Write 10 reviews',
            'unlocked': total_reviews >= 10
        },
        {
            'icon': '💯',
            'name': 'Century',
            'description': 'Write 100 reviews',
            'unlocked': total_reviews >= 100
        },
        {
            'icon': '👍',
            'name': 'Helpful Reviewer',
            'description': 'Get 50 helpful votes',
            'unlocked': helpful_votes >= 50
        },
        {
            'icon': '🌟',
            'name': 'Category Expert',
            'description': 'Review 5+ products in one category',
            'unlocked': any(count >= 5 for count in categories)
        }
    ]
    
    return achievements

def time_ago(timestamp):
    """Convert timestamp to human-readable time ago"""
    if not timestamp:
        return 'Unknown'
    
    delta = datetime.now() - timestamp
    
    if delta.days > 365:
        return f"{delta.days // 365} year{'s' if delta.days // 365 > 1 else ''} ago"
    elif delta.days > 30:
        return f"{delta.days // 30} month{'s' if delta.days // 30 > 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600} hour{'s' if delta.seconds // 3600 > 1 else ''} ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60} minute{'s' if delta.seconds // 60 > 1 else ''} ago"
    else:
        return "Just now"