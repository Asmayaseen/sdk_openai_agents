from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class FitnessAgent(BaseAgent):
    """Specialized fitness agent for workout planning and exercise guidance."""
    
    def __init__(self):
        system_prompt = """You are a certified personal trainer and exercise physiologist. You provide:

1. Personalized workout plans
2. Exercise form and technique guidance
3. Fitness program progression
4. Injury prevention strategies
5. Recovery and rest recommendations

Key Guidelines:
- Always prioritize safety and proper form
- Consider user's fitness level, injuries, and limitations
- Provide clear, step-by-step exercise instructions
- Include warm-up and cool-down recommendations
- Adapt exercises for different equipment availability
- Progress workouts gradually to prevent injury
- For serious injuries or health conditions, recommend consulting healthcare professionals

Focus on creating sustainable, effective fitness routines that match the user's goals and capabilities."""

        super().__init__(
            name="fitness",
            description="Specialized personal trainer for workout planning and exercise guidance",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process fitness-related messages."""
        logger.info(f"Fitness agent processing: {message[:50]}...")
        
        # Build enhanced context for fitness
        contextual_message = self._build_fitness_context(message)
        
        # Stream response from OpenAI
        async for chunk in self.get_openai_response(contextual_message):
            yield chunk

    def _build_fitness_context(self, message: str) -> str:
        """Build fitness-specific context."""
        base_context = self.build_context_prompt(message)
        
        if not self.context:
            return base_context
        
        fitness_context = []
        
        # Add current fitness level
        if self.context.activity_level:
            fitness_context.append(f"Current Activity Level: {self.context.activity_level}")
        
        # Add injury considerations
        if self.context.injury_notes:
            fitness_context.append(f"Injury Considerations: {self.context.injury_notes}")
        
        # Add current workout plan if exists
        if self.context.workout_plan:
            fitness_context.append("User has an existing workout plan")
        
        # Add goal-specific context
        if self.context.goal_type:
            goal_context = self._get_goal_specific_context()
            if goal_context:
                fitness_context.append(goal_context)
        
        if fitness_context:
            additional_context = "\n".join(fitness_context)
            return f"{base_context}\n\n[Fitness Context]\n{additional_context}"
        
        return base_context

    def _get_goal_specific_context(self) -> str:
        """Get goal-specific fitness context."""
        if not self.context or not self.context.goal_type:
            return ""
        
        goal_contexts = {
            "weight_loss": "Focus on calorie-burning exercises and sustainable routines",
            "weight_gain": "Emphasize strength training and muscle-building exercises",
            "muscle_gain": "Prioritize progressive resistance training and recovery",
            "endurance": "Focus on cardiovascular fitness and stamina building",
            "general_fitness": "Provide balanced approach to strength, cardio, and flexibility",
            "rehabilitation": "Emphasize safe, therapeutic exercises for recovery"
        }
        
        return goal_contexts.get(self.context.goal_type.value, "")

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to another agent."""
        message_lower = message.lower()
        
        # Check for nutrition-related keywords
        nutrition_keywords = [
            "meal plan", "diet", "nutrition", "food", "eating",
            "calories", "protein", "supplements"
        ]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"
        
        # Check for progress tracking
        progress_keywords = [
            "track progress", "log workout", "record reps",
            "update measurements", "progress tracking"
        ]
        if any(keyword in message_lower for keyword in progress_keywords):
            return "progress"
        
        return None
