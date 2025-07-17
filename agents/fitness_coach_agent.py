from .base_agent import BaseAgent
from openai import Assistant
from typing import Dict, Optional, List, Any, Literal
from ..context import UserSessionContext
from datetime import datetime


class FitnessCoachAgent(BaseAgent):
    """Agent for providing personalized exercise recommendations."""

    def __init__(self):
        super().__init__(
            name="FitnessCoachAgent",
            description="Provides workout plans based on fitness levels and goals",
            tools=[self.create_workout_plan, self.adjust_for_equipment]  # ✅ This is fine only if agent system allows bound methods
        )

        self.exercise_library: Dict[str, List[Dict[str, Any]]] = {
            "beginner": [
                {"name": "Bodyweight Squats", "muscles": ["quadriceps", "glutes"], "equipment": []},
                {"name": "Wall Push-ups", "muscles": ["chest", "triceps"], "equipment": ["wall"]}
            ],
            "intermediate": [
                {"name": "Dumbbell Lunges", "muscles": ["quadriceps", "hamstrings"], "equipment": ["dumbbells"]},
                {"name": "Push-ups", "muscles": ["chest", "shoulders"], "equipment": []}
            ],
            "advanced": [
                {"name": "Barbell Squats", "muscles": ["legs", "core"], "equipment": ["barbell", "rack"]},
                {"name": "Pull-ups", "muscles": ["back", "biceps"], "equipment": ["pull-up bar"]}
            ]
        }

    @Assistant.tool
    async def create_workout_plan(
        self,
        level: Literal["beginner", "intermediate", "advanced"],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate workout plan based on user's fitness level.
        """
        try:
            exercises = self.exercise_library.get(level.lower())
            if not exercises:
                raise ValueError(f"Invalid fitness level: {level}")

            return {
                "exercises": [ex.copy() for ex in exercises],
                "schedule": self._generate_schedule(level.lower()),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    @Assistant.tool
    async def adjust_for_equipment(
        self,
        equipment: List[str],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Filter exercises based on available equipment.
        """
        try:
            equipment_lower = [e.lower() for e in equipment]
            suitable, missing = [], []

            for level_exercises in self.exercise_library.values():
                for exercise in level_exercises:
                    req = exercise.get("equipment", [])
                    if all(item.lower() in equipment_lower for item in req):
                        suitable.append(exercise.copy())
                    elif req:
                        missing.append(exercise.copy())

            return {
                "suitable_exercises": suitable,
                "missing_equipment": missing,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _generate_schedule(self, level: str) -> Dict[str, str]:
        """Generate weekly workout schedule based on fitness level."""
        schedules = {
            "beginner": {
                "Monday": "Full body circuit",
                "Thursday": "Core and flexibility"
            },
            "intermediate": {
                "Monday": "Upper body",
                "Wednesday": "Lower body",
                "Friday": "Cardio"
            },
            "advanced": {
                "Monday": "Push (Chest/Triceps/Shoulders)",
                "Tuesday": "Pull (Back/Biceps)",
                "Thursday": "Legs",
                "Saturday": "Conditioning"
            }
        }
        return schedules.get(level, {})
