# backend/scripts/generate_advanced_data.py - Updated version with emojis
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db, init_db
from database.models import *
from datetime import datetime, timedelta
import random
import json
from faker import Faker
import bcrypt

fake = Faker()

# Sample data with emojis
REVIEW_TEMPLATES = {
    'positive': [
        "Absolutely love this product! 😍 The quality is amazing and it arrived super fast 🚀",
        "Best purchase ever! 💯 Highly recommend to everyone 👍",
        "Exceeded my expectations! 🌟 Will definitely buy again 😊",
        "Perfect! Just what I was looking for 👌 Great value for money 💰",
        "Amazing quality! 🎉 My friends are jealous 😄",
        "So happy with this purchase! 😃 Works exactly as described ✨",
        "Fantastic product! 🏆 Customer service was also excellent 👏",
        "Love it! ❤️ Using it every day now 😊",
        "Outstanding quality! 💎 Worth every penny 💵",
        "Brilliant! 🌟 Arrived earlier than expected 📦"
    ],
    'negative': [
        "Disappointed with the quality 😞 Not worth the price 👎",
        "Product broke after 2 days 😠 Very frustrated 😤",
        "Not as described 😕 Feeling cheated 💔",
        "Terrible experience 😡 Would not recommend ❌",
        "Complete waste of money 😢 Very poor quality 🚫",
        "Arrived damaged 📦💥 Customer service unhelpful 😒",
        "Cheap materials, overpriced 😑 Save your money 💸",
        "Stopped working after a week 🛑 Very disappointed 😔",
        "False advertising! 🤥 Nothing like the pictures 📸",
        "Worst purchase ever 😖 Returning immediately 📮"
    ],
    'neutral': [
        "It's okay, nothing special 🤷 Does the job I guess",
        "Average product 😐 You get what you pay for",
        "Not bad, not great either 🤔 Just mediocre",
        "Decent quality but overpriced 💭 Mixed feelings",
        "Works as expected 📦 Nothing extraordinary",
        "It's fine 😶 No complaints but not impressed",
        "Acceptable quality 🆗 Serves its purpose",
        "Standard product 📋 Nothing to write home about",
        "Middle of the road 🛣️ Could be better, could be worse",
        "Functional but basic 🔧 Does what it's supposed to"
    ]
}

CATEGORIES = {
    'Electronics': {
        'subcategories': ['Smartphones', 'Laptops', 'Headphones', 'Cameras', 'Tablets'],
        'brands': ['TechPro', 'ElectroMax', 'GigaTech', 'SmartLife', 'DigiWorld'],
        'aspects': ['battery life', 'screen quality', 'performance', 'build quality', 'value']
    },
    'Fashion': {
        'subcategories': ['Clothing', 'Shoes', 'Accessories', 'Bags', 'Watches'],
        'brands': ['StyleCo', 'TrendSet', 'UrbanWear', 'ClassicFit', 'ModernLook'],
        'aspects': ['fit', 'material quality', 'style', 'comfort', 'durability']
    },
    'Home & Kitchen': {
        'subcategories': ['Furniture', 'Appliances', 'Decor', 'Cookware', 'Storage'],
        'brands': ['HomeStyle', 'KitchenPro', 'ComfortLiving', 'ModernHome', 'EasyLife'],
        'aspects': ['quality', 'functionality', 'design', 'durability', 'ease of use']
    },
    'Beauty': {
        'subcategories': ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Tools'],
        'brands': ['GlowBeauty', 'PureGlow', 'BeautyPro', 'NaturalCare', 'LuxeBeauty'],
        'aspects': ['effectiveness', 'texture', 'scent', 'packaging', 'value']
    },
    'Sports': {
        'subcategories': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports', 'Winter Sports'],
        'brands': ['SportMax', 'ActiveLife', 'ProGear', 'FitnessPro', 'OutdoorKing'],
        'aspects': ['durability', 'comfort', 'performance', 'quality', 'design']
    }
}

def create_users(db, num_users=100):
    """Create sample users"""
    print("Creating users...")
    users = []
    
    # Create admin user
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        role="admin",
        customer_segment="premium",
        lifetime_value=50000.0
    )
    users.append(admin)
    
    # Create regular test user
    test_user = User(
        name="Test User",
        email="user@example.com",
        password_hash=bcrypt.hashpw("user123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        role="user",
        customer_segment="regular",
        lifetime_value=5000.0
    )
    users.append(test_user)
    
    # Create random users
    for i in range(num_users - 2):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            password_hash=bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role="user",
            customer_segment=random.choice(['premium', 'regular', 'budget']),
            lifetime_value=random.uniform(100, 10000),
            churn_risk_score=random.uniform(0, 1)
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    print(f"✅ Created {len(users)} users")
    return users

def create_products(db):
    """Create sample products"""
    print("Creating products...")
    products = []
    product_id = 1
    
    for category, info in CATEGORIES.items():
        for subcategory in info['subcategories']:
            for brand in info['brands']:
                for i in range(5):  # 5 products per brand per subcategory
                    product = Product(
                        id=f"PROD{product_id:05d}",
                        name=f"{brand} {subcategory} {fake.word().title()} {random.choice(['Pro', 'Plus', 'Max', 'Elite', 'Premium'])}",
                        category=category,
                        subcategory=subcategory,
                        brand=brand,
                        price=round(random.uniform(20, 2000), 2),
                        launch_date=fake.date_between(start_date='-2y', end_date='today'),
                        market_segment=random.choice(['premium', 'mid-range', 'budget']),
                        target_audience={
                            'age_group': random.choice(['18-25', '26-35', '36-45', '46-55', '55+']),
                            'gender': random.choice(['male', 'female', 'unisex']),
                            'income_level': random.choice(['low', 'medium', 'high'])
                        },
                        key_features=[fake.word() for _ in range(random.randint(3, 6))]
                    )
                    products.append(product)
                    product_id += 1
    
    db.add_all(products)
    db.commit()
    print(f"✅ Created {len(products)} products")
    return products

def create_reviews_with_emojis(db, users, products, num_reviews=10000):
    """Create sample reviews with emojis and NLP fields populated"""
    print("Creating reviews with emojis...")
    reviews = []
    
    for i in range(num_reviews):
        user = random.choice(users)
        product = random.choice(products)
        
        # Determine sentiment
        sentiment_choice = random.choices(
            ['positive', 'negative', 'neutral'],
            weights=[0.6, 0.2, 0.2]
        )[0]
        
        # Get review template with emojis
        review_text = random.choice(REVIEW_TEMPLATES[sentiment_choice])
        
        # Add some product-specific content
        aspect = random.choice(CATEGORIES[product.category]['aspects'])
        if sentiment_choice == 'positive':
            review_text += f" The {aspect} is excellent!"
        elif sentiment_choice == 'negative':
            review_text += f" The {aspect} is terrible."
        else:
            review_text += f" The {aspect} is okay."
        
        # Set rating based on sentiment
        if sentiment_choice == 'positive':
            rating = random.choice([4, 5, 5, 5])  # More 5s
        elif sentiment_choice == 'negative':
            rating = random.choice([1, 1, 2, 2])  # More 1s
        else:
            rating = random.choice([3, 3, 4])
        
        # Create emoji analysis
        emoji_analysis = {
            'has_emojis': True,
            'emoji_count': len([c for c in review_text if ord(c) > 127]),
            'emoji_sentiment': sentiment_choice,
            'emoji_sentiment_score': {'positive': 0.8, 'negative': -0.8, 'neutral': 0.0}[sentiment_choice],
            'emoji_breakdown': {
                'positive': review_text.count('😊') + review_text.count('😍') + review_text.count('👍'),
                'negative': review_text.count('😞') + review_text.count('😠') + review_text.count('👎'),
                'neutral': review_text.count('🤷') + review_text.count('😐')
            }
        }
        
        # Create sentiment scores
        sentiment_scores = {
            'positive': 0.1,
            'neutral': 0.1,
            'negative': 0.1
        }
        sentiment_scores[sentiment_choice] = 0.8
        
        # Create aspect sentiments
        aspect_sentiments = {}
        for asp in CATEGORIES[product.category]['aspects']:
            if asp in review_text.lower():
                aspect_sentiments[asp] = {
                    'mentioned': True,
                    'sentiment': sentiment_choice,
                    'confidence': random.uniform(0.7, 0.95)
                }
        
        review = Review(
            user_id=user.id,
            product_id=product.id,
            rating=rating,
            review_title=f"{sentiment_choice.title()} experience with {product.name}",
            review_text=review_text,
            processed_text=review_text.lower().replace('!', '').replace('?', ''),
            sentiment=sentiment_choice,
            sentiment_scores=sentiment_scores,
            confidence_score=random.uniform(0.7, 0.95),
            aspect_sentiments=aspect_sentiments,
            extracted_aspects=aspect_sentiments,
            emoji_analysis=emoji_analysis,
            emotion_scores={
                'joy': random.uniform(0, 1) if sentiment_choice == 'positive' else 0,
                'sadness': random.uniform(0, 1) if sentiment_choice == 'negative' else 0,
                'anger': random.uniform(0, 1) if sentiment_choice == 'negative' else 0,
                'fear': random.uniform(0, 0.3),
                'surprise': random.uniform(0, 0.5),
                'neutral': random.uniform(0, 1) if sentiment_choice == 'neutral' else 0
            },
            quality_score=random.uniform(0.6, 0.95),
            authenticity_score=random.uniform(0.7, 0.98),
            spam_probability=random.uniform(0.01, 0.15),
            verified_purchase=random.choice([True, True, True, False]),  # 75% verified
            helpful_count=random.randint(0, 100),
            review_date=fake.date_time_between(start_date='-1y', end_date='now'),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            review_source=random.choice(['website', 'mobile_app', 'api'])
        )
        
        reviews.append(review)
        
        if (i + 1) % 1000 == 0:
            db.add_all(reviews)
            db.commit()
            reviews = []
            print(f"  Created {i + 1}/{num_reviews} reviews...")
    
    if reviews:
        db.add_all(reviews)
        db.commit()
    
    print(f"✅ Created {num_reviews} reviews with emojis")

def create_alerts(db, products):
    """Create sample alerts"""
    print("Creating alerts...")
    alerts = []
    
    alert_types = [
        {
            'type': 'critical',
            'category': 'sentiment_spike',
            'message': 'Sudden increase in negative reviews detected'
        },
        {
            'type': 'warning',
            'category': 'quality_issue',
            'message': 'Multiple reviews mentioning quality problems'
        },
        {
            'type': 'info',
            'category': 'competitor_threat',
            'message': 'Increased competitor mentions in reviews'
        }
    ]
    
    for product in random.sample(products, min(20, len(products))):
        alert_type = random.choice(alert_types)
        alert = Alert(
            type=alert_type['type'],
            category=alert_type['category'],
            message=f"{alert_type['message']} for {product.name}",
            severity=random.randint(1, 5),
            affected_product_id=product.id,
            metrics={
                'negative_review_count': random.randint(5, 50),
                'sentiment_change': random.uniform(-0.5, -0.1),
                'time_period': '24h'
            },
            status='active'
        )
        alerts.append(alert)
    
    db.add_all(alerts)
    db.commit()
    print(f"✅ Created {len(alerts)} alerts")

def main():
    """Generate all sample data"""
    print("🚀 Starting data generation for PostgreSQL database...")
    
    # Initialize database
    init_db()
    
    # Get database session
    db = get_db()
    
    try:
        # Clear existing data (optional - comment out to preserve data)
        print("Clearing existing data...")
        db.query(Review).delete()
        db.query(Alert).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()
        
        # Create data
        users = create_users(db, num_users=100)
        products = create_products(db)
        create_reviews_with_emojis(db, users, products, num_reviews=10000)
        create_alerts(db, products)
        
        print("\n✅ Data generation completed successfully!")
        
        # Print summary
        print("\n📊 Database Summary:")
        print(f"Users: {db.query(User).count()}")
        print(f"Products: {db.query(Product).count()}")
        print(f"Reviews: {db.query(Review).count()}")
        print(f"Alerts: {db.query(Alert).count()}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()