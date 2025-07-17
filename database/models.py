from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from .session import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    uid = Column(String(50), unique=True, nullable=False)
    goal = Column(Text)
    diet_preferences = Column(Text)


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    metrics = Column(Text)
