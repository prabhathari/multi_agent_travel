# app/auth/utils.py - Fixed version
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.auth.models import User, UserSession
import secrets
import logging

SECRET_KEY = os.getenv("SECRET_KEY", "XYZ123_your_super_secret_random_key_here_make_it_very_long_ABC789")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

def create_session_token(user_id: str, db: Session, user_agent: str = None, ip_address: str = None) -> str:
    token_data = {"sub": str(user_id), "type": "access"}
    token = create_access_token(token_data)
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
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
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db_session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not db_session:
        return None
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    return user

def invalidate_session(token: str, db: Session) -> bool:
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

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    # CRITICAL FIX: Normalize email
    email = email.strip().lower()
    
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    user.last_login = datetime.utcnow()
    db.commit()
    return user

def create_user(email: str, name: str, password: str, db: Session) -> Optional[User]:
    try:
        # CRITICAL FIX: Normalize email to lowercase
        email = email.strip().lower()
        name = name.strip()
        
        if not email or not name or not password:
            return None
        
        if len(password) < 6:
            return None
        
        # CRITICAL FIX: Proper duplicate check
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logging.warning(f"User already exists: {email}")
            return None
        
        hashed_password = hash_password(password)
        db_user = User(
            email=email,
            name=name,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logging.info(f"User created successfully: {email}")
        return db_user
        
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        db.rollback()
        return None

def generate_secure_token() -> str:
    return secrets.token_urlsafe(32)
