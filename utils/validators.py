from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Literal, Optional, Dict, Any
from datetime import time, date

# --- Validators for various API payloads and user input (Gemini-ready) ---

class TimeValidator(BaseModel):
    """Validates time input: HH:MM, 24-hour, returns time object."""
    time_str: str = Field(
        ..., 
        pattern=r"^(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$",
        description="Time string in 24-hour format (HH:MM)"
    )
    @field_validator('time_str')
    @classmethod
    def convert_to_time(cls, v: str) -> time:
        hours, minutes = map(int, v.split(':'))
        return time(hour=hours, minute=minutes)

class WeightValidator(BaseModel):
    """Validates weight (0 < value ≤ 300) -- kg or lbs."""
    value: float = Field(..., gt=0, le=300)
    unit: Literal["kg", "lbs"] = "kg"
    @field_validator('value')
    @classmethod
    def round_weight(cls, v: float) -> float:
        return round(v, 1)

class ExerciseLevelValidator(BaseModel):
    """Standardizes/validates exercise level."""
    level: Literal["beginner", "intermediate", "advanced"]
    @property
    def numeric_level(self) -> int:
        return ["beginner", "intermediate", "advanced"].index(self.level)

def validate_user_data(user_data: Dict[str, Any]) -> bool:
    """Validates user input dict for Gemini/AI/LLM."""
    required_fields = ['age', 'height', 'weight', 'activity_level']
    try:
        if not all(field in user_data for field in required_fields):
            return False
        if isinstance(user_data.get("weight"), dict):
            WeightValidator(**user_data["weight"])
        if "exercise_level" in user_data:
            ExerciseLevelValidator(level=user_data["exercise_level"])
        for key, value in user_data.items():
            if isinstance(value, str) and ":" in value:
                TimeValidator(time_str=value)
        return True
    except ValidationError as e:
        print(f"[Validation Error] {e}")
        return False

class UserGoalValidator(BaseModel):
    """Validates a user wellness goal: description, weights, deadline, etc."""
    description: str = Field(..., min_length=10, max_length=200)
    current_weight: WeightValidator
    target_weight: WeightValidator
    deadline: Optional[date] = None
    preferred_time: Optional[TimeValidator] = None
    @field_validator('description')
    @classmethod
    def validate_goal_consistency(cls, v: str, info) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Goal description must be at least 10 characters long")
        return v.strip()

class MealPlanValidator(BaseModel):
    """Validates structure of the meal plan (must include all required meals)."""
    meals: Dict[str, Any] = Field(..., min_items=3)
    total_calories: float = Field(..., gt=0)
    @field_validator('meals')
    @classmethod
    def check_meal_balance(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        required = {"breakfast", "lunch", "dinner"}
        if missing := required - set(v.keys()):
            raise ValueError(f"Missing required meal categories: {missing}")
        return v

def validate_api_payload(payload: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """
    Unified entry-point for validating incoming Gemini API payloads.
    Returns: (bool success, dict details_on_failure)
    """
    try:
        if "goal" in payload:
            UserGoalValidator.model_validate(payload["goal"])
        if "meal_plan" in payload:
            MealPlanValidator.model_validate(payload["meal_plan"])
        return True, {}
    except Exception as e:
        return False, {
            "error": str(e),
            "type": type(e).__name__,
            "fields": getattr(e, "errors", None)
        }
