import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional but useful for local dev)
load_dotenv()

class Config:
    """Application configuration."""

    def __init__(self):
        # Gemini Configuration
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        # Database Configuration
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///wellness.db")

        # Application Settings
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.MAX_CONVERSATION_HISTORY: int = 50
        self.DEFAULT_TEMPERATURE: float = 0.7
        self.MAX_TOKENS: int = 1000

        # Report Settings
        self.REPORTS_DIR: str = "reports"

    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.GEMINI_API_KEY)

# Create a config instance
config = Config()
