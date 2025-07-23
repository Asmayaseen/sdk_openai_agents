from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from context import UserSessionContext, DietaryPreference

logger = logging.getLogger(__name__)

class Meal(BaseModel):
    """Individual meal with nutritional information."""
    name: str = Field(..., description="Name of the meal")
    description: str = Field(..., description="Meal description")
    calories: int = Field(..., description="Estimated calories")
    protein: float = Field(..., description="Protein content in grams")
    carbs: float = Field(..., description="Carbohydrate content in grams")
    fat: float = Field(..., description="Fat content in grams")
    prep_time: int = Field(..., description="Preparation time in minutes")
    ingredients: List[str] = Field(..., description="List of ingredients")

class DayMealPlan(BaseModel):
    """Complete meal plan for one day."""
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    snacks: List[Meal] = Field(default_factory=list)
    total_calories: int = Field(..., description="Total daily calories")
    total_protein: float = Field(..., description="Total daily protein")
    total_carbs: float = Field(..., description="Total daily carbs")
    total_fat: float = Field(..., description="Total daily fat")

class MealDatabase:
    """Database of meal options organized by dietary preference."""
    
    VEGETARIAN_MEALS = {
        "breakfast": [
            Meal(
                name="Oatmeal with Berries",
                description="Steel-cut oats topped with fresh berries and nuts",
                calories=320,
                protein=12.0,
                carbs=58.0,
                fat=8.0,
                prep_time=15,
                ingredients=["steel-cut oats", "blueberries", "almonds", "honey", "milk"]
            ),
            Meal(
                name="Greek Yogurt Parfait",
                description="Greek yogurt layered with granola and fresh fruit",
                calories=280,
                protein=20.0,
                carbs=35.0,
                fat=6.0,
                prep_time=5,
                ingredients=["Greek yogurt", "granola", "strawberries", "banana", "honey"]
            ),
            Meal(
                name="Avocado Toast",
                description="Whole grain toast topped with mashed avocado and eggs",
                calories=350,
                protein=16.0,
                carbs=28.0,
                fat=22.0,
                prep_time=10,
                ingredients=["whole grain bread", "avocado", "eggs", "tomato", "salt", "pepper"]
            )
        ],
        "lunch": [
            Meal(
                name="Quinoa Buddha Bowl",
                description="Quinoa with roasted vegetables and tahini dressing",
                calories=420,
                protein=15.0,
                carbs=62.0,
                fat=14.0,
                prep_time=25,
                ingredients=["quinoa", "sweet potato", "broccoli", "chickpeas", "tahini", "lemon"]
            ),
            Meal(
                name="Caprese Salad with Bread",
                description="Fresh mozzarella, tomatoes, and basil with crusty bread",
                calories=380,
                protein=18.0,
                carbs=32.0,
                fat=22.0,
                prep_time=10,
                ingredients=["mozzarella", "tomatoes", "basil", "balsamic", "olive oil", "bread"]
            ),
            Meal(
                name="Lentil Soup",
                description="Hearty lentil soup with vegetables and herbs",
                calories=320,
                protein=18.0,
                carbs=52.0,
                fat=4.0,
                prep_time=30,
                ingredients=["lentils", "carrots", "celery", "onion", "garlic", "vegetable broth"]
            )
        ],
        "dinner": [
            Meal(
                name="Eggplant Parmesan",
                description="Baked eggplant with marinara sauce and cheese",
                calories=450,
                protein=22.0,
                carbs=35.0,
                fat=26.0,
                prep_time=45,
                ingredients=["eggplant", "marinara sauce", "mozzarella", "parmesan", "breadcrumbs"]
            ),
            Meal(
                name="Vegetable Stir-fry with Tofu",
                description="Mixed vegetables and tofu in savory sauce over rice",
                calories=380,
                protein=20.0,
                carbs=48.0,
                fat=12.0,
                prep_time=20,
                ingredients=["tofu", "bell peppers", "broccoli", "carrots", "soy sauce", "brown rice"]
            ),
            Meal(
                name="Black Bean Quesadillas",
                description="Whole wheat tortillas filled with black beans and cheese",
                calories=420,
                protein=18.0,
                carbs=55.0,
                fat=16.0,
                prep_time=15,
                ingredients=["black beans", "whole wheat tortillas", "cheese", "peppers", "onions"]
            )
        ]
    }
    
    VEGAN_MEALS = {
        "breakfast": [
            Meal(
                name="Chia Pudding",
                description="Chia seeds soaked in almond milk with fruit",
                calories=280,
                protein=8.0,
                carbs=32.0,
                fat=14.0,
                prep_time=5,
                ingredients=["chia seeds", "almond milk", "berries", "maple syrup", "vanilla"]
            ),
            Meal(
                name="Smoothie Bowl",
                description="Thick fruit smoothie topped with nuts and seeds",
                calories=320,
                protein=10.0,
                carbs=48.0,
                fat=12.0,
                prep_time=10,
                ingredients=["banana", "spinach", "almond milk", "granola", "hemp seeds"]
            )
        ],
        "lunch": [
            Meal(
                name="Hummus and Veggie Wrap",
                description="Whole wheat wrap with hummus and fresh vegetables",
                calories=350,
                protein=12.0,
                carbs=52.0,
                fat=12.0,
                prep_time=10,
                ingredients=["whole wheat tortilla", "hummus", "cucumber", "tomato", "lettuce"]
            )
        ],
        "dinner": [
            Meal(
                name="Lentil Curry",
                description="Spiced lentil curry with coconut milk over rice",
                calories=400,
                protein=16.0,
                carbs=64.0,
                fat=10.0,
                prep_time=30,
                ingredients=["red lentils", "coconut milk", "curry spices", "tomatoes", "rice"]
            )
        ]
    }
    
    GENERAL_MEALS = {
        "breakfast": [
            Meal(
                name="Scrambled Eggs with Toast",
                description="Fluffy scrambled eggs with whole grain toast",
                calories=340,
                protein=22.0,
                carbs=28.0,
                fat=16.0,
                prep_time=10,
                ingredients=["eggs", "whole grain bread", "butter", "milk", "herbs"]
            )
        ],
        "lunch": [
            Meal(
                name="Grilled Chicken Salad",
                description="Mixed greens with grilled chicken and vinaigrette",
                calories=380,
                protein=32.0,
                carbs=18.0,
                fat=20.0,
                prep_time=15,
                ingredients=["chicken breast", "mixed greens", "tomatoes", "cucumber", "olive oil"]
            )
        ],
        "dinner": [
            Meal(
                name="Baked Salmon with Vegetables",
                description="Herb-crusted salmon with roasted seasonal vegetables",
                calories=420,
                protein=35.0,
                carbs=25.0,
                fat=22.0,
                prep_time=30,
                ingredients=["salmon fillet", "broccoli", "sweet potato", "olive oil", "herbs"]
            )
        ]
    }
    
    @classmethod
    def get_meals_by_preference(cls, preference: DietaryPreference) -> Dict[str, List[Meal]]:
        """Get meals based on dietary preference."""
        if preference == DietaryPreference.VEGETARIAN:
            return cls.VEGETARIAN_MEALS
        elif preference == DietaryPreference.VEGAN:
            return cls.VEGAN_MEALS
        else:
            return cls.GENERAL_MEALS

class MealPlannerTool:
    """Tool for generating personalized meal plans."""
    
    @classmethod
    def name(cls) -> str:
        return "meal_planner"
    
    @classmethod
    def description(cls) -> str:
        return "Generates personalized meal plans based on dietary preferences and nutritional goals"
    
    class InputModel(BaseModel):
        days: int = Field(default=7, description="Number of days to plan for")
        daily_calories: Optional[int] = Field(None, description="Target daily calories")
        dietary_preference: DietaryPreference = Field(
            default=DietaryPreference.NO_PREFERENCE,
            description="Dietary preference"
        )
        allergies: List[str] = Field(default_factory=list, description="Food allergies to avoid")
    
    class OutputModel(BaseModel):
        success: bool = Field(..., description="Whether meal plan generation was successful")
        message: str = Field(..., description="Status message")
        meal_plan: Optional[Dict[str, Any]] = Field(None, description="Generated meal plan")
    
    async def execute(
        self,
        days: int = 7,
        daily_calories: Optional[int] = None,
        dietary_preference: DietaryPreference = DietaryPreference.NO_PREFERENCE,
        allergies: List[str] = None,
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized meal plan.
        
        Args:
            days: Number of days to plan for
            daily_calories: Target daily calories
            dietary_preference: Dietary preference
            allergies: List of food allergies
            context: User session context
            
        Returns:
            Dict with success status, message, and meal plan
        """
        logger.info(f"Generating {days}-day meal plan for {dietary_preference.value}")
        
        try:
            if allergies is None:
                allergies = []
            
            # Get meals based on dietary preference
            available_meals = MealDatabase.get_meals_by_preference(dietary_preference)
            
            # Filter out meals with allergens
            if allergies and context and context.food_allergies:
                allergies.extend(context.food_allergies)
            
            if allergies:
                available_meals = self._filter_allergens(available_meals, allergies)
            
            # Generate meal plan
            meal_plan = {}
            for day in range(1, days + 1):
                day_name = f"Day {day}"
                day_plan = self._generate_day_plan(available_meals, daily_calories)
                meal_plan[day_name] = day_plan.model_dump()
            
            # Update context if provided
            if context:
                context.meal_plan = meal_plan
                context.update_progress(
                    "Generated meal plan",
                    metric="meal_plans",
                    value=days
                )
            
            return {
                "success": True,
                "message": f"Generated {days}-day meal plan for {dietary_preference.value} diet",
                "meal_plan": meal_plan
            }
            
        except Exception as e:
            logger.error(f"Meal plan generation failed: {str(e)}")
            return {
                "success": False,
                "message": f"Meal plan generation failed: {str(e)}",
                "meal_plan": None
            }
    
    def _filter_allergens(self, meals: Dict[str, List[Meal]], allergies: List[str]) -> Dict[str, List[Meal]]:
        """Filter out meals containing allergens."""
        filtered_meals = {}
        
        for meal_type, meal_list in meals.items():
            filtered_list = []
            for meal in meal_list:
                # Check if any allergen is in the ingredients
                has_allergen = any(
                    allergen.lower() in ingredient.lower()
                    for allergen in allergies
                    for ingredient in meal.ingredients
                )
                if not has_allergen:
                    filtered_list.append(meal)
            
            filtered_meals[meal_type] = filtered_list
        
        return filtered_meals
    
    def _generate_day_plan(self, available_meals: Dict[str, List[Meal]], target_calories: Optional[int] = None) -> DayMealPlan:
        """Generate a single day's meal plan."""
        import random
        
        # Select random meals for each meal type
        breakfast = random.choice(available_meals.get("breakfast", []))
        lunch = random.choice(available_meals.get("lunch", []))
        dinner = random.choice(available_meals.get("dinner", []))
        
        # Calculate totals
        total_calories = breakfast.calories + lunch.calories + dinner.calories
        total_protein = breakfast.protein + lunch.protein + dinner.protein
        total_carbs = breakfast.carbs + lunch.carbs + dinner.carbs
        total_fat = breakfast.fat + lunch.fat + dinner.fat
        
        # Add snacks if we need more calories
        snacks = []
        if target_calories and total_calories < target_calories:
            # Simple snack to reach target
            calorie_gap = target_calories - total_calories
            if calorie_gap > 100:
                snack = Meal(
                    name="Mixed Nuts",
                    description="A handful of mixed nuts",
                    calories=min(calorie_gap, 200),
                    protein=6.0,
                    carbs=8.0,
                    fat=14.0,
                    prep_time=1,
                    ingredients=["almonds", "walnuts", "cashews"]
                )
                snacks.append(snack)
                total_calories += snack.calories
                total_protein += snack.protein
                total_carbs += snack.carbs
                total_fat += snack.fat
        
        return DayMealPlan(
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snacks=snacks,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat
        )
