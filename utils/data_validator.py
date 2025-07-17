from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import Optional, Dict, Any, Tuple
from .validators import TimeValidator, WeightValidator

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

    @model_validator(mode='after')
    def validate_goal_consistency(self) -> 'UserGoalValidator':
        desc = self.description.lower()
        current = self.current_weight.value
        target = self.target_weight.value

        if "lose" in desc and target >= current:
            raise ValueError("Target weight must be less than current weight for weight loss goals.")
        if "gain" in desc and target <= current:
            raise ValueError("Target weight must be greater than current weight for weight gain goals.")
        return self


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


def validate_api_payload(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
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
