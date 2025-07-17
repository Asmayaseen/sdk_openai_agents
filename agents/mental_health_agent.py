from .base_agent import BaseAgent
from openai import Assistant
from typing import Dict, Optional, List, Any
from ..context import UserSessionContext
from datetime import datetime

class MentalHealthAgent(BaseAgent):
    """Agent for stress management and sleep hygiene recommendations"""

    def __init__(self):
        super().__init__(
            name="MentalHealthAgent",
            description="Provides mental wellness and sleep improvement strategies",
            tools=[self.suggest_stress_techniques, self.create_sleep_plan]
        )
        self.stress_techniques: Dict[int, List[str]] = {
            1: ["Deep breathing exercises", "Short walk"],
            2: ["Progressive muscle relaxation", "Guided meditation"],
            3: ["Journaling", "Nature exposure"],
            4: ["Cognitive restructuring", "Digital detox"],
            5: ["Professional counseling recommended"]
        }

        self.sleep_protocols: Dict[str, List[str]] = {
            "insomnia": ["Sleep restriction therapy", "Stimulus control"],
            "apnea": ["Positional therapy", "CPAP consultation"],
            "restless": ["Iron level check", "Evening stretching"],
            "general": ["Consistent bedtime", "Blue light reduction"]
        }

    @Assistant.tool
    async def suggest_stress_techniques(
        self,
        stress_level: int,
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Recommend stress reduction methods based on stress level (1-5 scale)
        """
        try:
            if not 1 <= stress_level <= 5:
                raise ValueError("Stress level must be between 1 and 5")

            techniques = self.stress_techniques.get(stress_level, [])
            urgency = "Within 1 week" if stress_level < 4 else "Immediately"

            if context:
                context.update_progress(
                    update=f"Stress level {stress_level} assessed",
                    metric="stress_management",
                    value=stress_level
                )

            return {
                "techniques": techniques,
                "urgency": urgency,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "recommendation": "Contact mental health professional"
            }

    @Assistant.tool
    async def create_sleep_plan(
        self,
        sleep_issues: List[str],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized sleep improvement plan.
        """
        try:
            if not sleep_issues or not all(isinstance(i, str) for i in sleep_issues):
                raise ValueError("At least one valid sleep issue must be provided.")

            protocols: List[str] = []

            for issue in sleep_issues:
                issue_key = issue.strip().lower()
                matched_protocols = self.sleep_protocols.get(issue_key)
                if matched_protocols:
                    protocols.extend(matched_protocols)

            if not protocols:
                protocols = self.sleep_protocols["general"]

            plan = {
                "protocols": sorted(set(protocols)),
                "precautions": [
                    "No caffeine after 2pm",
                    "Consistent wake-up time",
                    "Bed only for sleep"
                ],
                "timestamp": datetime.now().isoformat()
            }

            if context:
                context.update_progress(
                    update=f"Sleep plan created for {len(sleep_issues)} issues",
                    metric="sleep_improvement",
                    value=len(sleep_issues)
                )

            return plan

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "fallback_protocols": self.sleep_protocols["general"]
            }
