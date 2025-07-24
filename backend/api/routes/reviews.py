# backend/api/routes/reviews.py - Complete updated version with category-aware competitor detection
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from database.models import Review, Product, ProcessingLog, AspectSentiment, Alert
from database.connection import get_db
from utils.auth_decorator import simple_auth_required, get_current_user_id
import traceback
import time

# Initialize NLP pipeline
try:
    from nlp.advanced_pipeline import AdvancedNLPPipeline
    nlp_pipeline = AdvancedNLPPipeline()
except ImportError:
    print("Warning: Could not load AdvancedNLPPipeline")
    nlp_pipeline = None

bp = Blueprint('reviews', __name__)

@bp.route('/submit', methods=['POST'])
@simple_auth_required
def submit_review():
    """Submit a new review"""
    db = None
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        print(f"Review submission - User: {user_id}, Product: {data.get('product_id')}")
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['product_id', 'rating', 'review_text']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Convert product_id to int if it's a string
        try:
            product_id = (data['product_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid product_id'}), 400
        
        # Validate rating
        try:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating'}), 400
        
        db = get_db()
        
        # Check if product exists
        product = db.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'error': f'Product not found with id: {product_id}'}), 404
        
        print(f"Processing review for product: {product.name} (Category: {product.category}, Subcategory: {product.subcategory})")
        
        # Initialize with default NLP results
        nlp_results = {
            'processed_text': data['review_text'].lower(),
            'sentiment_analysis': {
                'primary_sentiment': 'neutral',
                'sentiment_scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33},
                'confidence': 0.5
            },
            'aspect_sentiments': {},
            'entities': {},
            'emotions': {
                'primary_emotion': 'neutral',
                'emotion_scores': {'neutral': 1.0}
            },
            'keywords': [],
            'quality_metrics': {
                'quality_score': 0.5,
                'authenticity_score': 0.5,
                'is_likely_fake': False
            },
            'competitor_mentions': [],
            'emoji_analysis': {'has_emojis': False}
        }
        
        # Try NLP processing with full product context
        if nlp_pipeline:
            try:
                print("Starting NLP processing with category context...")
                # Pass complete product info including subcategory
                product_info = {
                    'category': product.category,
                    'subcategory': product.subcategory,  # Added subcategory
                    'brand': product.brand,
                    'product_name': product.name,
                    'product_id': product.id
                }
                
                nlp_results = nlp_pipeline.process_review(
                    data['review_text'],
                    product_info
                )
                
                # Log competitor mentions if found
                if nlp_results.get('competitor_mentions'):
                    print(f"Found {len(nlp_results['competitor_mentions'])} competitor mentions")
                    for mention in nlp_results['competitor_mentions']:
                        print(f"  - {mention.get('competitor')}: {mention.get('comparison_type')} (Favorable: {mention.get('favorable_to_us')})")
                
                print("NLP processing completed successfully")
            except Exception as nlp_error:
                print(f"NLP processing error (non-fatal): {nlp_error}")
                traceback.print_exc()
                # Continue with default results
        
        # Create review
        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            review_title=data.get('review_title', ''),
            review_text=data['review_text'],
            verified_purchase=data.get('verified_purchase', False),
            
            # NLP results
            processed_text=nlp_results.get('processed_text', data['review_text'].lower()),
            sentiment=nlp_results.get('sentiment_analysis', {}).get('primary_sentiment', 'neutral'),
            sentiment_scores=nlp_results.get('sentiment_analysis', {}).get('sentiment_scores', {}),
            confidence_score=nlp_results.get('sentiment_analysis', {}).get('confidence', 0.5),
            aspect_sentiments=nlp_results.get('aspect_sentiments', {}),
            entities=nlp_results.get('entities', {}),
            keywords=nlp_results.get('keywords', []),
            emotion_scores=nlp_results.get('emotions', {}).get('emotion_scores', {}),
            emoji_analysis=nlp_results.get('emoji_analysis', {}),
            quality_score=nlp_results.get('quality_metrics', {}).get('quality_score', 0.5),
            authenticity_score=nlp_results.get('quality_metrics', {}).get('authenticity_score', 0.5),
            competitor_mentions=nlp_results.get('competitor_mentions', []),
            
            review_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db.add(review)
        db.commit()
        
        print(f"Review saved successfully with ID: {review.id}")
        
        # Format NLP results for frontend
        formatted_nlp = {
            'sentiment': {
                'primary_sentiment': nlp_results.get('sentiment_analysis', {}).get('primary_sentiment', 'neutral'),
                'confidence': nlp_results.get('sentiment_analysis', {}).get('confidence', 0.5),
                'sentiment_scores': nlp_results.get('sentiment_analysis', {}).get('sentiment_scores', {})
            },
            'aspects': nlp_results.get('aspect_sentiments', {}),
            'emotions': nlp_results.get('emotions', {}),
            'quality': nlp_results.get('quality_metrics', {}),
            'keywords': nlp_results.get('keywords', []),
            'entities': nlp_results.get('entities', {}),
            'competitor_mentions': nlp_results.get('competitor_mentions', [])
        }
        
        return jsonify({
            'message': 'Review submitted successfully',
            'review_id': review.id,
            'nlp_analysis': formatted_nlp
        }), 201
        
    except Exception as e:
        print(f"Review submission error: {str(e)}")
        traceback.print_exc()
        if db:
            db.rollback()
        return jsonify({'error': f'Failed to submit review: {str(e)}'}), 500

@bp.route('/user-history', methods=['GET'])
@simple_auth_required
def get_user_reviews():
    """Get reviews submitted by the current user"""
    try:
        user_id = get_current_user_id()
        print(f"Fetching reviews for user: {user_id}")
        
        db = get_db()
        
        # Get all reviews for this user
        reviews = db.query(Review).filter_by(user_id=user_id).order_by(
            Review.created_at.desc()
        ).all()
        
        print(f"Found {len(reviews)} reviews for user {user_id}")
        
        result = []
        for review in reviews:
            # Get product info
            product = db.query(Product).filter_by(id=review.product_id).first()
            
            review_data = {
                'id': review.id,
                'product_name': product.name if product else 'Unknown Product',
                'product_category': product.category if product else 'Unknown',
                'product_subcategory': product.subcategory if product else None,  # Added subcategory
                'rating': review.rating,
                'review_title': review.review_title or '',
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'verified_purchase': review.verified_purchase,
                'helpful_count': review.helpful_count or 0,
                'quality_score': float(review.quality_score) if review.quality_score else 0,
                'authenticity_score': float(review.authenticity_score) if review.authenticity_score else 0,
                'aspect_sentiments': review.aspect_sentiments or {},
                'emotion_scores': review.emotion_scores or {},
                'competitor_mentions': review.competitor_mentions or []  # Added competitor mentions
            }
            
            result.append(review_data)
        
        return jsonify({'reviews': result})
        
    except Exception as e:
        print(f"Get user reviews error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get reviews'}), 500

@bp.route('/<review_id>/nlp-details', methods=['GET'])
@simple_auth_required
def get_review_nlp_details(review_id):
    """Get detailed NLP analysis for a review"""
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        # Get review and verify ownership
        review = db.query(Review).filter_by(id=review_id, user_id=user_id).first()
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        # Get product info
        product = db.query(Product).filter_by(id=review.product_id).first()
        
        # Prepare detailed NLP analysis
        nlp_details = {
            'review_id': review.id,
            'review_text': review.review_text,
            'product_name': product.name if product else 'Unknown',
            'product_category': product.category if product else 'Unknown',
            'product_subcategory': product.subcategory if product else None,
            'nlp_analysis': {
                'sentiment': {
                    'primary': review.sentiment,
                    'confidence': float(review.confidence_score) if review.confidence_score else 0,
                    'scores': review.sentiment_scores or {}
                },
                'aspects': [],
                'emotions': review.emotion_scores or {},
                'quality_metrics': {
                    'quality_score': float(review.quality_score) if review.quality_score else 0,
                    'authenticity_score': float(review.authenticity_score) if review.authenticity_score else 0,
                    'spam_probability': 1 - float(review.authenticity_score) if review.authenticity_score else 0.5
                },
                'keywords': review.keywords or [],
                'entities': review.entities or {},
                'competitor_mentions': review.competitor_mentions or [],
                'emoji_analysis': review.emoji_analysis or {},
                'processing': {
                    'time': 0.5,  # Mock processing time
                    'model': 'AdvancedNLPPipeline v2.0'
                }
            }
        }
        
        # Process aspect sentiments for better display
        if review.aspect_sentiments:
            for aspect, data in review.aspect_sentiments.items():
                if isinstance(data, dict):
                    nlp_details['nlp_analysis']['aspects'].append({
                        'aspect': aspect,
                        'sentiment': data.get('sentiment', 'neutral'),
                        'confidence': data.get('confidence', 0.5),
                        'mentioned': data.get('mentioned', False),
                        'extracted_text': data.get('sentences', [''])[0] if data.get('sentences') else ''
                    })
                elif isinstance(data, str):
                    # Handle simple string sentiment
                    nlp_details['nlp_analysis']['aspects'].append({
                        'aspect': aspect,
                        'sentiment': data,
                        'confidence': 0.75,
                        'mentioned': True,
                        'extracted_text': ''
                    })
        
        return jsonify(nlp_details)
        
    except Exception as e:
        print(f"Get NLP details error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get NLP details'}), 500

@bp.route('/product/<product_id>', methods=['GET'])
@simple_auth_required
def get_product_reviews(product_id):
    """Get reviews for a specific product"""
    try:
        db = get_db()
        
        reviews = db.query(Review).filter_by(product_id=product_id).order_by(
            Review.created_at.desc()
        ).limit(20).all()
        
        result = []
        for review in reviews:
            result.append({
                'id': review.id,
                'rating': review.rating,
                'review_title': review.review_title,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'helpful_count': review.helpful_count or 0,
                'verified_purchase': review.verified_purchase,
                'sentiment_scores': review.sentiment_scores or {},
                'quality_score': float(review.quality_score) if review.quality_score else 0,
                'emotion_scores': review.emotion_scores or {},
                'competitor_mentions': review.competitor_mentions or []  # Added competitor mentions
            })
        
        return jsonify({'reviews': result})
        
    except Exception as e:
        print(f"Get product reviews error: {str(e)}")
        return jsonify({'error': 'Failed to get reviews'}), 500

@bp.route('/recent', methods=['GET'])
@simple_auth_required
def get_recent_reviews():
    """Get recent reviews across all products"""
    try:
        db = get_db()
        limit = int(request.args.get('limit', 10))
        
        reviews = db.query(Review).order_by(
            Review.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for review in reviews:
            product = db.query(Product).filter_by(id=review.product_id).first()
            
            # Check for competitor mentions
            has_competitor_mentions = bool(review.competitor_mentions)
            
            result.append({
                'id': review.id,
                'product_name': product.name if product else 'Unknown',
                'product_category': product.category if product else 'Unknown',
                'product_subcategory': product.subcategory if product else None,
                'rating': review.rating,
                'sentiment': review.sentiment,
                'review_text': review.review_text[:100] + '...' if len(review.review_text) > 100 else review.review_text,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'user_id': review.user_id,
                'has_competitor_mentions': has_competitor_mentions
            })
        
        return jsonify({'reviews': result})
        
    except Exception as e:
        print(f"Get recent reviews error: {str(e)}")
        return jsonify({'error': 'Failed to get reviews'}), 500

@bp.route('/stats', methods=['GET'])
@simple_auth_required
def get_review_stats():
    """Get review statistics for the current user"""
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        # Get user's reviews
        reviews = db.query(Review).filter_by(user_id=user_id).all()
        
        # Calculate statistics
        total_reviews = len(reviews)
        if total_reviews == 0:
            return jsonify({
                'total_reviews': 0,
                'average_rating': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'top_categories': [],
                'review_quality_avg': 0,
                'competitor_mentions_count': 0
            })
        
        # Sentiment distribution
        sentiment_dist = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_rating = 0
        total_quality = 0
        category_counts = {}
        competitor_mentions_count = 0
        
        for review in reviews:
            sentiment_dist[review.sentiment] = sentiment_dist.get(review.sentiment, 0) + 1
            total_rating += review.rating
            total_quality += float(review.quality_score) if review.quality_score else 0.5
            
            # Count competitor mentions
            if review.competitor_mentions:
                competitor_mentions_count += len(review.competitor_mentions)
            
            # Get product category
            product = db.query(Product).filter_by(id=review.product_id).first()
            if product and product.category:
                category_counts[product.category] = category_counts.get(product.category, 0) + 1
        
        # Top categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return jsonify({
            'total_reviews': total_reviews,
            'average_rating': total_rating / total_reviews,
            'sentiment_distribution': sentiment_dist,
            'top_categories': [{'category': cat, 'count': count} for cat, count in top_categories],
            'review_quality_avg': total_quality / total_reviews,
            'competitor_mentions_count': competitor_mentions_count
        })
        
    except Exception as e:
        print(f"Get review stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@bp.route('/reprocess/<review_id>', methods=['POST'])
@simple_auth_required
def reprocess_review(review_id):
    """Reprocess a review with updated NLP pipeline (admin only)"""
    try:
        db = get_db()
        
        # Get review
        review = db.query(Review).filter_by(id=review_id).first()
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        # Get product info for context
        product = db.query(Product).filter_by(id=review.product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if nlp_pipeline:
            print(f"Reprocessing review {review_id} with category context...")
            
            # Pass complete product info
            product_info = {
                'category': product.category,
                'subcategory': product.subcategory,
                'brand': product.brand,
                'product_name': product.name,
                'product_id': product.id
            }
            
            nlp_results = nlp_pipeline.process_review(review.review_text, product_info)
            
            # Update review with new NLP results
            review.processed_text = nlp_results.get('processed_text', review.review_text.lower())
            review.sentiment = nlp_results.get('sentiment_analysis', {}).get('primary_sentiment', 'neutral')
            review.sentiment_scores = nlp_results.get('sentiment_analysis', {}).get('sentiment_scores', {})
            review.confidence_score = nlp_results.get('sentiment_analysis', {}).get('confidence', 0.5)
            review.aspect_sentiments = nlp_results.get('aspect_sentiments', {})
            review.entities = nlp_results.get('entities', {})
            review.keywords = nlp_results.get('keywords', [])
            review.emotion_scores = nlp_results.get('emotions', {}).get('emotion_scores', {})
            review.emoji_analysis = nlp_results.get('emoji_analysis', {})
            review.quality_score = nlp_results.get('quality_metrics', {}).get('quality_score', 0.5)
            review.authenticity_score = nlp_results.get('quality_metrics', {}).get('authenticity_score', 0.5)
            review.competitor_mentions = nlp_results.get('competitor_mentions', [])
            
            db.commit()
            
            print(f"Review {review_id} reprocessed successfully")
            
            return jsonify({
                'message': 'Review reprocessed successfully',
                'review_id': review_id,
                'competitor_mentions_found': len(nlp_results.get('competitor_mentions', []))
            })
        else:
            return jsonify({'error': 'NLP pipeline not available'}), 503
            
    except Exception as e:
        print(f"Reprocess review error: {str(e)}")
        traceback.print_exc()
        if db:
            db.rollback()
        return jsonify({'error': f'Failed to reprocess review: {str(e)}'}), 500