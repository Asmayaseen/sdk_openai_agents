from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Load from environment or hardcoded for now (use dotenv in production)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yourpassword@localhost:5432/wellness_db")

# SQLAlchemy engine & session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
