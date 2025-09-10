# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.auth.models import Base
import logging

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://travel_user:secure_travel_pass_2024@localhost:5432/travel_planner"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL logging in development
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database on startup"""
    try:
        # Test connection
        with engine.connect() as connection:
            logging.info("Database connection successful")
        
        # Create tables if they don't exist
        create_tables()
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

# Health check function
def check_database_health():
    """Check if database is healthy"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False
