from openai import Assistant
from typing import List, Optional, Dict, Any
from .context import UserSessionContext
from .tools.goal_analyzer import GoalAnalyzerTool
from .tools.meal_planner import MealPlannerTool
from .tools.workout_recommender import WorkoutRecommenderTool
from .agents.nutrition_expert_agent import NutritionExpertAgent
from .agents.injury_support_agent import InjurySupportAgent
from .agents.escalation_agent import EscalationAgent
from datetime import datetime

class HealthWellnessAgent(Assistant):
    def __init__(self, handoff_agents: Optional[List[Assistant]] = None):
        self.goal_tool = GoalAnalyzerTool()
        self.meal_tool = MealPlannerTool()
        self.workout_tool = WorkoutRecommenderTool()

        super().__init__(
            name="HealthWellnessAgent",
            description="Primary agent for comprehensive wellness planning",
            tools=[self.goal_tool, self.meal_tool, self.workout_tool]
        )

        self.specialized_agents = {
            "NutritionExpertAgent": NutritionExpertAgent(),
            "InjurySupportAgent": InjurySupportAgent(),
            "EscalationAgent": EscalationAgent()
        }

        if handoff_agents:
            for agent in handoff_agents:
                self.specialized_agents[agent.name] = agent

    async def on_tool_start(self, tool_name: str, input: Dict[str, Any]) -> None:
        print(f"[{datetime.now().isoformat()}] Tool started: {tool_name}")
        print(f"Input parameters: {input}")

    async def on_handoff(self, target_agent_name: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            if target_agent_name not in self.specialized_agents:
                raise ValueError(f"Unknown agent: {target_agent_name}")
            print(f"[{datetime.now().isoformat()}] Handing off to {target_agent_name}")
            return {
                "status": "success",
                "target_agent": target_agent_name,
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def run_conversation(self, user_input: str, context: Optional[UserSessionContext] = None) -> Dict[str, Any]:
        if not context:
            context = UserSessionContext()

        try:
            goal = await self.goal_tool.run({"goal_text": user_input}, context)
            meals = await self.meal_tool.run({"diet_preferences": context.diet_preferences or ""}, context)
            workout = await self.workout_tool.run({"fitness_level": context.fitness_level or "beginner"}, context)

            return {
                "response": {
                    "goal": goal.output,
                    "meals": meals.output,
                    "workout": workout.output
                },
                "context": context,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
