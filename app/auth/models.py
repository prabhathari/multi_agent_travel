# app/auth/models.py - Fixed version without circular references
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, Text, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # FIXED: Simplified relationships to avoid circular references
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    origin_city = Column(String(255))
    preferred_budget = Column(Integer, default=1500)
    favorite_interests = Column(ARRAY(Text))
    notification_settings = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="preferences")

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    destination = Column(String(255), nullable=False)
    origin_city = Column(String(255), nullable=False)
    days = Column(Integer, nullable=False)
    month = Column(String(50), nullable=False)
    budget_total = Column(DECIMAL(10,2), nullable=False)
    interests = Column(ARRAY(Text), nullable=False)
    visa_passport = Column(String(100))
    preferred_destination = Column(String(255))
    trip_data = Column(JSONB, nullable=False)  # Complete trip plan from AI
    status = Column(String(50), default="completed")
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trips")
    feedback = relationship("Feedback", back_populates="trip", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    aspects = Column(ARRAY(Text))  # What they liked
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # FIXED: Proper relationships
    trip = relationship("Trip", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(Text)
    ip_address = Column(INET)
    
    # Relationship
    user = relationship("User", back_populates="sessions")
