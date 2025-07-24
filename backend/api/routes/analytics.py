# backend/api/routes/analytics.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from database.models import Review, Product, Alert, TrendAnalysis
from database.connection import get_db
from utils.auth_decorator import simple_auth_required, get_current_user_id  # Updated import
import pandas as pd
import numpy as np

bp = Blueprint('analytics', __name__)

@bp.route('/dashboard-stats', methods=['GET'])
@simple_auth_required  # Changed from @jwt_required()
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        db = get_db()
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get total reviews
        total_reviews = db.query(Review).filter(
            Review.created_at >= start_date
        ).count()
        
        # Average rating
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.created_at >= start_date
        ).scalar()
        
        # Sentiment distribution
        sentiments = db.query(
            Review.sentiment,
            func.count(Review.id)
        ).filter(
            Review.created_at >= start_date
        ).group_by(Review.sentiment).all()
        
        sentiment_dist = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        for sentiment, count in sentiments:
            if sentiment:  # Check if sentiment is not None
                sentiment_dist[sentiment] = count
        
        # Category distribution
        categories = db.query(
            Product.category,
            func.count(Review.id)
        ).join(Review).filter(
            Review.created_at >= start_date
        ).group_by(Product.category).all()
        
        category_dist = {cat: count for cat, count in categories}
        
        # Top products
        top_products = db.query(
            Product.id,
            Product.name,
            func.count(Review.id).label('review_count'),
            func.avg(Review.rating).label('avg_rating')
        ).join(Review).filter(
            Review.created_at >= start_date
        ).group_by(Product.id, Product.name).order_by(
            func.count(Review.id).desc()
        ).limit(10).all()
        
        # Calculate positive ratio for each product
        top_products_data = []
        for product in top_products:
            positive_count = db.query(Review).filter(
                Review.product_id == product.id,
                Review.sentiment == 'positive',
                Review.created_at >= start_date
            ).count()
            
            top_products_data.append({
                'id': product.id,
                'name': product.name,
                'review_count': product.review_count,
                'avg_rating': float(product.avg_rating) if product.avg_rating else 0,
                'positive_ratio': positive_count / product.review_count if product.review_count else 0
            })
        
        return jsonify({
            'total_reviews': total_reviews,
            'average_rating': float(avg_rating) if avg_rating else 0,
            'sentiment_distribution': sentiment_dist,
            'categories': category_dist,
            'top_products': top_products_data
        })
        
    except Exception as e:
        print(f"Dashboard stats error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/sentiment-trend', methods=['GET'])
@simple_auth_required
def get_sentiment_trend():
    """Get sentiment trend over time"""
    try:
        db = get_db()
        days = int(request.args.get('days', 30))
        
        # Get daily sentiment counts
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create date series
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Get reviews within date range
        reviews = db.query(
            Review.created_at,
            Review.sentiment
        ).filter(
            Review.created_at >= start_date,
            Review.created_at <= end_date
        ).all()
        
        # Process data
        if reviews:
            df = pd.DataFrame(reviews, columns=['created_at', 'sentiment'])
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            
            # Group by date and sentiment
            sentiment_by_date = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
            
            # Ensure all sentiments are present
            for sentiment in ['positive', 'neutral', 'negative']:
                if sentiment not in sentiment_by_date.columns:
                    sentiment_by_date[sentiment] = 0
            
            # Reindex to ensure all dates are present
            sentiment_by_date = sentiment_by_date.reindex(date_range.date, fill_value=0)
            
            # Convert to format suitable for Chart.js
            labels = [date.strftime('%Y-%m-%d') for date in sentiment_by_date.index]
            
            datasets = [
                {
                    'label': 'Positive',
                    'data': sentiment_by_date['positive'].tolist(),
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                },
                {
                    'label': 'Neutral',
                    'data': sentiment_by_date['neutral'].tolist(),
                    'borderColor': 'rgb(255, 205, 86)',
                    'backgroundColor': 'rgba(255, 205, 86, 0.2)'
                },
                {
                    'label': 'Negative',
                    'data': sentiment_by_date['negative'].tolist(),
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                }
            ]
        else:
            # No data - return empty structure
            labels = [date.strftime('%Y-%m-%d') for date in date_range]
            datasets = [
                {'label': 'Positive', 'data': [0] * len(labels), 'borderColor': 'rgb(75, 192, 192)'},
                {'label': 'Neutral', 'data': [0] * len(labels), 'borderColor': 'rgb(255, 205, 86)'},
                {'label': 'Negative', 'data': [0] * len(labels), 'borderColor': 'rgb(255, 99, 132)'}
            ]
        
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
        
    except Exception as e:
        print(f"Sentiment trend error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/top-products', methods=['GET'])
@simple_auth_required
def get_top_products():
    """Get top performing products"""
    try:
        db = get_db()
        limit = int(request.args.get('limit', 10))
        
        # Get top products by review count and rating
        products = db.query(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            func.count(Review.id).label('review_count'),
            func.avg(Review.rating).label('avg_rating'),
            func.sum(func.case([(Review.sentiment == 'positive', 1)], else_=0)).label('positive_count')
        ).join(Review).group_by(
            Product.id, Product.name, Product.category, Product.price
        ).order_by(
            func.count(Review.id).desc()
        ).limit(limit).all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': float(product.price) if product.price else 0,
                'review_count': product.review_count,
                'avg_rating': float(product.avg_rating) if product.avg_rating else 0,
                'positive_ratio': product.positive_count / product.review_count if product.review_count > 0 else 0
            })
        
        return jsonify({'products': result})
        
    except Exception as e:
        print(f"Top products error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/recent-alerts', methods=['GET'])
@simple_auth_required
def get_recent_alerts():
    """Get recent alerts"""
    try:
        db = get_db()
        limit = int(request.args.get('limit', 10))
        
        alerts = db.query(Alert).filter_by(
            status='active'
        ).order_by(
            Alert.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for alert in alerts:
            result.append({
                'id': alert.id,
                'type': alert.type,
                'category': alert.category,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat() if alert.created_at else None
            })
        
        return jsonify({'alerts': result})
        
    except Exception as e:
        print(f"Recent alerts error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/category-performance', methods=['GET'])
@simple_auth_required
def get_category_performance():
    """Get performance metrics by category"""
    try:
        db = get_db()
        
        # Get metrics by category
        categories = db.query(
            Product.category,
            func.count(Review.id).label('review_count'),
            func.avg(Review.rating).label('avg_rating'),
            func.sum(func.case([(Review.sentiment == 'positive', 1)], else_=0)).label('positive_count'),
            func.sum(func.case([(Review.sentiment == 'negative', 1)], else_=0)).label('negative_count')
        ).join(Review).group_by(Product.category).all()
        
        labels = []
        review_counts = []
        avg_ratings = []
        sentiment_scores = []
        
        for category in categories:
            labels.append(category.category)
            review_counts.append(category.review_count)
            avg_ratings.append(float(category.avg_rating) if category.avg_rating else 0)
            
            # Calculate sentiment score
            total = category.positive_count + category.negative_count
            if total > 0:
                score = (category.positive_count / total) * 100
            else:
                score = 50
            sentiment_scores.append(score)
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Review Count',
                    'data': review_counts,
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)'
                },
                {
                    'label': 'Average Rating',
                    'data': avg_ratings,
                    'backgroundColor': 'rgba(153, 102, 255, 0.6)'
                },
                {
                    'label': 'Sentiment Score',
                    'data': sentiment_scores,
                    'backgroundColor': 'rgba(255, 159, 64, 0.6)'
                }
            ]
        })
        
    except Exception as e:
        print(f"Category performance error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/category/<category>', methods=['GET'])
@simple_auth_required
def get_category_analytics(category):
    """Get detailed analytics for a specific category"""
    try:
        db = get_db()
        
        # Get all products in the category
        products_in_category = db.query(Product).filter_by(category=category).all()
        
        if not products_in_category:
            return jsonify({
                'total_products': 0,
                'total_reviews': 0,
                'average_rating': 0,
                'top_brand': 'N/A',
                'products': [],
                'brand_comparison': {}
            })
        
        product_ids = [p.id for p in products_in_category]
        
        # Get all reviews for products in this category
        reviews = db.query(Review).filter(Review.product_id.in_(product_ids)).all()
        
        # Calculate overall statistics
        total_reviews = len(reviews)
        average_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
        
        # Get products with their analytics
        products_data = []
        brand_stats = {}
        
        for product in products_in_category:
            # Get reviews for this product
            product_reviews = [r for r in reviews if r.product_id == product.id]
            review_count = len(product_reviews)
            
            if review_count > 0:
                avg_rating = sum(r.rating for r in product_reviews) / review_count
                positive_count = sum(1 for r in product_reviews if r.sentiment == 'positive')
                positive_percentage = (positive_count / review_count) * 100
            else:
                avg_rating = 0
                positive_percentage = 0
            
            products_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'brand': product.brand,
                'average_rating': avg_rating,
                'review_count': review_count,
                'positive_percentage': positive_percentage,
                'price': float(product.price) if product.price else 0
            })
            
            # Aggregate brand statistics
            if product.brand not in brand_stats:
                brand_stats[product.brand] = {
                    'total_reviews': 0,
                    'total_rating': 0,
                    'positive_count': 0,
                    'product_count': 0
                }
            
            brand_stats[product.brand]['total_reviews'] += review_count
            brand_stats[product.brand]['total_rating'] += sum(r.rating for r in product_reviews)
            brand_stats[product.brand]['positive_count'] += sum(1 for r in product_reviews if r.sentiment == 'positive')
            brand_stats[product.brand]['product_count'] += 1
        
        # Calculate brand comparison data
        brand_comparison = {}
        for brand, stats in brand_stats.items():
            if stats['total_reviews'] > 0:
                brand_comparison[brand] = {
                    'avg_rating': stats['total_rating'] / stats['total_reviews'],
                    'review_count': stats['total_reviews'],
                    'positive_percentage': (stats['positive_count'] / stats['total_reviews']) * 100,
                    'product_count': stats['product_count']
                }
        
        # Find top brand by review count
        top_brand = max(brand_comparison.items(), key=lambda x: x[1]['review_count'])[0] if brand_comparison else 'N/A'
        
        return jsonify({
            'total_products': len(products_in_category),
            'total_reviews': total_reviews,
            'average_rating': average_rating,
            'top_brand': top_brand,
            'products': products_data,
            'brand_comparison': brand_comparison
        })
        
    except Exception as e:
        print(f"Category analytics error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@bp.route('/product/<product_id>', methods=['GET'])
@simple_auth_required
def get_product_analytics(product_id):
    """Get detailed analytics for a specific product"""
    try:
        db = get_db()
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        print(f"Product analytics - Product ID: {product_id}, Days: {days}, Start date: {start_date}")
        
        # Get product details
        product = db.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get all reviews for this product
        all_reviews = db.query(Review).filter_by(product_id=product_id).all()
        
        # Filter reviews based on date range
        # Check which date field to use - created_at or review_date
        filtered_reviews = []
        for review in all_reviews:
            review_date = review.created_at or review.review_date
            if review_date and review_date >= start_date:
                filtered_reviews.append(review)
        
        print(f"Total reviews: {len(all_reviews)}, Filtered reviews (last {days} days): {len(filtered_reviews)}")
        
        # Use filtered reviews for calculations
        reviews_to_analyze = filtered_reviews if filtered_reviews else all_reviews
        total_reviews = len(reviews_to_analyze)
        
        if total_reviews > 0:
            avg_rating = sum(r.rating for r in reviews_to_analyze) / total_reviews
        else:
            avg_rating = 0
        
        # Sentiment distribution for filtered period
        sentiment_dist = {'positive': 0, 'negative': 0, 'neutral': 0}
        for review in reviews_to_analyze:
            if review.sentiment in sentiment_dist:
                sentiment_dist[review.sentiment] += 1
        
        # Most common sentiment
        if sentiment_dist:
            most_common_sentiment = max(sentiment_dist, key=sentiment_dist.get)
        else:
            most_common_sentiment = 'neutral'
        
        # Rating distribution for filtered period
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews_to_analyze:
            if 1 <= review.rating <= 5:
                rating_dist[review.rating] += 1
        
        # Calculate trend (compare recent half vs older half of the filtered period)
        if len(reviews_to_analyze) >= 10:
            sorted_reviews = sorted(reviews_to_analyze, key=lambda r: r.created_at or r.review_date or datetime.min)
            mid_point = len(sorted_reviews) // 2
            
            older_half = sorted_reviews[:mid_point]
            recent_half = sorted_reviews[mid_point:]
            
            older_avg = sum(r.rating for r in older_half) / len(older_half) if older_half else 0
            recent_avg = sum(r.rating for r in recent_half) / len(recent_half) if recent_half else 0
            
            trend = recent_avg - older_avg
        else:
            trend = 0
        
        # Reviews per day (for the selected period)
        if total_reviews > 0 and days > 0:
            reviews_per_day = total_reviews / days
        else:
            reviews_per_day = 0
        
        # Extract top topics from keywords (from filtered reviews)
        topic_counts = {}
        for review in reviews_to_analyze:
            if review.keywords:
                for keyword in review.keywords:
                    if isinstance(keyword, dict):
                        topic = keyword.get('keyword', '')
                    else:
                        topic = str(keyword)
                    
                    if topic:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Get top 10 topics
        top_topics = []
        if topic_counts:
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_topics = [{'name': topic, 'count': count} for topic, count in sorted_topics]
        
        response_data = {
            'product_name': product.name,
            'category': product.category,
            'brand': product.brand,
            'average_rating': avg_rating,
            'total_reviews': total_reviews,
            'sentiment_distribution': sentiment_dist,
            'rating_distribution': rating_dist,
            'most_common_sentiment': most_common_sentiment,
            'trend': trend,
            'reviews_per_day': reviews_per_day,
            'top_topics': top_topics,
            'time_period': days  # Include this to verify the filter is working
        }
        
        print(f"Returning data for {days} days period with {total_reviews} reviews")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Product analytics error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500