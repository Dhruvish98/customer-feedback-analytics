# backend/database/models.py - Clean version without duplicates
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import bcrypt

Base = declarative_base()

# Association tables
product_competitor_association = Table('product_competitors',
    Base.metadata,
    Column('product_id', String, ForeignKey('products.id')),
    Column('competitor_product_id', String, ForeignKey('competitor_products.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields
    customer_segment = Column(String(50))  # premium, regular, budget
    lifetime_value = Column(Float, default=0)
    churn_risk_score = Column(Float, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = relationship('Review', back_populates='user')
    customer_journey = relationship('CustomerJourney', back_populates='user')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    brand = Column(String(100), nullable=False)
    price = Column(Float)
    launch_date = Column(DateTime)
    
    # New fields
    market_segment = Column(String(50))  # premium, mid-range, budget
    target_audience = Column(JSON)  # demographics
    key_features = Column(JSON)  # list of main features
    
    # Relationships
    reviews = relationship('Review', back_populates='product')
    competitors = relationship('CompetitorProduct', secondary=product_competitor_association)
    market_position = relationship('MarketPosition', back_populates='product')

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(String(50), ForeignKey('products.id'))
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=False)
    review_title = Column(String(200))
    
    # Enhanced NLP fields
    processed_text = Column(Text)
    sentiment = Column(String(20))
    sentiment_scores = Column(JSON)  # {positive: 0.8, neutral: 0.1, negative: 0.1}
    confidence_score = Column(Float)
    
    # Aspect-based sentiment
    aspect_sentiments = Column(JSON)  # {quality: positive, price: negative, ...}
    extracted_aspects = Column(JSON)  # detailed aspect analysis
    
    # Advanced NLP features
    entities = Column(JSON)  # extracted entities
    topics = Column(JSON)  # topic modeling results
    keywords = Column(JSON)  # extracted keywords
    emotion_scores = Column(JSON)  # emotion detection results
    
    # Emoji analysis field - NEW
    emoji_analysis = Column(JSON)  # {has_emojis: bool, emoji_count: int, emoji_sentiment: str, etc.}
    
    # Quality and authenticity
    quality_score = Column(Float, default=0)
    authenticity_score = Column(Float, default=0)
    spam_probability = Column(Float, default=0)
    
    # Competitor analysis
    competitor_mentions = Column(JSON)  # list of competitor mentions
    
    # Metadata
    verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    response_to_review_id = Column(Integer, ForeignKey('reviews.id'))
    
    review_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New fields for enhanced analytics
    purchase_context = Column(JSON)  # {first_time: bool, repeat_customer: bool, etc.}
    review_source = Column(String(50))  # website, mobile_app, api
    language = Column(String(10), default='en')
    
    # Relationships
    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
    responses = relationship('Review', backref='parent_review', remote_side=[id])
    aspect_sentiments_rel = relationship('AspectSentiment', back_populates='review')
    processing_log = relationship('ProcessingLog', back_populates='review', uselist=False)

class AspectSentiment(Base):
    __tablename__ = 'aspect_sentiments'
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    aspect = Column(String(50), nullable=False)
    sentiment = Column(String(20), nullable=False)
    confidence = Column(Float)
    extracted_text = Column(Text)  # relevant text for this aspect
    
    # New fields
    intensity = Column(Float)  # sentiment intensity
    context = Column(JSON)  # additional context about the aspect
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship('Review', back_populates='aspect_sentiments_rel')

class CustomerJourney(Base):
    __tablename__ = 'customer_journeys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    touchpoint = Column(String(100))  # review_submitted, product_viewed, etc.
    action = Column(String(100))
    journey_metadata = Column(JSON)  # Changed from 'metadata' to 'journey_metadata'
    
    # Enhanced tracking
    session_id = Column(String(100))
    device_type = Column(String(50))
    referrer = Column(String(200))
    duration_seconds = Column(Integer)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='customer_journey')

class CompetitorProduct(Base):
    __tablename__ = 'competitor_products'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100), nullable=False)
    category = Column(String(100))
    price = Column(Float)
    
    # Competitive intelligence
    market_share = Column(Float)
    average_rating = Column(Float)
    total_reviews = Column(Integer)
    key_features = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    
    # Tracking
    last_updated = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketPosition(Base):
    __tablename__ = 'market_positions'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(50), ForeignKey('products.id'))
    date = Column(DateTime, nullable=False)
    
    # Market metrics
    market_share = Column(Float)
    price_index = Column(Float)  # relative to market average
    quality_index = Column(Float)  # based on ratings/reviews
    brand_strength_index = Column(Float)
    
    # Competitive position
    market_rank = Column(Integer)
    category_rank = Column(Integer)
    growth_rate = Column(Float)
    
    # Sentiment metrics
    sentiment_score = Column(Float)
    nps_score = Column(Float)  # Net Promoter Score
    
    # Relationships
    product = relationship('Product', back_populates='market_position')

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50))  # critical, warning, info
    category = Column(String(100))  # sentiment_spike, quality_issue, competitor_threat
    message = Column(Text)
    
    # Alert details
    severity = Column(Integer)  # 1-5
    affected_product_id = Column(String(50), ForeignKey('products.id'))
    metrics = Column(JSON)  # relevant metrics that triggered the alert
    
    # Status tracking
    status = Column(String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by = Column(Integer, ForeignKey('users.id'))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Auto-escalation
    escalation_level = Column(Integer, default=0)
    escalated_to = Column(JSON)  # list of user IDs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcessingLog(Base):
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    
    # Processing details
    stage = Column(String(50))  # submitted, processing, complete, failed
    processing_time = Column(Float)  # in seconds
    model_used = Column(String(100))
    model_version = Column(String(20))
    
    # Performance metrics
    confidence_scores = Column(JSON)
    processing_steps = Column(JSON)  # detailed log of each step
    errors = Column(JSON)
    
    # Resource usage
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    gpu_usage = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship('Review', back_populates='processing_log')

class TrendAnalysis(Base):
    __tablename__ = 'trend_analyses'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(50), ForeignKey('products.id'))
    period = Column(String(20))  # daily, weekly, monthly
    date = Column(DateTime)
    
    # Trend metrics
    sentiment_trend = Column(JSON)  # sentiment over time
    aspect_trends = Column(JSON)  # aspect sentiment trends
    volume_trend = Column(JSON)  # review volume trend
    rating_trend = Column(JSON)  # rating distribution trend
    
    # Predictive metrics
    predicted_rating = Column(Float)
    predicted_volume = Column(Integer)
    trend_direction = Column(String(20))  # improving, stable, declining
    confidence_interval = Column(JSON)
    
    # Insights
    key_drivers = Column(JSON)  # main factors driving the trend
    recommendations = Column(JSON)  # AI-generated recommendations
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ABTest(Base):
    __tablename__ = 'ab_tests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(Text)
    
    # Test configuration
    test_type = Column(String(50))  # product_feature, pricing, messaging
    control_group = Column(JSON)
    test_group = Column(JSON)
    
    # Test period
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20))  # planned, active, completed, cancelled
    
    # Results
    control_metrics = Column(JSON)
    test_metrics = Column(JSON)
    statistical_significance = Column(Float)
    winner = Column(String(20))  # control, test, inconclusive
    
    # Impact analysis
    estimated_impact = Column(JSON)
    recommendations = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelPerformance(Base):
    __tablename__ = 'model_performance'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(100))
    model_version = Column(String(20))
    evaluation_date = Column(DateTime)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Detailed metrics by category
    metrics_by_category = Column(JSON)
    confusion_matrix = Column(JSON)
    
    # Model details
    training_samples = Column(Integer)
    test_samples = Column(Integer)
    feature_importance = Column(JSON)
    hyperparameters = Column(JSON)
    
    # Drift detection
    data_drift_score = Column(Float)
    concept_drift_detected = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Helper function to create all tables
def create_tables(engine):
    Base.metadata.create_all(engine)