# api/routes.py

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from .schema import (
    GoalSchema,
    MealPlanResponse,
    ProgressUpdateSchema,
    APIErrorResponse
)

router = APIRouter()

# ----------------- DUMMY IN-MEMORY STORAGE -----------------

goals_db: List[GoalSchema] = []
progress_db: List[ProgressUpdateSchema] = []

# ----------------- GOAL ROUTE -----------------

@router.post("/set-goal", response_model=GoalSchema, responses={400: {"model": APIErrorResponse}})
async def set_goal(goal: GoalSchema):
    """
    ✅ Set a new wellness goal.
    ❗ Validates if the deadline is in the future.
    """
    if goal.deadline < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Deadline must be in the future",
            headers={"X-Error": "Invalid deadline"}
        )
    goals_db.append(goal)
    return goal

# ----------------- MEAL PLAN ROUTE -----------------

@router.get("/meal-plan", response_model=MealPlanResponse)
async def get_meal_plan():
    """
    🍽️ Returns a sample meal plan (static for demo).
    📌 Replace this with AI logic or database-driven meals.
    """
    plan = MealPlanResponse(
        days=[
            {"Monday": ["Oatmeal", "Salad", "Grilled Chicken"]},
            {"Tuesday": ["Smoothie", "Tuna Sandwich", "Quinoa Bowl"]}
        ],
        nutritional_info={"calories": 2000, "protein": 120.0, "carbs": 180.0},
        generated_at=datetime.utcnow()
    )
    return plan

# ----------------- PROGRESS ROUTES -----------------

@router.post("/update-progress", response_model=ProgressUpdateSchema)
async def update_progress(data: ProgressUpdateSchema):
    """
    📈 Submit a progress update (e.g., weight, steps).
    """
    progress_db.append(data)
    return data

@router.get("/progress", response_model=List[ProgressUpdateSchema])
async def get_progress():
    """
    📊 Retrieve all submitted progress updates.
    """
    return progress_db