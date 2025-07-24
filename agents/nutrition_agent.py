from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class NutritionAgent(BaseAgent):
    """Specialized nutrition agent for meal planning and dietary guidance."""

    def __init__(self):
        system_prompt = (
            "You are a certified nutritionist and dietitian. You provide:\n"
            "1. Personalized meal planning\n"
            "2. Nutritional analysis and recommendations\n"
            "3. Dietary guidance for specific health goals\n"
            "4. Food substitution suggestions\n"
            "5. Calorie and macro calculations\n\n"
            "Key Guidelines:\n"
            "- Always consider user's dietary preferences, allergies, and medical conditions\n"
            "- Provide specific, actionable meal suggestions\n"
            "- Include nutritional information when relevant\n"
            "- Suggest appropriate portion sizes\n"
            "- Consider the user's activity level and goals\n"
            "- Be mindful of cultural food preferences\n"
            "- For medical dietary restrictions, recommend consulting a healthcare provider\n\n"
            "Focus on creating practical, sustainable eating plans that align with the user's lifestyle and goals."
        )
        super().__init__(
            name="nutrition",
            description="Specialized nutritionist for meal planning and dietary guidance",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process nutrition-related messages, streaming Gemini output."""
        logger.info(f"Nutrition agent processing: {message[:50]}...")

        contextual_message = self._build_nutrition_context(message)

        async for chunk in self.get_gemini_response(contextual_message):
            yield chunk

    def _build_nutrition_context(self, message: str) -> str:
        """
        Builds added context string with user BMI, activity, current meals.
        Returns prompt for Gemini.
        """
        base_context = self.build_context_prompt(message)

        if not self.context:
            return base_context

        nutrition_context = []

        # BMI if present
        bmi = None
        if hasattr(self.context, "calculate_bmi"):
            bmi = self.context.calculate_bmi()
        if bmi:
            nutrition_context.append(f"Current BMI: {bmi}")

        # Activity level
        if getattr(self.context, "activity_level", None):
            nutrition_context.append(f"Activity Level: {self.context.activity_level}")

        # Current meal plan
        if getattr(self.context, "meal_plan", None):
            if self.context.meal_plan:
                nutrition_context.append("User has an existing meal plan")

        if nutrition_context:
            additional_context = "\n".join(nutrition_context)
            return f"{base_context}\n\n[Nutrition Context]\n{additional_context}"

        return base_context

    async def should_handoff(self, message: str) -> Optional[str]:
        """
        Determines if message should be handed off to fitness or progress agent.
        Returns agent string to hand off to, or None.
        """
        message_lower = message.lower()

        # Fitness keywords
        fitness_keywords = [
            "workout", "exercise", "training", "gym", "fitness",
            "cardio", "strength training", "running"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            logger.info("NutritionAgent: Handing off to fitness agent for activity-related query.")
            return "fitness"

        # Progress tracking
        progress_keywords = [
            "track weight", "log progress", "record measurement",
            "update stats", "progress tracking"
        ]
        if any(keyword in message_lower for keyword in progress_keywords):
            logger.info("NutritionAgent: Handing off to progress agent for progress query.")
            return "progress"

        return None

    def generate_meal_plan_summary(self) -> str:
        """Generates a human-friendly summary of the current meal plan in the agent context."""
        if not self.context or not getattr(self.context, "meal_plan", None):
            return "No current meal plan available."

        # Would normally summarize the plan in detail
        return "Current meal plan includes balanced nutrition tailored to your goals."


