# backend/scripts/add_emoji_analysis_column.py
"""
Migration script to add emoji_analysis column to reviews table
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def add_emoji_analysis_column():
    """Add emoji_analysis column to reviews table if it doesn't exist"""
    
    # Create engine
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce_reviews.db')
    engine = create_engine(DATABASE_URL)
    
    try:
        # Check if column already exists
        with engine.connect() as conn:
            # For SQLite
            if 'sqlite' in DATABASE_URL:
                result = conn.execute(text("PRAGMA table_info(reviews)"))
                columns = [row[1] for row in result]
                
                if 'emoji_analysis' not in columns:
                    print("Adding emoji_analysis column to reviews table...")
                    conn.execute(text("ALTER TABLE reviews ADD COLUMN emoji_analysis TEXT"))
                    conn.commit()
                    print("Column added successfully!")
                else:
                    print("emoji_analysis column already exists.")
            
            # For PostgreSQL
            elif 'postgresql' in DATABASE_URL:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='reviews' AND column_name='emoji_analysis'
                """))
                
                if result.rowcount == 0:
                    print("Adding emoji_analysis column to reviews table...")
                    conn.execute(text("ALTER TABLE reviews ADD COLUMN emoji_analysis JSONB"))
                    conn.commit()
                    print("Column added successfully!")
                else:
                    print("emoji_analysis column already exists.")
            
            # For MySQL
            elif 'mysql' in DATABASE_URL:
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'reviews' 
                    AND COLUMN_NAME = 'emoji_analysis'
                """))
                
                if result.rowcount == 0:
                    print("Adding emoji_analysis column to reviews table...")
                    conn.execute(text("ALTER TABLE reviews ADD COLUMN emoji_analysis JSON"))
                    conn.commit()
                    print("Column added successfully!")
                else:
                    print("emoji_analysis column already exists.")
                    
    except OperationalError as e:
        print(f"Error adding column: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = add_emoji_analysis_column()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)