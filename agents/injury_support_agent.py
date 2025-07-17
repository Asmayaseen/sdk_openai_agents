from .base_agent import BaseAgent
from openai import Assistant
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from typing_extensions import Annotated
from ..context import UserSessionContext
from datetime import datetime

try:
    from pydantic import field_validator  # Pydantic v2
except ImportError:
    from pydantic import validator as field_validator  # Pydantic v1 fallback


class InjuryInput(BaseModel):
    """Guardrail model for injury input validation"""
    notes: str

    @field_validator('notes')
    @classmethod
    def validate_injury_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Injury description must be at least 5 characters")
        blocked_terms = ["emergency", "broken", "fracture", "bleeding"]
        if any(term in v.lower() for term in blocked_terms):
            raise ValueError("For serious injuries, please consult a doctor immediately")
        return v


class InjurySupportAgent(BaseAgent):
    """Agent for providing injury-specific workout modifications and recovery guidance"""

    def __init__(self):
        super().__init__(
            name="InjurySupportAgent",
            description="Provides safe workout modifications and recovery advice for injuries",
            tools=[self.provide_injury_advice, self.log_recovery_progress]
        )

        self.injury_modifications: Dict[str, Dict[str, Any]] = {
            "knee": {
                "avoid": ["Squats", "Lunges", "Jumping exercises", "Stair climbing"],
                "recommend": ["Leg extensions", "Seated leg press", "Swimming", "Cycling"],
                "recovery_tips": [
                    "RICE method (Rest, Ice, Compression, Elevation)",
                    "Quad and hamstring stretches",
                    "Low-impact cardio for 20-30 mins daily"
                ]
            },
            "back": {
                "avoid": ["Deadlifts", "Overhead press", "Twisting motions", "Heavy lifting"],
                "recommend": ["Bird dogs", "Pelvic tilts", "Walking", "Yoga"],
                "recovery_tips": [
                    "Maintain proper posture",
                    "Core strengthening exercises",
                    "Heat therapy for muscle relaxation"
                ]
            },
            "shoulder": {
                "avoid": ["Overhead presses", "Bench press", "Pull-ups"],
                "recommend": ["Band pull-aparts", "Scapular squeezes", "Wall slides"],
                "recovery_tips": [
                    "Rotator cuff strengthening",
                    "Avoid sleeping on affected side",
                    "Gentle range-of-motion exercises"
                ]
            }
        }

        self.recovery_plans: Dict[str, List[Dict[str, Any]]] = {}

    @Assistant.tool
    async def provide_injury_advice(
        self,
        injury_type: str,
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Provides exercise modifications for specific injuries.
        """
        try:
            validated = InjuryInput(notes=injury_type)
            injury_clean = validated.notes.lower()

            advice = {
                "avoid": ["All painful movements"],
                "recommend": ["Low-impact exercises", "Consult physical therapist"],
                "recovery_tips": ["Rest affected area"],
                "timestamp": datetime.now().isoformat()
            }

            matched = False
            for key, mod in self.injury_modifications.items():
                if key in injury_clean:
                    advice.update({
                        "avoid": mod["avoid"].copy(),
                        "recommend": mod["recommend"].copy(),
                        "recovery_tips": mod["recovery_tips"].copy(),
                        "specific_for": key
                    })
                    matched = True
                    break

            if not matched:
                advice["note"] = "Injury type not recognized. Please consult a specialist for detailed guidance."

            if context:
                context.injury_notes = injury_clean
                context.update_progress(
                    update=f"Received advice for {injury_clean}",
                    metric="injury_consultation"
                )

            return advice

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "recommendation": "Consult a healthcare professional"
            }

    @Assistant.tool
    async def log_recovery_progress(
        self,
        injury_type: str,
        progress_notes: str,
        pain_level: Annotated[int, (1, 10)],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Tracks injury recovery progress.
        """
        try:
            if not 1 <= pain_level <= 10:
                raise ValueError("Pain level must be between 1 and 10")

            record = {
                "timestamp": datetime.now().isoformat(),
                "pain_level": pain_level,
                "notes": progress_notes,
                "recommendations": self._generate_recommendations(injury_type.lower(), pain_level)
            }

            plan_id = f"{injury_type}_{datetime.now().strftime('%Y%m%d')}"
            self.recovery_plans.setdefault(plan_id, []).append(record)

            if context:
                context.update_progress(
                    update=f"Updated {injury_type} recovery",
                    metric="pain_level",
                    value=pain_level
                )

            return {
                "status": "success",
                "plan_id": plan_id,
                "next_steps": record["recommendations"]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _generate_recommendations(self, injury_type: str, pain_level: int) -> List[str]:
        """Generate recommendations based on pain level."""
        if pain_level >= 7:
            return ["Complete rest", "Medical consultation"]
        elif pain_level >= 4:
            return self.injury_modifications.get(injury_type, {}).get("recommend", ["Gentle stretching"])
        return self.injury_modifications.get(injury_type, {}).get("recommend", ["Gradual return to activity"])
