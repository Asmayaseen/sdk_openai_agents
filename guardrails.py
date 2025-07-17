from pydantic import BaseModel,field_validator
from typing import Optional, Dict, List, Union
import re
from enum import Enum

class GoalMetrics(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_BUILDING = "muscle_building"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"

class DietaryPreferences(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    OMNIVORE = "omnivore"

class InjuryType(str, Enum):
    KNEE = "knee"
    BACK = "back"
    SHOULDER = "shoulder"
    WRIST = "wrist"
    ANKLE = "ankle"
    NONE = "none"

class HealthCondition(str, Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    CHOLESTEROL = "cholesterol"
    NONE = "none"

class StructuredGoal(BaseModel):
    """Validated goal structure"""
    goal_type: GoalMetrics
    target_value: float
    unit: str
    timeframe_weeks: int
    experience_level: str = "beginner"
    
    @field_validator('target_value')
    def validate_target_value(cls, v):
        if v <= 0:
            raise ValueError("Target value must be positive")
        if v > 1000:  # arbitrary large number
            raise ValueError("Target value is unrealistically high")
        return v
    
    @field_validator('timeframe_weeks')
    def validate_timeframe(cls, v):
        if v < 1:
            raise ValueError("Timeframe must be at least 1 week")
        if v > 52:
            raise ValueError("Timeframe cannot exceed 1 year")
        return v

class InputGuardrails:
    """Validates and sanitizes user input"""
    
    @staticmethod
    def validate_goal_input(user_input: str) -> Optional[StructuredGoal]:
        """Extracts and validates goal from natural language input"""
        try:
            # Example pattern: "lose 5 kg in 2 months"
            pattern = r"(lose|gain|build)\s+(\d+\.?\d*)\s*(kg|lb|pounds?|kilos?)\s*(?:in|within|over)\s*(\d+)\s*(weeks?|months?|years?)"
            match = re.search(pattern, user_input.lower())
            
            if not match:
                raise ValueError("Could not parse goal from input")
            
            action, value, unit, duration, time_unit = match.groups()
            
            # Convert to structured format
            goal_map = {
                "lose": GoalMetrics.WEIGHT_LOSS,
                "gain": GoalMetrics.WEIGHT_GAIN,
                "build": GoalMetrics.MUSCLE_BUILDING
            }
            
            # Convert time to weeks
            time_multiplier = 1
            if time_unit.startswith("month"):
                time_multiplier = 4
            elif time_unit.startswith("year"):
                time_multiplier = 52
                
            timeframe_weeks = int(duration) * time_multiplier
            
            # Standardize units
            if unit in ["lb", "pound", "pounds"]:
                unit = "lb"
            else:
                unit = "kg"
            
            return StructuredGoal(
                goal_type=goal_map[action],
                target_value=float(value),
                unit=unit,
                timeframe_weeks=timeframe_weeks
            )
            
        except Exception as e:
            raise ValueError(f"Invalid goal format: {str(e)}")
    
    @staticmethod
    def validate_dietary_preference(input: str) -> DietaryPreferences:
        """Validates dietary preference input"""
        input = input.lower().strip()
        for pref in DietaryPreferences:
            if pref.value in input:
                return pref
        raise ValueError("Unsupported dietary preference")
    
    @staticmethod
    def validate_injury_info(input: str) -> InjuryType:
        """Validates injury information"""
        input = input.lower().strip()
        for injury in InjuryType:
            if injury.value in input and injury != InjuryType.NONE:
                return injury
        return InjuryType.NONE
    
    @staticmethod
    def validate_health_condition(input: str) -> HealthCondition:
        """Validates health conditions"""
        input = input.lower().strip()
        for condition in HealthCondition:
            if condition.value in input and condition != HealthCondition.NONE:
                return condition
        return HealthCondition.NONE

class OutputGuardrails:
    """Validates and structures tool outputs"""
    
    @staticmethod
    def validate_meal_plan_output(plan: Union[Dict, List]) -> Dict:
        """Validates meal plan output structure"""
        if isinstance(plan, list):
            if len(plan) != 7:
                raise ValueError("Meal plan must cover 7 days")
            return {"days": plan}
        
        if not isinstance(plan, dict) or "days" not in plan:
            raise ValueError("Meal plan must have 'days' key")
        
        if len(plan["days"]) != 7:
            raise ValueError("Meal plan must cover 7 days")
            
        return plan
    
    @staticmethod
    def validate_workout_plan_output(plan: Dict) -> Dict:
        """Validates workout plan output structure"""
        required_keys = {"days", "exercises", "duration_min", "intensity"}
        if not all(key in plan for key in required_keys):
            raise ValueError(f"Workout plan missing required keys: {required_keys}")
        
        if len(plan["days"]) not in [3, 4, 5, 7]:
            raise ValueError("Workout plan must cover 3, 4, 5, or 7 days")
            
        return plan
    
    @staticmethod
    def validate_progress_update(update: Dict) -> Dict:
        """Validates progress tracking update"""
        required_keys = {"metric", "value", "date", "notes"}
        if not all(key in update for key in required_keys):
            raise ValueError(f"Progress update missing required keys: {required_keys}")
        return update

class GuardrailError(Exception):
    """Custom exception for guardrail violations"""
    pass

def apply_input_guardrails(input: str, guardrail_type: str) -> Union[StructuredGoal, DietaryPreferences, InjuryType, HealthCondition]:
    """Applies the appropriate input guardrail based on type"""
    try:
        if guardrail_type == "goal":
            return InputGuardrails.validate_goal_input(input)
        elif guardrail_type == "diet":
            return InputGuardrails.validate_dietary_preference(input)
        elif guardrail_type == "injury":
            return InputGuardrails.validate_injury_info(input)
        elif guardrail_type == "health":
            return InputGuardrails.validate_health_condition(input)
        else:
            raise ValueError(f"Unknown guardrail type: {guardrail_type}")
    except ValueError as e:
        raise GuardrailError(str(e))

def apply_output_guardrails(output: Union[Dict, List], output_type: str) -> Dict:
    """Applies the appropriate output guardrail based on type"""
    try:
        if output_type == "meal_plan":
            return OutputGuardrails.validate_meal_plan_output(output)
        elif output_type == "workout_plan":
            return OutputGuardrails.validate_workout_plan_output(output)
        elif output_type == "progress_update":
            return OutputGuardrails.validate_progress_update(output)
        else:
            raise ValueError(f"Unknown output guardrail type: {output_type}")
    except ValueError as e:
        raise GuardrailError(str(e))