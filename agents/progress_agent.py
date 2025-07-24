from typing import AsyncGenerator, Optional
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class ProgressAgent(BaseAgent):
    """Specialized agent for progress tracking and analytics."""

    def __init__(self):
        system_prompt = (
            "You are a health analytics specialist focused on progress tracking and goal monitoring. You provide:\n"
            "1. Progress analysis and insights\n"
            "2. Goal tracking and milestone recognition\n"
            "3. Data interpretation and trends\n"
            "4. Motivation based on achievements\n"
            "5. Recommendations for goal adjustments\n\n"
            "Key Guidelines:\n"
            "- Analyze user's progress data to provide meaningful insights\n"
            "- Celebrate achievements and milestones\n"
            "- Identify trends and patterns in the data\n"
            "- Provide constructive feedback on goal progress\n"
            "- Suggest adjustments when goals need to be modified\n"
            "- Be encouraging while being realistic about progress\n"
            "- Help users understand what their data means for their health journey\n\n"
            "Focus on helping users understand their progress and stay motivated toward their goals."
        )
        super().__init__(
            name="progress",
            description="Specialized analyst for progress tracking and goal monitoring",
            system_prompt=system_prompt
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process progress-related messages (Gemini streaming)."""
        logger.info(f"Progress agent processing: {message[:50]}...")

        contextual_message = self._build_progress_context(message)

        async for chunk in self.get_gemini_response(contextual_message):
            yield chunk

    def _build_progress_context(self, message: str) -> str:
        """Build progress-specific user prompt for analysis."""
        base_context = self.build_context_prompt(message)
        ctx = self.context

        if not ctx:
            return base_context

        progress_context = []

        # Add recent progress entries
        if getattr(ctx, "progress_history", None):
            recent_entries = ctx.progress_history[-5:]  # Last 5 entries
            progress_summary = [
                f"{entry.date.strftime('%Y-%m-%d')}: {entry.metric} = {entry.value}{entry.unit}"
                for entry in recent_entries
            ]
            progress_context.append("Recent Progress Entries:")
            progress_context.extend(progress_summary)

        # Add latest metrics
        if getattr(ctx, "latest_metrics", None) and ctx.latest_metrics:
            progress_context.append("Current Metrics:")
            for metric, data in ctx.latest_metrics.items():
                progress_context.append(f"{metric}: {data['value']}{data['unit']}")

        # Add goal information
        if getattr(ctx, "goal_type", None) and getattr(ctx, "goal_target", None):
            goal_unit = getattr(ctx.goal_unit, "value", str(ctx.goal_unit)) if getattr(ctx, "goal_unit", None) else ""
            progress_context.append(f"Current Goal: {ctx.goal_type.value} - Target: {ctx.goal_target}{goal_unit}")

        if progress_context:
            additional_context = "\n".join(progress_context)
            return f"{base_context}\n\n[Progress Context]\n{additional_context}"

        return base_context

    async def should_handoff(self, message: str) -> Optional[str]:
        """
        Determine if message should be handed off to another agent.
        Returns the agent name string or None.
        """
        message_lower = message.lower()

        # Nutrition
        nutrition_keywords = [
            "meal plan", "diet plan", "nutrition advice", "food recommendations"
        ]
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition"

        # Fitness
        fitness_keywords = [
            "workout plan", "exercise routine", "training program", "fitness plan"
        ]
        if any(keyword in message_lower for keyword in fitness_keywords):
            return "fitness"

        # Wellness/general
        wellness_keywords = [
            "general advice", "wellness tips", "health guidance", "lifestyle"
        ]
        if any(keyword in message_lower for keyword in wellness_keywords):
            return "wellness"

        return None

    def generate_progress_summary(self) -> str:
        """Generate a comprehensive progress summary from the agent context."""
        ctx = self.context
        if not ctx:
            return "No progress data available."

        summary_parts = []

        # Goal progress
        if getattr(ctx, "goal_type", None) and getattr(ctx, "goal_target", None):
            goal_unit = getattr(ctx.goal_unit, "value", str(ctx.goal_unit)) if getattr(ctx, "goal_unit", None) else ""
            summary_parts.append(f"Goal: {ctx.goal_type.value} - Target: {ctx.goal_target}{goal_unit}")

        # Latest progress
        if getattr(ctx, "progress_history", None) and ctx.progress_history:
            latest_entry = ctx.progress_history[-1]
            summary_parts.append(f"Latest Update: {latest_entry.metric} = {latest_entry.value}{latest_entry.unit}")

        # Total entries
        total_entries = len(ctx.progress_history) if getattr(ctx, "progress_history", None) else 0
        summary_parts.append(f"Total Progress Entries: {total_entries}")

        return "\n".join(summary_parts) if summary_parts else "No progress data available."

    def get_capabilities(self):
        return [
            "Progress analysis and insights",
            "Goal tracking and milestone recognition",
            "Data interpretation and trends",
            "Motivation based on achievements",
            "Recommendations for goal adjustments"
        ]
