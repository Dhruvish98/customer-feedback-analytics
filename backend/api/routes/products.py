# backend/api/routes/products.py - Complete file with all endpoints
from flask import Blueprint, request, jsonify
from utils.auth_decorator import simple_auth_required
from database.models import Product, Review
from database.connection import get_db
from sqlalchemy import func, or_, distinct
import traceback

bp = Blueprint('products', __name__)

@bp.route('/list', methods=['GET'])
@simple_auth_required
def get_products_list():
    """Get list of products for review submission"""
    try:
        db = get_db()
        
        # Get search query and filters
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '')
        brand = request.args.get('brand', '')
        limit = int(request.args.get('limit', 1000))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = db.query(Product)
        
        # Apply search filter
        if search:
            search_filter = or_(
                Product.name.ilike(f'%{search}%'),
                Product.brand.ilike(f'%{search}%'),
                Product.category.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Apply category filter
        if category:
            query = query.filter_by(category=category)
            
        # Apply brand filter
        if brand:
            query = query.filter_by(brand=brand)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        products_query = query.order_by(Product.name).offset(offset).limit(limit)
        
        # Get products with review counts
        products = []
        for product in products_query.all():
            # Get review statistics
            review_stats = db.query(
                func.count(Review.id).label('count'),
                func.avg(Review.rating).label('avg_rating')
            ).filter_by(product_id=product.id).first()
            
            products.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'subcategory': product.subcategory,
                'brand': product.brand,
                'price': float(product.price) if product.price else 0,
                'review_count': review_stats.count if review_stats else 0,
                'avg_rating': float(review_stats.avg_rating) if review_stats and review_stats.avg_rating else 0
            })
        
        return jsonify({
            'products': products,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        print(f"Get products error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get products'}), 500

@bp.route('/categories', methods=['GET'])
@simple_auth_required
def get_categories():
    """Get list of available product categories"""
    try:
        db = get_db()
        
        # Get unique categories
        categories = db.query(Product.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({'categories': sorted(category_list)})
        
    except Exception as e:
        print(f"Get categories error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get categories'}), 500

@bp.route('/brands', methods=['GET'])
@simple_auth_required
def get_brands():
    """Get list of brands, optionally filtered by category"""
    try:
        db = get_db()
        category = request.args.get('category', '')
        
        # Build query
        query = db.query(Product.brand).distinct()
        
        if category:
            query = query.filter(Product.category == category)
        
        # Get unique brands
        brands_result = query.all()
        brands = [brand[0] for brand in brands_result if brand[0]]
        
        return jsonify({'brands': sorted(brands)})
        
    except Exception as e:
        print(f"Get brands error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get brands'}), 500

@bp.route('/<product_id>', methods=['GET'])
@simple_auth_required
def get_product_details(product_id):
    """Get detailed product information"""
    try:
        db = get_db()
        
        product = db.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get review statistics
        reviews = db.query(Review).filter_by(product_id=product_id).all()
        
        # Calculate statistics
        total_reviews = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total_reviews if reviews else 0
        
        # Rating distribution
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_dist[review.rating] += 1
        
        # Recent reviews
        recent_reviews = sorted(reviews, key=lambda r: r.created_at, reverse=True)[:5]
        
        return jsonify({
            'product': {
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'subcategory': product.subcategory,
                'brand': product.brand,
                'price': float(product.price) if product.price else 0,
                'launch_date': product.launch_date.isoformat() if product.launch_date else None,
                'market_segment': product.market_segment,
                'key_features': product.key_features
            },
            'statistics': {
                'total_reviews': total_reviews,
                'average_rating': avg_rating,
                'rating_distribution': rating_dist
            },
            'recent_reviews': [
                {
                    'id': r.id,
                    'rating': r.rating,
                    'review_text': r.review_text[:200] + '...' if len(r.review_text) > 200 else r.review_text,
                    'sentiment': r.sentiment,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                }
                for r in recent_reviews
            ]
        })
        
    except Exception as e:
        print(f"Get product details error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to get product details'}), 500

@bp.route('/search', methods=['GET'])
@simple_auth_required
def search_products():
    """Search products with autocomplete support"""
    try:
        db = get_db()
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'products': []})
        
        # Search in name, brand, and category
        search_filter = or_(
            Product.name.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%'),
            Product.category.ilike(f'%{query}%')
        )
        
        products = db.query(Product).filter(search_filter).limit(10).all()
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price) if product.price else 0
            })
        
        return jsonify({'products': results})
        
    except Exception as e:
        print(f"Search products error: {str(e)}")
        return jsonify({'error': 'Failed to search products'}), 500

@bp.route('/stats', methods=['GET'])
@simple_auth_required
def get_product_stats():
    """Get overall product statistics"""
    try:
        db = get_db()
        
        total_products = db.query(Product).count()
        total_reviews = db.query(Review).count()
        
        # Get category distribution
        category_stats = db.query(
            Product.category,
            func.count(Product.id)
        ).group_by(Product.category).all()
        
        # Get brand distribution
        brand_stats = db.query(
            Product.brand,
            func.count(Product.id)
        ).group_by(Product.brand).order_by(func.count(Product.id).desc()).limit(10).all()
        
        return jsonify({
            'total_products': total_products,
            'total_reviews': total_reviews,
            'categories': {cat: count for cat, count in category_stats},
            'top_brands': {brand: count for brand, count in brand_stats}
        })
        
    except Exception as e:
        print(f"Get product stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500