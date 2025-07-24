from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class FitnessAgent(BaseAgent):
    """Specialized fitness agent for workout planning and exercise guidance."""

    def __init__(self):
        system_prompt = (
            "You are a certified personal trainer and exercise physiologist. You provide:\n"
            "1. Personalized workout plans\n"
            "2. Exercise form and technique guidance\n"
            "3. Fitness program progression\n"
            "4. Injury prevention strategies\n"
            "5. Recovery and rest recommendations\n\n"
            "Key Guidelines:\n"
            "- Always prioritize safety and proper form\n"
            "- Consider user's fitness level, injuries, and limitations\n"
            "- Provide clear, step-by-step exercise instructions\n"
            "- Include warm-up and cool-down recommendations\n"
            "- Adapt exercises for different equipment availability\n"
            "- Progress workouts gradually to prevent injury\n"
            "- For serious injuries or health conditions, recommend consulting healthcare professionals\n\n"
            "Focus on creating sustainable, effective fitness routines that match the user's goals and capabilities."
        )
        super().__init__(
            name="fitness",
            description="Specialized personal trainer for workout planning and exercise guidance",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process fitness-related messages."""
        logger.info(f"Fitness agent processing: {message[:50]}...")

        contextual_message = self._build_fitness_context(message)

        async for chunk in self.get_gemini_response(contextual_message):
            yield chunk

    def _build_fitness_context(self, message: str) -> str:
        """Builds fitness-specific context for the model prompt."""
        base_context = self.build_context_prompt(message)

        if not self.context:
            return base_context

        fitness_context = []

        if getattr(self.context, "activity_level", None):
            fitness_context.append(f"Current Activity Level: {self.context.activity_level}")

        if getattr(self.context, "injury_notes", None):
            fitness_context.append(f"Injury Considerations: {self.context.injury_notes}")

        if getattr(self.context, "workout_plan", None):
            fitness_context.append("User has an existing workout plan")

        if getattr(self.context, "goal_type", None):
            goal_context = self._get_goal_specific_context()
            if goal_context:
                fitness_context.append(goal_context)

        if fitness_context:
            additional_context = "\n".join(fitness_context)
            return f"{base_context}\n\n[Fitness Context]\n{additional_context}"

        return base_context

    def _get_goal_specific_context(self) -> str:
        """Extra context based on user's fitness goal."""
        if not self.context or not self.context.goal_type:
            return ""

        goal_type = getattr(self.context.goal_type, "value", str(self.context.goal_type))  # support Enum or str
        goal_contexts = {
            "weight_loss": "Focus on calorie-burning exercises and sustainable routines.",
            "weight_gain": "Emphasize strength training and muscle-building exercises.",
            "muscle_gain": "Prioritize progressive resistance training and recovery.",
            "endurance": "Focus on cardiovascular fitness and stamina building.",
            "general_fitness": "Provide balanced approach to strength, cardio, and flexibility.",
            "rehabilitation": "Emphasize safe, therapeutic exercises for recovery."
        }
        return goal_contexts.get(goal_type, "")

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to another agent."""
        msg = message.lower()

        nutrition_keywords = [
            "meal plan", "diet", "nutrition", "food", "eating",
            "calories", "protein", "supplements"
        ]
        if any(keyword in msg for keyword in nutrition_keywords):
            return "nutrition"

        progress_keywords = [
            "track progress", "log workout", "record reps",
            "update measurements", "progress tracking"
        ]
        if any(keyword in msg for keyword in progress_keywords):
            return "progress"

        return None
