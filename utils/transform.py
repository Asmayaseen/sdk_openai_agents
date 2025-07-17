from context import GoalType, GoalUnit, DietaryPreference, MedicalCondition

def transform_input(raw_data: dict) -> dict:
    return {
        "user_id": raw_data.get("uid") or raw_data.get("name", "unknown_user"),
        "goal_type": GoalType.WEIGHT_LOSS,
        "goal_target": 5.0,
        "goal_unit": GoalUnit.KG,
        "goal_deadline": "2025-09-15",
        "dietary_preference": DietaryPreference.VEGETARIAN,
        "food_allergies": [],
        "medical_conditions": [MedicalCondition.NONE],
        "workout_plan": None,
        "meal_plan": None,
        "injury_notes": None,
        "handoff_history": [],
        "progress_history": []
    }
