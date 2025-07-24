from context import GoalType, GoalUnit, DietaryPreference, MedicalCondition
from datetime import date

def transform_input(raw_data: dict) -> dict:
    """
    Maps raw input data to the user session dict,
    using enums and providing sane defaults for Gemini agent apps.
    """
    # Helper: Safely parse enum fields (fallback to default if value missing or invalid)
    def parse_enum(value, enum_cls, default):
        try:
            if value is None:
                return default
            if isinstance(value, enum_cls):
                return value
            return enum_cls(value)
        except Exception:
            return default

    # Helper: parse date (YYYY-MM-DD string → date)
    def parse_date(s, default=None):
        if not s:
            return default
        if isinstance(s, date):
            return s
        try:
            return date.fromisoformat(str(s))
        except Exception:
            return default

    # Transform
    return {
        "user_id": str(raw_data.get("uid") or raw_data.get("user_id") or raw_data.get("name") or "unknown_user"),
        "goal_type": parse_enum(raw_data.get("goal_type"), GoalType, GoalType.WEIGHT_LOSS),
        "goal_target": float(raw_data.get("goal_target", 5.0)),
        "goal_unit": parse_enum(raw_data.get("goal_unit"), GoalUnit, GoalUnit.KG),
        "goal_deadline": parse_date(raw_data.get("goal_deadline"), date(2025, 9, 15)),
        "dietary_preference": parse_enum(raw_data.get("dietary_preference"), DietaryPreference, DietaryPreference.VEGETARIAN),
        "food_allergies": raw_data.get("food_allergies", []),
        "medical_conditions": [
            parse_enum(cond, MedicalCondition, MedicalCondition.NONE)
            for cond in raw_data.get("medical_conditions", [MedicalCondition.NONE])
        ],
        "workout_plan": raw_data.get("workout_plan"),
        "meal_plan": raw_data.get("meal_plan"),
        "injury_notes": raw_data.get("injury_notes"),
        "handoff_history": raw_data.get("handoff_history", []),
        "progress_history": raw_data.get("progress_history", []),
    }
