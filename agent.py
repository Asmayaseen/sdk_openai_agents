"""
Main Health & Wellness Planner Agent
Coordinates tools and handles handoffs to specialized agents
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from context import UserSessionContext
from tools.goal_analyzer import GoalAnalyzerTool
from tools.meal_planner import MealPlannerTool
from tools.workout_recommender import WorkoutRecommenderTool
from tools.scheduler import CheckinSchedulerTool
from tools.progress_tracker import ProgressTrackerTool
from agents.escalation_agent import EscalationAgent
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent
from guardrails import HealthWellnessGuardrails


class HealthWellnessAgent:
    """Coordinator agent that orchestrates user requests via tools and delegates to specialized agents as needed."""

    def __init__(self):
        self.tools = {
            "goal_analyzer": GoalAnalyzerTool(),
            "meal_planner": MealPlannerTool(),
            "workout_recommender": WorkoutRecommenderTool(),
            "scheduler": CheckinSchedulerTool(),
            "progress_tracker": ProgressTrackerTool()
        }

        self.handoff_agents = {
            "escalation": EscalationAgent(),
            "nutrition_expert": NutritionExpertAgent(),
            "injury_support": InjurySupportAgent()
        }

        self.guardrails = HealthWellnessGuardrails()
        self.name = "HealthWellnessAgent"
        self.instructions = self._get_instructions()

    def _get_instructions(self) -> str:
        return (
            "You are a Health & Wellness Planner Agent.\n"
            "Use tools to help users:\n"
            "- Set goals\n"
            "- Get meal and workout plans\n"
            "- Track progress\n"
            "- Handle health-specific needs via agent handoff"
        )

    async def process_message(self, message: str, context: UserSessionContext) -> str:
        """Process incoming user message, validate, route, respond."""
        try:
            context.last_activity = datetime.now()

            validated_input = self.guardrails.validate_input(message)
            if not validated_input.get("is_valid", True):
                return f"❌ {validated_input.get('error', 'Invalid input')}"

            handoff_target = self._should_handoff(message)
            if handoff_target:
                response = await self._handle_handoff(handoff_target, message, context)
                context.add_message("user", message)
                context.add_message("assistant", response, handoff_target)
                return response

            tool_name = self._determine_tool(message, context)
            if tool_name:
                response = await self._use_tool(tool_name, message, context)
                context.add_message("user", message)
                context.add_message("assistant", response, tool_name)
                return response

            response = await self._generate_default_response(message, context)
            context.add_message("user", message)
            context.add_message("assistant", response, "default")
            return response

        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            context.add_message("user", message)
            context.add_message("assistant", error_msg, "error")
            return error_msg

    def _should_handoff(self, message: str) -> Optional[str]:
        """Check if the message should be handed off to a specialized agent."""
        msg = message.lower()
        if any(keyword in msg for keyword in ["human", "coach", "speak to person", "trainer", "real expert"]):
            return "escalation"
        if any(keyword in msg for keyword in ["diabetes", "hypertension", "insulin", "heart", "cholesterol", "blood sugar"]):
            return "nutrition_expert"
        if any(keyword in msg for keyword in ["pain", "injury", "arthritis", "rehab", "knee", "shoulder", "sprain"]):
            return "injury_support"
        return None

    async def _handle_handoff(self, agent_type: str, message: str, context: UserSessionContext) -> str:
        """Delegate message handling to a specialized agent."""
        if agent_type not in self.handoff_agents:
            return "❌ Cannot handle your request right now."

        context.log_handoff(
            from_agent=self.name,
            to_agent=agent_type,
            reason=f"Trigger: {agent_type}",
            context_snapshot=context.dict()
        )

        return await self.handoff_agents[agent_type].process_message(message, context)

    def _determine_tool(self, message: str, context: UserSessionContext) -> Optional[str]:
        """Map keywords to appropriate internal tools."""
        msg = message.lower()
        if any(k in msg for k in ["lose", "gain", "goal", "target", "build muscle"]) and not context.goal_target:
            return "goal_analyzer"
        if any(k in msg for k in ["meal", "diet", "food", "eat", "nutrition"]):
            return "meal_planner"
        if any(k in msg for k in ["exercise", "workout", "fitness", "training"]):
            return "workout_recommender"
        if any(k in msg for k in ["progress", "track", "update", "log", "weigh"]):
            return "progress_tracker"
        if any(k in msg for k in ["schedule", "remind", "check-in", "appointment"]):
            return "scheduler"
        return None

    async def _use_tool(self, tool_name: str, message: str, context: UserSessionContext) -> str:
        """Run selected tool and validate its output."""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"❌ Tool '{tool_name}' not available."

        try:
            output = await tool.run(message, context)
            validated = self.guardrails.validate_output(output, tool_name)
            if not validated.get("is_valid", True):
                return f"❌ Output validation failed: {validated.get('error', '')}"
            return validated.get("data", "✅ Done.")
        except Exception as e:
            return f"❌ Error running {tool_name}: {str(e)}"

    async def _generate_default_response(self, message: str, context: UserSessionContext) -> str:
        """Generate fallback message if no tool/handoff applies."""
        name = context.name
        response = f"Hello {name}! I'm your Health & Wellness Assistant. 👋\n\n"
        if not context.goal_target:
            response += "Tell me your goal! For example:\n• 'I want to lose 5kg in 2 months'\n• 'I want a vegetarian meal plan'\n"
        else:
            response += "You can ask me to:\n• Make a meal or workout plan\n• Track your progress\n• Schedule reminders\n"
        response += "\nHow can I help you today?"
        return response

    def get_capabilities(self) -> List[str]:
        """List of this agent's high-level features."""
        return [
            "Structured goal analysis",
            "Meal and workout planning",
            "Progress tracking",
            "Agent handoffs",
            "Real-time interaction"
        ]
