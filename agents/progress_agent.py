from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class ProgressAgent(BaseAgent):
    """Specialized agent for progress tracking and analytics."""
    
    def __init__(self):
        system_prompt = """You are a health analytics specialist focused on progress tracking and goal monitoring. You provide:

1. Progress analysis and insights
2. Goal tracking and milestone recognition
3. Data interpretation and trends
4. Motivation based on achievements
5. Recommendations for goal adjustments

Key Guidelines:
- Analyze user's progress data to provide meaningful insights
- Celebrate achievements and milestones
- Identify trends and patterns in the data
- Provide constructive feedback on goal progress
- Suggest adjustments when goals need to be modified
- Be encouraging while being realistic about progress
- Help users understand what their data means for their health journey

Focus on helping users understand their progress and stay motivated toward their goals."""

        super().__init__(
            name="progress",
            description="Specialized analyst for progress tracking and goal monitoring",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process progress-related messages."""
        logger.info(f"Progress agent processing: {message[:50]}...")
        
        # Build enhanced context for progress tracking
        contextual_message = self._build_progress_context(message)
        
        # Stream response from OpenAI
        async for chunk in self.get_openai_response(contextual_message):
            yield chunk

    def _build_progress_context(self, message: str) -> str:
        """Build progress-specific context."""
        base_context = self.build_context_prompt(message)
        
        if not self.context:
            return base_context
        
        progress_context = []
        
        # Add recent progress entries
        if self.context.progress_history:
            recent_entries = self.context.progress_history[-5:]  # Last 5 entries
            progress_summary = []
            for entry in recent_entries:
                progress_summary.append(f"{entry.date.strftime('%Y-%m-%d')}: {entry.metric} = {entry.value}{entry.unit}")
            
            progress_context.append("Recent Progress Entries:")
            progress_context.extend(progress_summary)
        
        # Add latest metrics
        if self.context.latest_metrics:
            progress_context.append("\nCurrent Metrics:")
            for metric, data in self.context.latest_metrics.items():
                progress_context.append(f"{metric}: {data['value']}{data['unit']}")
        
        # Add goal information
        if self.context.goal_type and self.context.goal_target:
            progress_context.append(f"\nCurrent Goal: {self.context.goal_type.value} - Target: {self.context.goal_target}{self.context.goal_unit.value}")
        
        if progress_context:
            additional_context = "\n".join(progress_context)
            return f"{base_context}\n\n[Progress Context]\n{additional_context}"
        
        return base_context

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if message should be handed off to another agent."""
        message_lower = message.lower()
        
        # Check for nutrition planning
        nutrition_keywords = [
            "meal plan", "diet plan", "nutrition advice", "food recommendations"
        ]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"
        
        # Check for workout planning
        fitness_keywords = [
            "workout plan", "exercise routine", "training program", "fitness plan"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"
        
        # Check for general wellness guidance
        wellness_keywords = [
            "general advice", "wellness tips", "health guidance", "lifestyle"
        ]
        if any(keyword in message_lower for keyword in wellness_keywords):
            return "wellness"
        
        return None

    def generate_progress_summary(self) -> str:
        """Generate a comprehensive progress summary."""
        if not self.context:
            return "No progress data available."
        
        summary_parts = []
        
        # Goal progress
        if self.context.goal_type and self.context.goal_target:
            summary_parts.append(f"Goal: {self.context.goal_type.value} - Target: {self.context.goal_target}{self.context.goal_unit.value}")
        
        # Recent progress
        if self.context.progress_history:
            latest_entry = self.context.progress_history[-1]
            summary_parts.append(f"Latest Update: {latest_entry.metric} = {latest_entry.value}{latest_entry.unit}")
        
        # Total entries
        total_entries = len(self.context.progress_history)
        summary_parts.append(f"Total Progress Entries: {total_entries}")
        
        return "\n".join(summary_parts) if summary_parts else "No progress data available."
