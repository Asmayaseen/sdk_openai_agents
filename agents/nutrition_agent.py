from typing import AsyncGenerator, Optional
import logging

from .base import BaseAgent
from context import UserSessionContext

logger = logging.getLogger(__name__)

class NutritionAgent(BaseAgent):
    """Specialized nutrition agent for meal planning and dietary guidance."""
    
    def __init__(self):
        system_prompt = """You are a certified nutritionist and dietitian. You provide:

1. Personalized meal planning
2. Nutritional analysis and recommendations
3. Dietary guidance for specific health goals
4. Food substitution suggestions
5. Calorie and macro calculations

Key Guidelines:
- Always consider user's dietary preferences, allergies, and medical conditions
- Provide specific, actionable meal suggestions
- Include nutritional information when relevant
- Suggest appropriate portion sizes
- Consider the user's activity level and goals
- Be mindful of cultural food preferences
- For medical dietary restrictions, recommend consulting a healthcare provider

Focus on creating practical, sustainable eating plans that align with the user's lifestyle and goals."""

        super().__init__(
            name="nutrition",
            description="Specialized nutritionist for meal planning and dietary guidance",
            system_prompt=system_prompt
        )

    async def run(self, message: str, context: UserSessionContext) -> str:
        """Required method from BaseAgent."""
        self.context = context
        response = ""
        async for chunk in self.process_message(message):
            response += chunk
        return response

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process nutrition-related messages."""
        logger.info(f"Nutrition agent processing: {message[:50]}...")
        
        # Build enhanced context for nutrition
        contextual_message = self._build_nutrition_context(message)
        
        # Stream response from OpenAI
        async for chunk in self.get_openai_response(contextual_message):
            yield chunk

    def _build_nutrition_context(self, message: str) -> str:
        """Build nutrition-specific context."""
        base_context = self.build_context_prompt(message)
        
        if not self.context:
            return base_context
        
        nutrition_context = []
        
        # Add BMI if available
        bmi = self.context.calculate_bmi()
        if bmi:
            nutrition_context.append(f"Current BMI: {bmi}")
        
        # Add activity level
        if self.context.activity_level:
            nutrition_context.append(f"Activity Level: {self.context.activity_level}")
        
        # Add current meal plan if exists
        if self.context.meal_plan:
            nutrition_context.append("User has an existing meal plan")
        
        if nutrition_context:
            additional_context = "\n".join(nutrition_context)
            return f"{base_context}\n\n[Nutrition Context]\n{additional_context}"
        
        return base_context

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to another agent."""
        message_lower = message.lower()
        
        # Check for fitness-related keywords
        fitness_keywords = [
            "workout", "exercise", "training", "gym", "fitness",
            "cardio", "strength training", "running"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"
        
        # Check for progress tracking
        progress_keywords = [
            "track weight", "log progress", "record measurement",
            "update stats", "progress tracking"
        ]
        if any(keyword in message_lower for keyword in progress_keywords):
            return "progress"
        
        return None

    def generate_meal_plan_summary(self) -> str:
        """Generate a summary of the current meal plan."""
        if not self.context or not self.context.meal_plan:
            return "No current meal plan available."
        
        # This would be expanded to parse and summarize the meal plan
        return "Current meal plan includes balanced nutrition tailored to your goals."
