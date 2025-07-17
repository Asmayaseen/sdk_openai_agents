import logging
from datetime import datetime
from typing import Optional, Dict, Any

from .base_agent import BaseAgent
from openai import Assistant
from ..context import UserSessionContext
from ..tools.goal_analyzer import GoalAnalyzerTool
from ..tools.meal_planner import MealPlannerTool
from ..tools.workout_recommender import WorkoutRecommenderTool

logger = logging.getLogger(__name__)

class WellnessAgent(BaseAgent):
    """
    Main health and wellness planning agent that coordinates:
    - Goal analysis
    - Meal planning
    - Workout recommendations
    """
    
    def __init__(self):
        super().__init__(
            name="WellnessAgent",
            description="Primary agent for health and wellness planning",
            tools=[
                GoalAnalyzerTool(),
                MealPlannerTool(),
                WorkoutRecommenderTool()
            ]
        )

    async def on_handoff(self, context: UserSessionContext) -> Optional[str]:
        """
        Determine if a handoff to a specialized agent is needed
        
        Args:
            context: Current user session context
            
        Returns:
            str: Name of agent to handoff to, or None
        """
        if context.injury_notes:
            return "InjurySupportAgent"
        elif context.diet_preferences and any(
            term in context.diet_preferences.lower() 
            for term in ["diabet", "allerg", "celiac"]
        ):
            return "NutritionExpertAgent"
        return None

    @Assistant.tool
    async def generate_wellness_plan(
        self,
        user_input: str,
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive wellness plan based on user input
        
        Args:
            user_input: User's health goals/requirements
            context: Current session context
            
        Returns:
            Dictionary containing:
            - goal_analysis: Parsed health goals
            - meal_plan: Generated meal suggestions
            - workout_plan: Exercise recommendations
            - timestamp: When plan was generated
        """
        try:
            if not context:
                context = UserSessionContext()
            
            # Step 1: Analyze goals
            goal_result = await GoalAnalyzerTool().run(
                {"goal_text": user_input},
                context
            )
            if not goal_result or not goal_result.output:
                raise ValueError("Goal analysis failed.")

            # Step 2: Create meal plan
            meal_result = await MealPlannerTool().run(
                {
                    "diet_preferences": context.diet_preferences or "",
                    "calorie_target": self._calculate_calorie_target(goal_result.output)
                },
                context
            )
            if not meal_result or not meal_result.output:
                raise ValueError("Meal planning failed.")

            # Step 3: Generate workouts
            workout_result = await WorkoutRecommenderTool().run(
                {
                    "fitness_level": context.fitness_level or "beginner",
                    "goal_type": goal_result.output.get("goal_type", "general")
                },
                context
            )
            if not workout_result or not workout_result.output:
                raise ValueError("Workout recommendation failed.")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "goal_analysis": goal_result.output,
                "meal_plan": meal_result.output,
                "workout_plan": workout_result.output
            }

        except Exception as e:
            logger.exception("Error generating wellness plan")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _calculate_calorie_target(self, goal_data: Dict[str, Any]) -> int:
        """
        Calculate daily calorie target based on goal type.
        
        Args:
            goal_data: Dictionary containing goal information
            
        Returns:
            int: Estimated daily calorie target
        """
        base_calories = 2000
        goal_type = goal_data.get("goal_type", "maintain")

        if goal_type == "lose":
            return base_calories - 300
        elif goal_type == "gain":
            return base_calories + 300
        return base_calories
