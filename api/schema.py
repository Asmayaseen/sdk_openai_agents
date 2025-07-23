# api/schema.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# ------------------ GOAL SCHEMA ------------------

class GoalSchema(BaseModel):
    description: str
    target_value: float
    unit: str
    deadline: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "description": "Lose weight",
                "target_value": 5.0,
                "unit": "kg",
                "deadline": "2025-08-15T00:00:00"
            }
        }

# ------------------ MEAL PLAN RESPONSE ------------------

class MealPlanResponse(BaseModel):
    days: List[Dict[str, List[str]]] = Field(..., min_items=1)
    nutritional_info: Dict[str, float]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "days": [
                    {"Monday": ["Oatmeal", "Grilled Chicken Salad", "Fish & Veggies"]},
                    {"Tuesday": ["Smoothie", "Turkey Wrap", "Stir Fry"]}
                ],
                "nutritional_info": {
                    "calories": 1800,
                    "protein": 120.0,
                    "carbs": 150.0
                },
                "generated_at": "2025-07-12T15:30:00"
            }
        }

# ------------------ PROGRESS SCHEMA ------------------

class ProgressUpdateSchema(BaseModel):
    metric: str
    value: float
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "metric": "weight",
                "value": 62.5,
                "notes": "Feeling great!",
                "timestamp": "2025-07-12T12:00:00"
            }
        }

# ------------------ API ERROR RESPONSE ------------------

class APIErrorResponse(BaseModel):
    detail: str
    error_code: int
    suggestions: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid goal input",
                "error_code": 400,
                "suggestions": [
                    "Check unit format",
                    "Ensure target_value is numeric"
                ]
            }
        }