from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class WellnessAgent(BaseAgent):
    """Primary wellness coaching agent for general health guidance."""

    def __init__(self):
        system_prompt = (
            "You are a certified wellness coach and health advisor. You provide:\n"
            "\n"
            "1. General health and wellness guidance\n"
            "2. Lifestyle recommendations\n"
            "3. Motivation and goal-setting support\n"
            "4. Holistic health approaches\n"
            "\n"
            "Key Guidelines:\n"
            "- Always prioritize user safety and recommend consulting healthcare professionals for medical issues\n"
            "- Provide evidence-based advice when possible\n"
            "- Be encouraging and supportive\n"
            "- Consider the user's complete health context\n"
            "- Make personalized recommendations based on their goals and preferences\n"
            "- If asked about specific nutrition or workout plans, suggest consulting the nutrition or fitness specialists\n"
            "\n"
            "Remember: You are not a medical doctor. Always recommend consulting healthcare professionals for medical concerns."
        )

        super().__init__(
            name="wellness",
            description="Primary wellness coach for general health guidance and motivation",
            system_prompt=system_prompt
        )

    async def process_message(
        self,
        message: str,
        *args,  # To absorb any unexpected positional args
        **kwargs  # To absorb any unexpected keyword args like context/session
    ) -> AsyncGenerator[str, None]:
        """Process wellness-related messages."""
        logger.info(f"Wellness agent processing: {message[:50]}...")
        contextual_message = self.build_context_prompt(message)
        async for chunk in self.get_gemini_response(contextual_message):
            yield chunk

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to specialist agent."""
        message_lower = message.lower()

        # Nutrition related keywords
        nutrition_keywords = [
            "meal plan", "diet", "nutrition", "calories", "food", "recipe",
            "eat", "eating", "macros", "protein", "carbs", "fat"
        ]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"

        # Fitness related keywords
        fitness_keywords = [
            "workout", "exercise", "training", "gym", "fitness", "strength",
            "cardio", "running", "lifting", "weights", "routine"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"

        # Progress tracking keywords
        progress_keywords = [
            "track", "progress", "weight", "measurement", "record", "log",
            "update", "metric", "goal progress"
        ]
        if any(keyword in message_lower for keyword in progress_keywords):
            return "progress"

        return None

    def get_welcome_message(self) -> str:
        """Get personalized welcome message."""
        if not hasattr(self, "context") or not self.context:
            return "Hello! I'm your wellness coach. How can I help you today?"

        name = getattr(self.context, "name", None)
        goal = (
            self.context.goal_type.value.replace("_", " ").title()
            if getattr(self.context, "goal_type", None)
            else "general wellness"
        )
        return (
            f"Hello {name}! 🌟\n\n"
            f"I'm your personal wellness coach, here to support you on your {goal} journey.\n\n"
            "I can help you with:\n"
            "• General health and wellness guidance\n"
            "• Lifestyle recommendations\n"
            "• Goal setting and motivation\n"
            "• Connecting you with our nutrition and fitness specialists\n\n"
            "What would you like to focus on today?"
        )
