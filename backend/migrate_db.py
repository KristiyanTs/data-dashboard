"""
Database migration script to add scraper fields
Run this once to update your existing database
"""
from sqlalchemy import create_engine, text
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./contracts.db"

def migrate():
    """Add new columns for scraper functionality"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add source column
            conn.execute(text("ALTER TABLE contracts ADD COLUMN source VARCHAR(100)"))
            print("✅ Added 'source' column")
        except Exception as e:
            print(f"⚠️  'source' column already exists or error: {e}")
        
        try:
            # Add external_id column
            conn.execute(text("ALTER TABLE contracts ADD COLUMN external_id VARCHAR(200)"))
            print("✅ Added 'external_id' column")
        except Exception as e:
            print(f"⚠️  'external_id' column already exists or error: {e}")
        
        try:
            # Add country column
            conn.execute(text("ALTER TABLE contracts ADD COLUMN country VARCHAR(3)"))
            print("✅ Added 'country' column")
        except Exception as e:
            print(f"⚠️  'country' column already exists or error: {e}")
        
        conn.commit()
    
    print("\n✅ Migration complete!")
    print("You can now use the scraper feature.")

if __name__ == "__main__":
    print("🔄 Running database migration...")
    print("This will add scraper-related columns to your contracts table.\n")
    
    migrate()
