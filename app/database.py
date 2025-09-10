# app/database.py - Fixed version with better model handling
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import logging

# Import models to ensure they're registered
from app.auth.models import Base

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://travel_user:prabhat_db_pass_2024@database:5432/travel_planner"
)

# Handle PostgreSQL URL format issues
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def create_engine_with_fallback():
    """Create database engine with SQLite fallback"""
    try:
        # Try PostgreSQL first
        if DATABASE_URL.startswith("postgresql"):
            engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for SQL debugging
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logging.info("PostgreSQL connection successful")
            return engine
            
    except Exception as e:
        logging.warning(f"PostgreSQL connection failed: {e}")
        logging.info("Falling back to SQLite...")
        
        # Fallback to SQLite
        sqlite_url = "sqlite:///./travel_planner.db"
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        return engine

# Create engine
engine = create_engine_with_fallback()

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    try:
        # Import all models to ensure they're registered
        from app.auth.models import User, UserPreference, Trip, Feedback, UserSession
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
        
        # Create demo user if needed
        create_demo_user_if_needed()
            
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def create_demo_user_if_needed():
    """Create demo user for testing if it doesn't exist"""
    try:
        from app.auth.utils import create_user
        from app.auth.models import UserPreference, User
        
        db = SessionLocal()
        
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if not existing_user:
            # Create demo user
            demo_user = create_user(
                email="demo@example.com",
                name="Demo User",
                password="demo123",
                db=db
            )
            
            if demo_user:
                # Create demo preferences
                demo_prefs = UserPreference(
                    user_id=demo_user.id,
                    origin_city="Hyderabad",
                    favorite_interests=["culture", "food"],
                    preferred_budget=1500
                )
                db.add(demo_prefs)
                db.commit()
                logging.info("Demo user created successfully")
        
        db.close()
        
    except Exception as e:
        logging.warning(f"Could not create demo user: {e}")

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
            connection.execute(text("SELECT 1"))
            logging.info("Database connection successful")
        
        # Create tables if they don't exist
        create_tables()
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

def check_database_health():
    """Check if database is healthy"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False
