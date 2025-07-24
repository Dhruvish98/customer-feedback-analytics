# backend/data/load_data.py

import sys
import os

# Add the backend directory to Python path so we can import modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from database.models import Review, User, ProcessingLog
from nlp.pipeline import NLPPipeline
from werkzeug.security import generate_password_hash
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.nlp_pipeline = NLPPipeline()
        self.Session = sessionmaker(bind=engine)
        
    def create_users_from_reviews(self, df):
        """Create user records from the review data"""
        logger.info("Creating users from review data...")
        
        session = self.Session()
        try:
            # Get unique user IDs from the dataset
            unique_user_ids = df['user_id'].unique()
            
            created_users = 0
            for user_id in unique_user_ids:
                # Check if user already exists
                existing_user = session.query(User).filter_by(id=int(user_id.replace('USER', ''))).first()
                if not existing_user:
                    # Create a new user
                    user = User(
                        id=int(user_id.replace('USER', '')),
                        email=f"user_{user_id}@example.com",
                        password_hash=generate_password_hash('password123'),
                        name=f"User {user_id}",
                        role='customer',
                        created_at=datetime.now()
                    )
                    session.add(user)
                    created_users += 1
            
            session.commit()
            logger.info(f"Created {created_users} new users")
            
        except Exception as e:
            logger.error(f"Error creating users: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def load_reviews_to_database(self, df):
        """Load reviews to database with NLP processing"""
        logger.info("Loading reviews to database...")
        
        session = self.Session()
        try:
            total_reviews = len(df)
            processed_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Check if review already exists
                    existing_review = session.query(Review).filter_by(review_id=row['review_id']).first()
                    if existing_review:
                        logger.info(f"Review {row['review_id']} already exists, skipping...")
                        continue
                    
                    # Prepare review data for NLP processing
                    review_data = {
                        'review_id': row['review_id'],
                        'user_id': int(row['user_id'].replace('USER', '')),
                        'product_id': row['product_id'],
                        'product_name': row['product_name'],
                        'category': row['category'],
                        'brand': row['brand'],
                        'rating': row['rating'],
                        'review_text': row['review_text'],
                        'review_date': datetime.strptime(row['review_date'], '%Y-%m-%d'),
                        'verified_purchase': row['verified_purchase']
                    }
                    
                    # Process through NLP pipeline
                    processing_start = datetime.now()
                    nlp_result = self.nlp_pipeline.process_single_review(review_data)
                    processing_end = datetime.now()
                    
                    # Create review record
                    review = Review(
                        review_id=review_data['review_id'],
                        user_id=review_data['user_id'],
                        product_id=review_data['product_id'],
                        product_name=review_data['product_name'],
                        category=review_data['category'],
                        brand=review_data['brand'],
                        rating=review_data['rating'],
                        review_text=review_data['review_text'],
                        review_date=review_data['review_date'],
                        verified_purchase=review_data['verified_purchase'],
                        sentiment=nlp_result['sentiment'],
                        sentiment_confidence=nlp_result['sentiment_confidence'],
                        processed_text=nlp_result['processed_text'],
                        entities=nlp_result['entities'],
                        aspects=nlp_result['aspects'],
                        helpful_votes=row.get('helpful_votes', 0),
                        total_votes=row.get('total_votes', 0)
                    )
                    
                    session.add(review)
                    
                    # Create processing log
                    processing_log = ProcessingLog(
                        review_id=review_data['review_id'],
                        processing_time=(processing_end - processing_start).total_seconds(),
                        pipeline_details=nlp_result['processing_details']
                    )
                    session.add(processing_log)
                    
                    processed_count += 1
                    
                    # Commit every 100 reviews to avoid memory issues
                    if processed_count % 100 == 0:
                        session.commit()
                        logger.info(f"Processed {processed_count}/{total_reviews} reviews...")
                
                except Exception as e:
                    logger.error(f"Error processing review {row['review_id']}: {e}")
                    session.rollback()
                    continue
            
            # Final commit
            session.commit()
            logger.info(f"Successfully loaded {processed_count} reviews to database")
            
        except Exception as e:
            logger.error(f"Error loading reviews: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def load_dataset(self, filepath):
        """Main function to load dataset from file"""
        logger.info(f"Loading dataset from {filepath}")
        
        try:
            # Load the dataset
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                raise ValueError("File must be CSV or JSON format")
            
            logger.info(f"Loaded {len(df)} reviews from dataset")
            
            # Create users first
            self.create_users_from_reviews(df)
            
            # Load reviews
            self.load_reviews_to_database(df)
            
            logger.info("Dataset loading completed successfully!")
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python load_data.py <path_to_dataset>")
        print("Example: python load_data.py backend/data/raw/ecommerce_reviews.csv")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist")
        sys.exit(1)
    
    loader = DataLoader()
    loader.load_dataset(filepath)

if __name__ == "__main__":
    main() 