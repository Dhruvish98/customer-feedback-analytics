# backend/database/connection.py (updated)

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
import logging

logger = logging.getLogger(__name__)

# Build database URL from environment variables
def get_database_url():
    """Build database URL from environment variables"""
    # Check if full DATABASE_URL is provided
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return db_url
    
    # Otherwise build from components
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'ecommerce_reviews')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

DATABASE_URL = get_database_url()

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe session
db_session = scoped_session(SessionLocal)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully!")

def get_db():
    """Get database session"""
    return db_session

def close_db():
    """Close database session"""
    db_session.remove()

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful!")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False