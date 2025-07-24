# backend/database/setup.py

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database.models import Base
from database.connection import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create database if it doesn't exist (for local PostgreSQL only)"""
    # Parse database URL
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")
    
    # For AWS RDS, the database should already exist
    if 'rds.amazonaws.com' in db_url:
        logger.info("Using AWS RDS, skipping database creation")
        return
    
    # For local PostgreSQL, create database if needed
    try:
        # Connect to PostgreSQL server (not specific database)
        parts = db_url.split('/')
        server_url = '/'.join(parts[:-1]) + '/postgres'
        db_name = parts[-1].split('?')[0]
        
        # Create engine for server connection
        server_engine = create_engine(server_url, isolation_level='AUTOCOMMIT')
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name}
            )
            exists = result.fetchone() is not None
            
            if not exists:
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_extensions():
    """Create required PostgreSQL extensions"""
    try:
        with engine.connect() as conn:
            # Create extensions if they don't exist
            extensions = ['uuid-ossp', 'pg_trgm']
            for ext in extensions:
                try:
                    conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\""))
                    conn.commit()
                    logger.info(f"Extension '{ext}' created/verified")
                except Exception as e:
                    logger.warning(f"Could not create extension '{ext}': {e}")
    except Exception as e:
        logger.error(f"Error creating extensions: {e}")

def create_tables():
    """Create all database tables"""
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def create_indexes():
    """Create custom indexes for better performance"""
    indexes = [
        # Reviews table indexes
        "CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews(review_date)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_category ON reviews(category)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_brand ON reviews(brand)",
        
        # Full text search index
        "CREATE INDEX IF NOT EXISTS idx_reviews_text_search ON reviews USING gin(to_tsvector('english', review_text))",
        
        # Processing logs indexes
        "CREATE INDEX IF NOT EXISTS idx_processing_logs_review_id ON processing_logs(review_id)",
        "CREATE INDEX IF NOT EXISTS idx_processing_logs_created_at ON processing_logs(created_at)",
        
        # Users table indexes
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)"
    ]
    
    try:
        with engine.connect() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
                conn.commit()
                logger.info(f"Index created: {index_sql.split('idx_')[1].split(' ')[0]}")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def create_initial_data():
    """Create initial data like admin user"""
    from database.models import User
    from sqlalchemy.orm import sessionmaker
    from werkzeug.security import generate_password_hash
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if admin exists
        admin = session.query(User).filter_by(email='admin@example.com').first()
        
        if not admin:
            # Create admin user
            admin = User(
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                name='System Admin',
                role='admin'
            )
            session.add(admin)
            session.commit()
            logger.info("Admin user created (email: admin@example.com, password: admin123)")
        else:
            logger.info("Admin user already exists")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        session.rollback()
    finally:
        session.close()

def verify_connection():
    """Verify database connection and configuration"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Database connection successful!")
            logger.info(f"PostgreSQL version: {version}")
            
            # Get database size
            result = conn.execute(text("""
                SELECT pg_database_size(current_database()) as size
            """))
            size = result.fetchone()[0]
            logger.info(f"Database size: {size / 1024 / 1024:.2f} MB")
            
            # Count tables
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.fetchone()[0]
            logger.info(f"Number of tables: {table_count}")
            
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def setup_database():
    """Main function to setup the complete database"""
    logger.info("Starting database setup...")
    
    # Step 1: Create database (if local)
    create_database_if_not_exists()
    
    # Step 2: Verify connection
    if not verify_connection():
        raise Exception("Cannot connect to database")
    
    # Step 3: Create extensions
    create_extensions()
    
    # Step 4: Create tables
    create_tables()
    
    # Step 5: Create indexes
    create_indexes()
    
    # Step 6: Create initial data
    create_initial_data()
    
    logger.info("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()