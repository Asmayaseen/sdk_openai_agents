from datetime import date, timedelta
from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import logging
import random

# Local imports
from .base_tool import BaseTool
from ..context import UserSessionContext

logger = logging.getLogger(__name__)

# ----------------------------- ENUMS -----------------------------

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class DietaryPreference(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    OMNIVORE = "omnivore"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"

# ----------------------------- MODELS -----------------------------

class NutritionalInfo(BaseModel):
    calories: int = Field(..., gt=0, description="Calories per serving")
    protein_g: float = Field(..., ge=0, description="Protein in grams")
    carbs_g: float = Field(..., ge=0, description="Carbohydrates in grams")
    fats_g: float = Field(..., ge=0, description="Fats in grams")
    fiber_g: Optional[float] = Field(None, ge=0, description="Fiber in grams")
    sugar_g: Optional[float] = Field(None, ge=0, description="Sugar in grams")

class MealItem(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=300)
    ingredients: List[str] = Field(..., min_items=1)
    instructions: List[str] = Field(..., min_items=1)
    nutrition: NutritionalInfo
    prep_time_min: int = Field(..., gt=0, le=120)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: List[str] = Field(default_factory=list)

class MealPlanInput(BaseModel):
    dietary_preference: DietaryPreference
    calorie_target: int = Field(..., ge=1200, le=4000)
    restrictions: List[str] = Field(default_factory=list)
    days: int = Field(7, ge=1, le=14)
    meal_types: List[MealType] = Field(
        default_factory=lambda: [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
    )
    start_date: Optional[date] = Field(
        None,
        description="Optional start date (defaults to today)"
    )

    @field_validator('restrictions')
    def validate_restrictions(cls, v: List[str]) -> List[str]:
        valid_restrictions = ["nut-free", "shellfish-free", "soy-free", "egg-free"]
        invalid = [r for r in v if r not in valid_restrictions]
        if invalid:
            raise ValueError(f"Invalid restriction(s): {invalid}. Allowed: {valid_restrictions}")
        return v

class MealPlanOutput(BaseModel):
    start_date: date = Field(..., description="Plan start date")
    end_date: date = Field(..., description="Plan end date")
    daily_plans: Dict[date, Dict[MealType, MealItem]] = Field(...)
    nutrition_summary: Dict[str, NutritionalInfo] = Field(...)
    shopping_list: Dict[str, List[str]] = Field(...)
    preparation_tips: Dict[date, str] = Field(...)

# ----------------------------- TOOL CLASS -----------------------------

class MealPlannerTool(BaseTool):
    """
    Meal Planner Tool

    - Generates meal plans based on dietary preferences
    - Calculates nutritional summary
    - Creates shopping list and preparation tips
    """

    @classmethod
    def name(cls) -> str:
        return "meal_planner"

    @classmethod
    def description(cls) -> str:
        return "Creates personalized meal plans with nutrition analysis and shopping lists"

    @classmethod
    def input_schema(cls) -> type[BaseModel]:
        return MealPlanInput

    @classmethod
    def output_schema(cls) -> type[BaseModel]:
        return MealPlanOutput

    async def execute(self, input_data: Dict[str, Any], context: Optional[UserSessionContext] = None) -> Dict[str, Any]:
        logger.info(
            f"Generating {input_data['days']}-day {input_data['dietary_preference']} meal plan"
        )

        meals = self._get_filtered_meals(
            input_data['dietary_preference'],
            input_data['restrictions']
        )

        plan = self._generate_plan(
            meals,
            input_data['days'],
            input_data['meal_types'],
            input_data['calorie_target'],
            input_data.get('start_date') or date.today()
        )

        if context:
            self._update_context(context, input_data, plan)

        return plan

    # -------------------- Internal Methods --------------------

    def _get_filtered_meals(self, diet: DietaryPreference, restrictions: List[str]) -> Dict[MealType, List[MealItem]]:
        all_meals = self._get_sample_meals()
        return {
            meal_type: [
                meal for meal in meals
                if self._meal_matches_requirements(meal, diet, restrictions)
            ]
            for meal_type, meals in all_meals.items()
        }

    def _generate_plan(
        self,
        meals: Dict[MealType, List[MealItem]],
        days: int,
        meal_types: List[MealType],
        calorie_target: int,
        start_date: date
    ) -> Dict[str, Any]:
        end_date = start_date + timedelta(days=days - 1)
        daily_plans = {}
        current_date = start_date

        for _ in range(days):
            daily_plans[current_date] = {
                meal_type: random.choice(meals[meal_type])
                for meal_type in meal_types
                if meals.get(meal_type)
            }
            current_date += timedelta(days=1)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "daily_plans": daily_plans,
            "nutrition_summary": self._calculate_nutrition(daily_plans, calorie_target),
            "shopping_list": self._generate_shopping_list(daily_plans),
            "preparation_tips": self._generate_prep_tips(daily_plans)
        }

    def _meal_matches_requirements(self, meal: MealItem, diet: DietaryPreference, restrictions: List[str]) -> bool:
        # TODO: Implement dietary & restriction filter logic
        return True

    def _calculate_nutrition(self, daily_plans: Dict[date, Dict[MealType, MealItem]], target: int) -> Dict[str, NutritionalInfo]:
        # TODO: Implement real nutritional summary
        return {
            "daily_average": NutritionalInfo(
                calories=target,
                protein_g=round(target * 0.3 / 4),
                carbs_g=round(target * 0.5 / 4),
                fats_g=round(target * 0.2 / 9)
            )
        }

    def _generate_shopping_list(self, daily_plans: Dict[date, Dict[MealType, MealItem]]) -> Dict[str, List[str]]:
        # TODO: Combine ingredients by category
        return {
            "produce": ["Sample vegetables", "Fruits"],
            "pantry": ["Oats", "Rice"],
            "protein": ["Tofu", "Chicken"],
        }

    def _generate_prep_tips(self, daily_plans: Dict[date, Dict[MealType, MealItem]]) -> Dict[date, str]:
        return {
            day: f"Prep ingredients for {len(meals)} meal(s) in advance."
            for day, meals in daily_plans.items()
        }

    def _update_context(self, context: UserSessionContext, input_data: Dict[str, Any], plan: Dict[str, Any]):
        context.dietary_preferences = input_data['dietary_preference'].value
        context.meal_plan = {
            "period": f"{plan['start_date']} to {plan['end_date']}",
            "details": plan
        }
        context.update_progress(
            "Generated new meal plan",
            metric="calories",
            value=input_data['calorie_target']
        )
