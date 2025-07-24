# backend/api/routes/insights.py (new file)
from flask import Blueprint, request, jsonify
from database.models import Review, Product
from database.connection import get_db
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from utils.auth_decorator import simple_auth_required
import numpy as np

bp = Blueprint('insights', __name__)

@bp.route('/generate', methods=['GET'])
@simple_auth_required
def generate_insights():
    """Generate AI-powered insights based on data analysis"""
    try:
        db = get_db()
        
        # Get parameters
        scope = request.args.get('scope', 'all')  # all, product, brand, category
        scope_value = request.args.get('value', '')
        days = int(request.args.get('days', 30))
        
        insights = []
        
        # Generate different types of insights based on scope
        if scope == 'category' and scope_value:
            insights.extend(generate_category_insights(db, scope_value, days))
        elif scope == 'brand' and scope_value:
            insights.extend(generate_brand_insights(db, scope_value, days))
        elif scope == 'product' and scope_value:
            insights.extend(generate_product_insights(db, scope_value, days))
        else:
            # Generate overall insights
            insights.extend(generate_overall_insights(db, days))
        
        # Sort by priority
        insights.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return jsonify({
            'insights': insights[:6],  # Return top 6 insights
            'generated_at': datetime.now().isoformat(),
            'scope': scope,
            'scope_value': scope_value
        })
        
    except Exception as e:
        print(f"Insights generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_category_insights(db, category, days):
    """Generate insights for a specific category"""
    insights = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Get category performance data
    current_reviews = db.query(Review).join(Product).filter(
        Product.category == category,
        Review.review_date >= start_date
    ).all()
    
    if current_reviews:
        # Sentiment trend
        positive_count = sum(1 for r in current_reviews if r.sentiment == 'positive')
        positive_ratio = positive_count / len(current_reviews)
        
        # Compare with previous period
        prev_start = start_date - timedelta(days=days)
        prev_reviews = db.query(Review).join(Product).filter(
            Product.category == category,
            Review.review_date >= prev_start,
            Review.review_date < start_date
        ).all()
        
        if prev_reviews:
            prev_positive = sum(1 for r in prev_reviews if r.sentiment == 'positive')
            prev_ratio = prev_positive / len(prev_reviews)
            
            change = ((positive_ratio - prev_ratio) / prev_ratio) * 100 if prev_ratio > 0 else 0
            
            if change > 10:
                insights.append({
                    'type': 'opportunity',
                    'title': 'Growth Opportunity',
                    'description': f'{category} category shows {change:.0f}% increase in positive sentiment. Consider expanding product line.',
                    'priority': 8,
                    'action': 'explore_category',
                    'action_url': f'/analytics/category/{category}',
                    'metrics': {
                        'change': change,
                        'current_positive': positive_ratio * 100,
                        'reviews_analyzed': len(current_reviews)
                    }
                })
        
        # Quality alerts
        declining_products = []
        products = db.query(Product).filter_by(category=category).all()
        
        for product in products:
            product_reviews = [r for r in current_reviews if r.product_id == product.id]
            if len(product_reviews) >= 5:
                avg_rating = np.mean([r.rating for r in product_reviews])
                if avg_rating < 3.5:
                    declining_products.append({
                        'id': product.id,
                        'name': product.name,
                        'rating': avg_rating
                    })
        
        if declining_products:
            insights.append({
                'type': 'warning',
                'title': 'Quality Alert',
                'description': f'{len(declining_products)} products in {category} showing low ratings. Immediate review recommended.',
                'priority': 9,
                'action': 'view_products',
                'action_url': f'/analytics/category/{category}',
                'products': declining_products[:3]
            })
    
    return insights

def generate_brand_insights(db, brand, days):
    """Generate insights for a specific brand"""
    insights = []
    # Similar implementation for brand-specific insights
    return insights

def generate_product_insights(db, product_id, days):
    """Generate insights for a specific product"""
    insights = []
    # Similar implementation for product-specific insights
    return insights

def generate_overall_insights(db, days):
    """Generate overall platform insights"""
    insights = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Trending topics analysis
    recent_reviews = db.query(Review).filter(
        Review.review_date >= start_date
    ).all()
    
    if recent_reviews:
        # Analyze keywords
        keyword_counts = {}
        for review in recent_reviews:
            if review.keywords:
                for kw in review.keywords:
                    keyword = kw.get('keyword', '') if isinstance(kw, dict) else str(kw)
                    if keyword:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Find trending keywords
        trending_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if trending_keywords:
            top_keyword, count = trending_keywords[0]
            insights.append({
                'type': 'trend',
                'title': 'Trending Topics',
                'description': f'"{top_keyword}" mentioned {count} times this month. Consider highlighting in marketing campaigns.',
                'priority': 6,
                'action': 'view_trends',
                'action_url': '/analytics/trends',
                'keywords': [{'word': k, 'count': c} for k, c in trending_keywords]
            })
    
    # Competitor mentions trend
    competitor_mentions = []
    for review in recent_reviews:
        if review.competitor_mentions:
            competitor_mentions.extend(review.competitor_mentions)
    
    if len(competitor_mentions) > 10:
        insights.append({
            'type': 'info',
            'title': 'Competitor Activity',
            'description': f'{len(competitor_mentions)} competitor mentions detected. Monitor competitive positioning.',
            'priority': 5,
            'action': 'view_competitors',
            'action_url': '/analytics/competitors/overview'
        })
    
    return insights