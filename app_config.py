import os  
import logging
from enum import Enum
from typing import Optional, Dict
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator, ValidationInfo, Extra
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field, field_validator, ValidationInfo

# Load environment variables from .env
load_dotenv()


# ----------------------------
# 🔹 ENUMS
# ----------------------------

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ----------------------------
# 🔹 Agent Configuration
# ----------------------------

class AgentConfig(BaseModel):

    name: str
    system_prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=300, gt=0)
    streaming: bool = True


# ----------------------------
# 🔹 Application Configuration
# ----------------------------

class AppConfig(BaseModel):
    # App Info
    app_name: str = "Health & Wellness Planner"
    version: str = "1.0.0"
    description: str = "AI-powered health assistant with specialized agents"

    # API & Model Config
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-1.5-flash")
    database_url: Optional[str] = Field(default=None)
    api_timeout: int = 30

    # Agent Definitions
    default_agent: str = "wellness"
    agents: Dict[str, AgentConfig] = {
        "wellness": AgentConfig(
            name="Wellness",
            system_prompt="You are a friendly health assistant. Provide general wellness advice."
        ),
        "nutrition": AgentConfig(
            name="Nutrition",
            system_prompt="You are a certified nutritionist. Give specific dietary recommendations."
        ),
        "injury": AgentConfig(
            name="Injury Support",
            system_prompt="You are a physical therapist. Suggest safe recovery methods."
        ),
        "escalation": AgentConfig(
            name="Escalation",
            system_prompt="Handle escalations to human specialists professionally."
        )
    }

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[Path] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Session
    max_session_duration: int = 3600
    session_timeout: int = 300

    # Guardrails
    max_message_length: int = 1000
    max_history_length: int = 20

    # Flags
    enable_streaming: bool = True
    enable_handoffs: bool = True
    mock_mode: bool = Field(default=False)

    # Internal Config
    class Config:
        extra = "allow"  

    # Validators
    @field_validator("gemini_api_key", mode="before")
    @classmethod
    def validate_gemini_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        mock_mode = info.data.get("mock_mode") if info.data else None
        if not mock_mode and not v:
            raise ValueError("GEMINI_API_KEY is required when not in mock mode")
        return v

    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: Optional[Path]) -> Optional[Path]:
        if v and not v.parent.exists():
            v.parent.mkdir(parents=True, exist_ok=True)
        return v


# ----------------------------
# 🔹 Logging Setup
# ----------------------------

def configure_logging(config: AppConfig):
    handlers = [logging.StreamHandler()]
    if config.log_file:
        handlers.append(logging.FileHandler(str(config.log_file)))

    logging.basicConfig(
        level=config.log_level.value,
        format=config.log_format,
        handlers=handlers
    )


# ----------------------------
# 🔹 Export config instance
# ----------------------------

# Initialize config with environment variables
app_config = AppConfig(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    database_url=os.getenv("DATABASE_URL"),
    mock_mode=os.getenv("MOCK_MODE", "false").lower() == "true"
)
config = app_config