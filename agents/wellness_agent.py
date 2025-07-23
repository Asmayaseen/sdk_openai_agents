from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class WellnessAgent(BaseAgent):
    """Primary wellness coaching agent for general health guidance."""
    
    def __init__(self):
        system_prompt = """You are a certified wellness coach and health advisor. You provide:

1. General health and wellness guidance
2. Lifestyle recommendations 
3. Motivation and goal-setting support
4. Holistic health approaches

Key Guidelines:
- Always prioritize user safety and recommend consulting healthcare professionals for medical issues
- Provide evidence-based advice when possible
- Be encouraging and supportive
- Consider the user's complete health context
- Make personalized recommendations based on their goals and preferences
- If asked about specific nutrition or workout plans, suggest consulting the nutrition or fitness specialists

Remember: You are not a medical doctor. Always recommend consulting healthcare professionals for medical concerns."""

        super().__init__(
            name="wellness",
            description="Primary wellness coach for general health guidance and motivation",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process wellness-related messages."""
        logger.info(f"Wellness agent processing: {message[:50]}...")
        
        # Build context-aware prompt
        contextual_message = self.build_context_prompt(message)
        
        # Stream response from OpenAI
        async for chunk in self.get_openai_response(contextual_message):
            yield chunk

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to specialist agent."""
        message_lower = message.lower()
        
        # Check for nutrition-related keywords
        nutrition_keywords = [
            "meal plan", "diet", "nutrition", "calories", "food", "recipe",
            "eat", "eating", "macros", "protein", "carbs", "fat"
        ]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"
        
        # Check for fitness-related keywords
        fitness_keywords = [
            "workout", "exercise", "training", "gym", "fitness", "strength",
            "cardio", "running", "lifting", "weights", "routine"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"
        
        # Check for progress tracking keywords
        progress_keywords = [
            "track", "progress", "weight", "measurement", "record", "log",
            "update", "metric", "goal progress"
        ]
        if any(keyword in message_lower for keyword in progress_keywords):
            return "progress"
        
        return None

    def get_welcome_message(self) -> str:
        """Get personalized welcome message."""
        if not self.context:
            return "Hello! I'm your wellness coach. How can I help you today?"
        
        name = self.context.name
        goal = self.context.goal_type.value.replace("_", " ").title() if self.context.goal_type else "general wellness"
        
        return f"""Hello {name}! 🌟 

I'm your personal wellness coach, here to support you on your {goal} journey. 

I can help you with:
• General health and wellness guidance
• Lifestyle recommendations
• Goal setting and motivation
• Connecting you with our nutrition and fitness specialists

What would you like to focus on today?"""
