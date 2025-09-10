# app/auth/utils.py
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.auth.models import User, UserSession
import secrets

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def create_session_token(user_id: str, db: Session, user_agent: str = None, ip_address: str = None) -> str:
    """Create a session token and store it in the database"""
    # Create JWT token
    token_data = {"sub": str(user_id), "type": "access"}
    token = create_access_token(token_data)
    
    # Hash token for storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Store session in database
    db_session = UserSession(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(db_session)
    db.commit()
    
    return token

def verify_session_token(token: str, db: Session) -> Optional[User]:
    """Verify a session token and return the user"""
    # Verify JWT
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Check if session exists in database
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db_session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not db_session:
        return None
    
    # Get user
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    return user

def invalidate_session(token: str, db: Session) -> bool:
    """Invalidate a session token"""
    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db_session = db.query(UserSession).filter(UserSession.token_hash == token_hash).first()
        
        if db_session:
            db.delete(db_session)
            db.commit()
            return True
        return False
    except:
        return False

def cleanup_expired_sessions(db: Session):
    """Clean up expired sessions from database"""
    try:
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.delete(session)
        
        db.commit()
        return len(expired_sessions)
    except:
        return 0

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def create_user(email: str, name: str, password: str, db: Session) -> Optional[User]:
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return None
        
        # Create user
        hashed_password = hash_password(password)
        db_user = User(
            email=email,
            name=name,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except:
        db.rollback()
        return None

def generate_secure_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)
