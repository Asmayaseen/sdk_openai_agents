from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    activity_level = Column(String)
    goal_type = Column(String)
    goal_target = Column(Float)
    goal_unit = Column(String)
    goal_deadline = Column(String)
    dietary_preference = Column(String)
    food_allergies = Column(Text)  # JSON string
    medical_conditions = Column(Text)  # JSON string
    injury_notes = Column(Text)
    theme = Column(String, default='light')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress_entries = relationship("ProgressEntry", back_populates="user")
    conversations = relationship("ConversationMessage", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    handoffs = relationship("AgentHandoff", back_populates="user")

class ProgressEntry(Base):
    """Progress tracking entries."""
    __tablename__ = 'progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String)
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress_entries")

class ConversationMessage(Base):
    """Conversation history."""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class MealPlan(Base):
    """Meal plans storage."""
    __tablename__ = 'meal_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    plan_name = Column(String)
    plan_data = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")

class WorkoutPlan(Base):
    """Workout plans storage."""
    __tablename__ = 'workout_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    plan_name = Column(String)
    plan_data = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workout_plans")

class AgentHandoff(Base):
    """Agent handoff logs."""
    __tablename__ = 'handoffs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    from_agent = Column(String, nullable=False)
    to_agent = Column(String, nullable=False)
    reason = Column(Text)
    context_snapshot = Column(Text)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="handoffs")
