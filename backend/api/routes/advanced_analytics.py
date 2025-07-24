# backend/api/routes/advanced_analytics.py - Fixed version
from flask import Blueprint, request, jsonify
from utils.auth_decorator import simple_auth_required, get_current_user_id  # Fixed import path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from database.models import *
from database.connection import get_db
from collections import defaultdict
import traceback

# Import NLP pipeline - with fallback
try:
    from nlp.advanced_pipeline import AdvancedNLPPipeline
    nlp_pipeline = AdvancedNLPPipeline()
except Exception as e:
    print(f"Warning: Could not load AdvancedNLPPipeline: {e}")
    nlp_pipeline = None

bp = Blueprint('advanced_analytics', __name__)

@bp.route('/aspects/<product_id>', methods=['GET'])
@simple_auth_required
def get_aspect_analysis(product_id):
    """Get detailed aspect-based sentiment analysis"""
    try:
        db = get_db()
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get reviews for product
        reviews = db.query(Review).filter(
            and_(
                Review.product_id == product_id,
                Review.review_date >= start_date
            )
        ).all()
        
        # Aggregate aspect data
        aspects = {}
        
        for review in reviews:
            if review.aspect_sentiments:
                for aspect, aspect_data in review.aspect_sentiments.items():
                    # Check if this aspect was actually mentioned
                    if isinstance(aspect_data, dict) and aspect_data.get('mentioned', False):
                        if aspect not in aspects:
                            aspects[aspect] = {
                                'mention_count': 0,
                                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                                'keywords': defaultdict(int),
                                'example_reviews': [],
                                'ratings': [],
                                'confidence_scores': []
                            }
                        
                        aspects[aspect]['mention_count'] += 1
                        
                        # Get sentiment - handle None case
                        sentiment = aspect_data.get('sentiment')
                        if sentiment is None:
                            sentiment = 'neutral'
                        else:
                            sentiment = str(sentiment).lower()
                        
                        # Ensure sentiment is valid
                        if sentiment not in ['positive', 'negative', 'neutral']:
                            sentiment = 'neutral'
                        
                        aspects[aspect]['sentiment_distribution'][sentiment] += 1
                        aspects[aspect]['ratings'].append(review.rating)
                        
                        # Add confidence score if available
                        confidence = aspect_data.get('confidence', 0)
                        if confidence:
                            aspects[aspect]['confidence_scores'].append(confidence)
                        
                        # Extract keywords from review
                        if review.keywords:
                            for keyword in review.keywords:
                                if isinstance(keyword, dict):
                                    keyword_text = keyword.get('keyword', keyword.get('word', ''))
                                    if keyword_text:
                                        aspects[aspect]['keywords'][keyword_text] += 1
                                elif isinstance(keyword, str):
                                    aspects[aspect]['keywords'][keyword] += 1
                        
                        # Add example review
                        if len(aspects[aspect]['example_reviews']) < 5:
                            review_text = review.review_text
                            if len(review_text) > 200:
                                review_text = review_text[:200] + '...'
                                
                            aspects[aspect]['example_reviews'].append({
                                'text': review_text,
                                'rating': review.rating,
                                'sentiment': sentiment,
                                'date': review.review_date.strftime('%Y-%m-%d') if review.review_date else 'N/A',
                                'confidence': confidence
                            })
        
        # Calculate metrics for each aspect
        aspect_analysis = {}
        
        for aspect, data in aspects.items():
            total_mentions = data['mention_count']
            sentiment_dist = data['sentiment_distribution']
            
            positive_ratio = sentiment_dist['positive'] / total_mentions if total_mentions > 0 else 0
            negative_ratio = sentiment_dist['negative'] / total_mentions if total_mentions > 0 else 0
            
            # Determine primary sentiment
            primary_sentiment = max(sentiment_dist, key=sentiment_dist.get)
            
            # Calculate average confidence
            avg_confidence = np.mean(data['confidence_scores']) if data['confidence_scores'] else 0
            
            # Calculate impact score
            avg_rating = np.mean(data['ratings']) if data['ratings'] else 0
            overall_avg = db.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar() or 0
            impact_score = abs(avg_rating - float(overall_avg)) * (total_mentions / len(reviews)) if reviews else 0
            
            # Get top keywords
            top_keywords = sorted(
                data['keywords'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Generate recommendations based on actual data
            recommendations = generate_aspect_recommendations(
                aspect, primary_sentiment, negative_ratio, top_keywords
            )
            
            aspect_analysis[aspect] = {
                'mention_count': total_mentions,
                'mention_frequency': total_mentions / len(reviews) if reviews else 0,
                'primary_sentiment': primary_sentiment,
                'sentiment_distribution': sentiment_dist,
                'positive_ratio': positive_ratio,
                'negative_ratio': negative_ratio,
                'impact_score': float(impact_score),
                'average_confidence': float(avg_confidence),
                'keywords': [{'word': k, 'frequency': v} for k, v in top_keywords],
                'example_reviews': data['example_reviews'],
                'recommendations': recommendations,
                'top_issues': extract_aspect_issues(aspect, data['example_reviews'])
            }
        
        # Get product name
        product = db.query(Product).filter_by(id=product_id).first()
        product_name = product.name if product else f"Product {product_id}"
        
        return jsonify({
            'product_id': product_id,
            'product_name': product_name,
            'analysis_period': days,
            'total_reviews': len(reviews),
            'aspects': aspect_analysis
        })
        
    except Exception as e:
        print(f"Aspect analysis error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# In backend/api/routes/advanced_analytics.py - Update the competitor intelligence endpoint

@bp.route('/competitor-intelligence', methods=['GET'])
@simple_auth_required
def get_competitor_intelligence():
    """Get comprehensive competitor analysis"""
    try:
        db = get_db()
        product_id = request.args.get('productId')
        category = request.args.get('category')
        
        # Get our product data
        our_product = db.query(Product).filter_by(id=product_id).first()
        if not our_product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Use product's category and subcategory if not provided
        if not category:
            category = our_product.category
        subcategory = our_product.subcategory
        
        # Get competitor products - simplified query without subcategory filtering
        # Just filter by category for now
        competitors = db.query(CompetitorProduct).filter_by(
            category=category
        ).order_by(CompetitorProduct.market_share.desc()).limit(5).all()
        
        # Get market position data
        our_position = db.query(MarketPosition).filter_by(
            product_id=product_id
        ).order_by(MarketPosition.date.desc()).first()
        
        # Get competitor mentions from reviews with subcategory context
        competitor_mentions = []
        reviews_with_mentions = db.query(Review).filter(
            Review.competitor_mentions.isnot(None),
            Review.product_id == product_id
        ).order_by(Review.review_date.desc()).limit(100).all()
        
        for review in reviews_with_mentions:
            if review.competitor_mentions:
                for mention in review.competitor_mentions:
                    competitor_mentions.append({
                        'competitor': mention.get('competitor', 'Unknown'),
                        'context': mention.get('context', ''),
                        'sentiment': mention.get('favorable_to_us', False),
                        'date': review.review_date.isoformat() if review.review_date else 'N/A',
                        'comparison_type': mention.get('comparison_type', 'direct_mention')
                    })
        
        # Calculate competitive advantages
        advantages = calculate_competitive_advantages(our_product, competitors, db)
        
        # Get feature comparison
        feature_comparison = compare_features(our_product, competitors)
        
        # Mention timeline
        mention_timeline = generate_mention_timeline(competitor_mentions)
        
        # Generate rating data
        our_rating_data = generate_our_rating_data(our_product, db)
        
        # Handle the case when no competitors are found
        if not competitors:
            return jsonify({
                'our_products': [{
                    'id': our_product.id,
                    'name': our_product.name,
                    'category': our_product.category,
                    'subcategory': our_product.subcategory,
                    'price_index': float(our_position.price_index) if our_position else 1.0,
                    'quality_index': float(our_position.quality_index) if our_position else 1.0,
                    'market_share': float(our_position.market_share) if our_position else 0.1
                }],
                'competitors': [],
                'competitive_advantages': advantages,
                'feature_comparison': [],
                'mention_contexts': competitor_mentions[:20],
                'mention_timeline': mention_timeline,
                'our_ratings': our_rating_data
            })
        
        return jsonify({
            'our_products': [{
                'id': our_product.id,
                'name': our_product.name,
                'category': our_product.category,
                'subcategory': our_product.subcategory,
                'price_index': float(our_position.price_index) if our_position else 1.0,
                'quality_index': float(our_position.quality_index) if our_position else 1.0,
                'market_share': float(our_position.market_share) if our_position else 0.1
            }],
            'competitors': [
                {
                    'id': c.id,
                    'name': c.name,
                    'brand': c.brand,
                    'price': float(c.price) if c.price else 0,
                    'price_index': float(c.price / our_product.price) if our_product.price and c.price else 1.0,
                    'quality_index': float(c.average_rating / 5.0) if c.average_rating else 0.5,
                    'market_share': float(c.market_share) if c.market_share else 0.1,
                    'average_rating': float(c.average_rating) if c.average_rating else 0,
                    'total_reviews': c.total_reviews or 0,
                    'key_features': c.key_features or [],
                    'strengths': c.strengths or [],
                    'weaknesses': c.weaknesses or [],
                    'ratings': generate_rating_data(c),
                    'mention_trend': get_mention_trend(c.brand, competitor_mentions)
                }
                for c in competitors
            ],
            'competitive_advantages': advantages,
            'feature_comparison': feature_comparison,
            'mention_contexts': competitor_mentions[:20],
            'mention_timeline': mention_timeline,
            'our_ratings': our_rating_data
        })
        
    except Exception as e:
        print(f"Competitor intelligence error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/predictions/<product_id>', methods=['GET'])
@simple_auth_required
def get_predictions(product_id):
    """Get predictive analytics for a product"""
    try:
        db = get_db()
        
        # Get historical data
        reviews = db.query(Review).filter_by(
            product_id=product_id
        ).order_by(Review.review_date).all()
        
        if len(reviews) < 30:
            return jsonify({'error': 'Insufficient data for predictions'}), 400
        
        # Prepare historical data
        historical_data = prepare_historical_data(reviews)
        
        # Generate predictions for different scenarios
        scenarios = {
            'baseline': generate_baseline_forecast(historical_data),
            'optimistic': generate_optimistic_forecast(historical_data),
            'pessimistic': generate_pessimistic_forecast(historical_data)
        }
        
        # Calculate churn risk
        churn_risk = calculate_churn_risk(reviews, db)
        
        # Calculate sales impact
        sales_impact = estimate_sales_impact(historical_data, scenarios['baseline'])
        
        # Generate recommendations
        recommendations = generate_predictive_recommendations(
            historical_data, scenarios, churn_risk
        )
        
        return jsonify({
            'product_id': product_id,
            'historical': historical_data,
            'forecast': scenarios,
            'churn_risk': churn_risk,
            'sales_impact': sales_impact,
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"Predictions error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/roi-calculator', methods=['POST'])
@simple_auth_required
def calculate_roi():
    """Calculate ROI for proposed improvements"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        improvements = data.get('improvements', [])
        
        db = get_db()
        
        # Get current metrics
        current_metrics = get_current_product_metrics(product_id, db)
        
        roi_analysis = []
        
        for improvement in improvements:
            # Estimate impact
            impact = estimate_improvement_impact(
                improvement['type'],
                improvement['investment'],
                current_metrics
            )
            
            roi = {
                'improvement': improvement['type'],
                'investment': improvement['investment'],
                'timeframe': improvement.get('timeframe', '6 months'),
                'estimated_rating_increase': impact['rating_increase'],
                'estimated_review_increase': impact['review_increase'],
                'estimated_revenue_impact': impact['revenue_impact'],
                'break_even_time': impact['break_even_time'],
                'roi_percentage': (impact['revenue_impact'] - improvement['investment']) / improvement['investment'] * 100,
                'confidence': impact['confidence']
            }
            
            roi_analysis.append(roi)
        
        return jsonify({
            'current_metrics': current_metrics,
            'roi_analysis': sorted(roi_analysis, key=lambda x: x['roi_percentage'], reverse=True)
        })
        
    except Exception as e:
        print(f"ROI calculator error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions

def generate_aspect_recommendations(aspect, sentiment, negative_ratio, keywords):
    """Generate specific recommendations for an aspect"""
    recommendations = []
    
    if negative_ratio > 0.3:
        recommendations.append({
            'priority': 'high',
            'title': f'Improve {aspect} based on customer feedback',
            'description': f'{int(negative_ratio * 100)}% of mentions about {aspect} are negative. Focus on addressing common complaints.',
            'impact': 'High',
            'effort': 'Medium'
        })
    
    # Keyword-based recommendations
    for keyword, freq in keywords[:3]:
        if any(neg in keyword.lower() for neg in ['poor', 'bad', 'terrible', 'cheap']):
            recommendations.append({
                'priority': 'medium',
                'title': f'Address "{keyword}" issues in {aspect}',
                'description': f'This issue was mentioned {freq} times in reviews.',
                'impact': 'Medium',
                'effort': 'Low'
            })
    
    return recommendations

def extract_aspect_issues(aspect, example_reviews):
    """Extract specific issues for an aspect"""
    issues = []
    negative_reviews = [r for r in example_reviews if r['sentiment'] == 'negative']
    
    for review in negative_reviews:
        # Simple issue extraction
        if 'not' in review['text'] or 'poor' in review['text']:
            issues.append(review['text'].split('.')[0])
    
    return list(set(issues))[:3]

def calculate_competitive_advantages(our_product, competitors, db):
    """Calculate competitive advantages"""
    advantages = []
    
    # Price advantage
    our_price = float(our_product.price) if our_product.price else 0
    avg_competitor_price = np.mean([float(c.price) for c in competitors if c.price]) if competitors else our_price
    
    if our_price < avg_competitor_price * 0.9:
        advantages.append({
            'icon': '💰',
            'title': 'Price Leadership',
            'description': f'{int((1 - our_price/avg_competitor_price) * 100)}% lower than competitors',
            'score': 0.9
        })
    
    # Rating advantage
    our_rating = db.query(func.avg(Review.rating)).filter_by(product_id=our_product.id).scalar() or 0
    avg_competitor_rating = np.mean([float(c.average_rating) for c in competitors if c.average_rating]) if competitors else 0
    
    if float(our_rating) > avg_competitor_rating:
        advantages.append({
            'icon': '⭐',
            'title': 'Superior Customer Satisfaction',
            'description': f'{float(our_rating):.1f} vs {avg_competitor_rating:.1f} competitor average',
            'score': float(our_rating) / 5.0
        })
    
    return advantages

def compare_features(our_product, competitors):
    """Compare features with competitors"""
    comparison = []
    
    our_features = set(our_product.key_features or [])
    
    for comp in competitors[:3]:  # Top 3 competitors
        comp_features = set(comp.key_features or [])
        
        for feature in our_features.union(comp_features):
            comparison.append({
                'name': feature,
                'our_status': 'better' if feature in our_features else 'missing',
                'their_status': 'better' if feature in comp_features else 'missing'
            })
    
    return comparison

def generate_mention_timeline(mentions):
    """Generate timeline data for competitor mentions"""
    from collections import defaultdict
    timeline_data = defaultdict(lambda: defaultdict(int))
    
    for mention in mentions:
        try:
            date = datetime.fromisoformat(mention['date']).strftime('%Y-%m')
            timeline_data[date][mention['competitor']] += 1
        except:
            pass
    
    return {
        'labels': sorted(timeline_data.keys()),
        'data': dict(timeline_data)
    }

def generate_rating_data(competitor):
    """Generate rating data for competitor"""
    return {
        'current': float(competitor.average_rating) if competitor.average_rating else 3.0,
        'trend': [3.0, 3.5, 4.0, float(competitor.average_rating) if competitor.average_rating else 3.0]  # Mock trend
    }

def generate_our_rating_data(product, db):
    """Generate rating data for our product"""
    avg_rating = db.query(func.avg(Review.rating)).filter_by(product_id=product.id).scalar() or 3.0
    return {
        'current': float(avg_rating),
        'trend': [3.0, 3.5, 4.0, float(avg_rating)]  # Mock trend
    }

def get_mention_trend(brand, mentions):
    """Get mention trend for a brand"""
    brand_mentions = [m for m in mentions if brand.lower() in m.get('competitor', '').lower()]
    return len(brand_mentions)

def prepare_historical_data(reviews):
    """Prepare historical data for predictions"""
    data = []
    for r in reviews:
        sentiment_scores = r.sentiment_scores or {}
        data.append({
            'date': r.review_date,
            'rating': r.rating,
            'sentiment_score': sentiment_scores.get('positive', 0) - sentiment_scores.get('negative', 0)
        })
    
    df = pd.DataFrame(data)
    
    # Group by week
    df['week'] = pd.to_datetime(df['date']).dt.to_period('W')
    weekly = df.groupby('week').agg({
        'rating': 'mean',
        'sentiment_score': 'mean'
    }).reset_index()
    
    return {
        'labels': [str(w) for w in weekly['week']],
        'ratings': weekly['rating'].tolist(),
        'sentiment_scores': weekly['sentiment_score'].tolist()
    }

def generate_baseline_forecast(historical_data):
    """Generate baseline forecast"""
    ratings = np.array(historical_data['ratings'])
    
    # Simple moving average forecast
    if len(ratings) >= 4:
        trend = np.mean(ratings[-4:]) - np.mean(ratings[-8:-4]) if len(ratings) >= 8 else 0
        last_avg = np.mean(ratings[-4:])
        
        forecast = []
        for i in range(4):
            next_val = last_avg + (trend * (i + 1) * 0.5)
            forecast.append(np.clip(next_val, 1, 5))
    else:
        forecast = [3.0] * 4
    
    return {
        'labels': [f'Week {i+1}' for i in range(4)],
        'ratings': forecast,
        'upper_bound': [min(f + 0.5, 5) for f in forecast],
        'lower_bound': [max(f - 0.5, 1) for f in forecast],
        'trend': float(forecast[-1] - ratings[-1]) if len(ratings) > 0 else 0,
        'confidence': 0.75,
        'final_rating': float(forecast[-1])
    }

def generate_optimistic_forecast(historical_data):
    """Generate optimistic forecast"""
    baseline = generate_baseline_forecast(historical_data)
    optimistic_ratings = [min(r * 1.1, 5) for r in baseline['ratings']]
    
    return {
        **baseline,
        'ratings': optimistic_ratings,
        'final_rating': float(optimistic_ratings[-1]),
        'confidence': 0.6
    }

def generate_pessimistic_forecast(historical_data):
    """Generate pessimistic forecast"""
    baseline = generate_baseline_forecast(historical_data)
    pessimistic_ratings = [max(r * 0.9, 1) for r in baseline['ratings']]
    
    return {
        **baseline,
        'ratings': pessimistic_ratings,
        'final_rating': float(pessimistic_ratings[-1]),
        'confidence': 0.6
    }

def calculate_churn_risk(reviews, db):
    """Calculate customer churn risk"""
    recent_reviews = [r for r in reviews if r.review_date >= datetime.now() - timedelta(days=30)]
    
    factors = []
    risk_score = 0
    
    # Factor 1: Declining ratings
    if len(recent_reviews) >= 10:
        recent_avg = np.mean([r.rating for r in recent_reviews])
        overall_avg = np.mean([r.rating for r in reviews])
        
        if recent_avg < overall_avg - 0.5:
            factors.append({
                'name': 'Declining Ratings',
                'impact': 0.8,
                'description': f'Recent ratings ({recent_avg:.1f}) are lower than average ({overall_avg:.1f})'
            })
            risk_score += 0.3
    
    # Factor 2: Negative sentiment
    if recent_reviews:
        recent_negative = sum(1 for r in recent_reviews if r.sentiment == 'negative')
        recent_negative_ratio = recent_negative / len(recent_reviews)
        
        if recent_negative_ratio > 0.3:
            factors.append({
                'name': 'High Negative Sentiment',
                'impact': 0.7,
                'description': f'{int(recent_negative_ratio * 100)}% of recent reviews are negative'
            })
            risk_score += 0.25
    
    return {
        'score': min(risk_score, 1.0),
        'factors': factors,
        'recommendation': get_churn_prevention_recommendation(risk_score)
    }

def get_churn_prevention_recommendation(risk_score):
    """Get churn prevention recommendation based on risk score"""
    if risk_score > 0.7:
        return "Immediate action required: Launch retention campaign and address quality issues"
    elif risk_score > 0.4:
        return "Monitor closely: Consider proactive customer outreach"
    else:
        return "Low risk: Continue monitoring customer satisfaction"

def estimate_sales_impact(historical_data, forecast):
    """Estimate sales impact"""
    current_rating = np.mean(historical_data['ratings'][-4:]) if len(historical_data['ratings']) >= 4 else 3.0
    predicted_rating = forecast['final_rating']
    rating_change = predicted_rating - current_rating
    
    sales_impact = rating_change * 20  # 20% per rating point
    
    return {
        'current': 100,
        'potential_increase': max(0, sales_impact),
        'potential_loss': abs(min(0, sales_impact)),
        'net_impact': sales_impact,
        'confidence': forecast['confidence']
    }

def generate_predictive_recommendations(historical_data, scenarios, churn_risk):
    """Generate recommendations"""
    recommendations = []
    
    if scenarios['baseline']['trend'] < -0.2:
        recommendations.append({
            'priority': 'high',
            'title': 'Address Declining Satisfaction Trend',
            'description': 'Rating forecast shows downward trend',
            'impact': '15',
            'action_items': ['Analyze negative reviews', 'Improve quality', 'Enhance support']
        })
    
    if churn_risk['score'] > 0.6:
        recommendations.append({
            'priority': 'high',
            'title': 'Implement Churn Prevention',
            'description': 'High risk of customer loss',
            'impact': '20',
            'action_items': ['Launch retention campaign', 'Offer incentives', 'Personal outreach']
        })
    
    return recommendations

def get_current_product_metrics(product_id, db):
    """Get current product metrics"""
    avg_rating = db.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar() or 3.0
    review_count = db.query(Review).filter_by(product_id=product_id).count()
    
    return {
        'avg_rating': float(avg_rating),
        'review_count': review_count,
        'monthly_reviews': review_count / 12  # Simplified
    }

def estimate_improvement_impact(improvement_type, investment, current_metrics):
    """Estimate impact of improvements"""
    # Simplified impact calculation
    base_impact = {
        'quality_improvement': {'rating': 0.3, 'reviews': 1.2, 'revenue': 1.15},
        'customer_service': {'rating': 0.2, 'reviews': 1.1, 'revenue': 1.08},
        'marketing': {'rating': 0.1, 'reviews': 1.5, 'revenue': 1.2}
    }
    
    impact = base_impact.get(improvement_type, {'rating': 0.1, 'reviews': 1.1, 'revenue': 1.05})
    
    return {
        'rating_increase': impact['rating'],
        'review_increase': current_metrics['review_count'] * (impact['reviews'] - 1),
        'revenue_impact': investment * impact['revenue'],
        'break_even_time': f"{int(investment / (investment * (impact['revenue'] - 1) / 12))} months",
        'confidence': 0.7
    }