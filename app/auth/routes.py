# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.auth.utils import (
    authenticate_user, create_user, create_session_token, 
    verify_session_token, invalidate_session
)
from app.auth.models import User, UserPreference

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response Models
class UserSignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    origin_city: Optional[str] = "Hyderabad"
    favorite_interests: Optional[list] = ["culture", "food"]

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str

# Helper function to get current user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    user = verify_session_token(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/signup", response_model=LoginResponse)
def signup(user_data: UserSignupRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Create user
    db_user = create_user(
        email=user_data.email,
        name=user_data.name,
        password=user_data.password,
        db=db
    )
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user preferences
    db_preferences = UserPreference(
        user_id=db_user.id,
        origin_city=user_data.origin_city,
        favorite_interests=user_data.favorite_interests,
        preferred_budget=1500
    )
    db.add(db_preferences)
    db.commit()
    
    # Create session token
    access_token = create_session_token(db_user.id, db)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            last_login=db_user.last_login
        )
    )

@router.post("/login", response_model=LoginResponse)
def login(user_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return token"""
    
    # Authenticate user
    user = authenticate_user(user_data.email, user_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session token
    access_token = create_session_token(user.id, db)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    )

@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate token"""
    
    token = credentials.credentials
    success = invalidate_session(token, db)
    
    if success:
        return MessageResponse(message="Successfully logged out")
    else:
        return MessageResponse(message="Already logged out")

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.get("/check", response_model=MessageResponse)
def check_auth(current_user: User = Depends(get_current_user)):
    """Check if user is authenticated"""
    
    return MessageResponse(message=f"Authenticated as {current_user.name}")

# Helper route to get user preferences
@router.get("/preferences")
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create default preferences if none exist
        preferences = UserPreference(
            user_id=current_user.id,
            origin_city="Hyderabad",
            favorite_interests=["culture", "food"],
            preferred_budget=1500
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return {
        "origin_city": preferences.origin_city,
        "favorite_interests": preferences.favorite_interests,
        "preferred_budget": preferences.preferred_budget,
        "notification_settings": preferences.notification_settings
    }

@router.put("/preferences")
def update_user_preferences(
    preferences_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
    
    # Update fields
    if "origin_city" in preferences_data:
        preferences.origin_city = preferences_data["origin_city"]
    if "favorite_interests" in preferences_data:
        preferences.favorite_interests = preferences_data["favorite_interests"]
    if "preferred_budget" in preferences_data:
        preferences.preferred_budget = preferences_data["preferred_budget"]
    if "notification_settings" in preferences_data:
        preferences.notification_settings = preferences_data["notification_settings"]
    
    db.commit()
    
    return MessageResponse(message="Preferences updated successfully")
