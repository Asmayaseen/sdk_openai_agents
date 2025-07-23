# utils/validators.py

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Literal, Optional, Dict, Any
from datetime import time, date  # date ko yahan import kiya

class TimeValidator(BaseModel):
    """
    Strict validation for time inputs using 24-hour format "HH:MM".
    
    Attributes:
        time_str (str): Time in HH:MM format.
    """

    time_str: str = Field(
        ..., 
        pattern=r"^(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$",
        description="Time string in 24-hour format (HH:MM)"
    )

    @field_validator('time_str')
    @classmethod
    def convert_to_time(cls, v: str) -> time:
        """Converts a valid HH:MM string into a datetime.time object."""
        hours, minutes = map(int, v.split(':'))
        return time(hour=hours, minute=minutes)


class WeightValidator(BaseModel):
    """
    Validates weight input and enforces realistic limits.
    
    Attributes:
        value (float): The weight value (0 < value <= 300).
        unit (str): Measurement unit - "kg" or "lbs".
    """

    value: float = Field(..., gt=0, le=300, description="Weight must be between 0 and 300.")
    unit: Literal["kg", "lbs"] = "kg"

    @field_validator('value')
    @classmethod
    def round_weight(cls, v: float) -> float:
        """Rounds weight to 1 decimal place."""
        return round(v, 1)


class ExerciseLevelValidator(BaseModel):
    """
    Standardizes and validates the fitness experience level.
    
    Attributes:
        level (str): One of ["beginner", "intermediate", "advanced"]
    """

    level: Literal["beginner", "intermediate", "advanced"]

    @property
    def numeric_level(self) -> int:
        """Converts level to numeric scale: 0=beginner, 1=intermediate, 2=advanced."""
        return ["beginner", "intermediate", "advanced"].index(self.level)


def validate_user_data(user_data: Dict[str, Any]) -> bool:
    """
    Validates complete user data structure including:
    - Time fields (as HH:MM)
    - Weight structure and units
    - Exercise level string
    - Required keys presence
    
    Args:
        user_data (dict): Dictionary containing user inputs.

    Returns:
        bool: True if all validations pass, otherwise False.
    """
    required_fields = ['age', 'height', 'weight', 'activity_level']

    try:
        # Ensure all required fields exist
        if not all(field in user_data for field in required_fields):
            return False

        # Validate weight
        if isinstance(user_data.get("weight"), dict):
            WeightValidator(**user_data["weight"])

        # Validate exercise level if present
        if "exercise_level" in user_data:
            ExerciseLevelValidator(level=user_data["exercise_level"])

        # Validate time-like strings
        for key, value in user_data.items():
            if isinstance(value, str) and ":" in value:
                TimeValidator(time_str=value)

        return True

    except ValidationError as e:
        print(f"[Validation Error] {e}")
        return False


class UserGoalValidator(BaseModel):
    """
    Validates user wellness goals for logical consistency between 
    description, current weight, and target weight.

    Attributes:
        description (str): Goal description (e.g., "I want to lose weight").
        current_weight (WeightValidator): User's current weight.
        target_weight (WeightValidator): User's goal weight.
        deadline (Optional[date]): Optional deadline for goal.
        preferred_time (Optional[TimeValidator]): Preferred workout/diet time.
    """

    description: str = Field(..., min_length=10, max_length=200)
    current_weight: WeightValidator
    target_weight: WeightValidator
    deadline: Optional[date] = None
    preferred_time: Optional[TimeValidator] = None

    @field_validator('description')
    @classmethod
    def validate_goal_consistency(cls, v: str, info) -> str:
        """Validate goal description consistency."""
        if len(v.strip()) < 10:
            raise ValueError("Goal description must be at least 10 characters long")
        return v.strip()


class MealPlanValidator(BaseModel):
    """
    Validates structure of the meal plan to ensure completeness and positive calorie value.

    Attributes:
        meals (dict): Dictionary of meals (must include breakfast, lunch, dinner).
        total_calories (float): Total calorie count (must be > 0).
    """
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
    Unified entry-point for validating incoming API payloads.

    Args:
        payload (dict): JSON-like input containing 'goal' or 'meal_plan' keys.

    Returns:
        tuple: (status, error_info)
            - status (bool): True if valid, False if any error occurs.
            - error_info (dict): Contains 'error', 'type', and 'fields' (if available).
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
