from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Dict, Optional, List, Any, Type
from .base_tool import BaseTool
from ..context import UserSessionContext
import logging

logger = logging.getLogger(__name__)


# -----------------------------
# 🔹 Input Schema
# -----------------------------
class GoalInput(BaseModel):
    """Input model for goal analysis with comprehensive validation"""
    goal_description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Natural language description of health/fitness goal"
    )
    target_value: float = Field(
        ...,
        gt=0,
        description="Numerical target value for the goal"
    )
    unit: str = Field(
        ...,
        pattern="^(kg|lbs|cm|inches|%|bmi|minutes|seconds)$",
        description="Unit of measurement for the target"
    )
    timeframe_weeks: int = Field(
        ...,
        ge=1,
        le=52,
        description="Duration to achieve goal in weeks"
    )
    current_value: Optional[float] = Field(
        None,
        ge=0,
        description="Current baseline value (optional)"
    )

    @field_validator('goal_description')
    @classmethod
    def validate_goal_description(cls, v: str) -> str:
        required_phrases = ["lose", "gain", "maintain", "improve", "achieve", "reduce"]
        if not any(phrase in v.lower() for phrase in required_phrases):
            raise ValueError("Goal must include an action verb (e.g., lose/gain/improve)")
        return v.strip()

    @field_validator('target_value', 'current_value')
    @classmethod
    def validate_reasonable_values(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v > 1000:
            raise ValueError("Value exceeds realistic health metric limits")
        return v


# -----------------------------
# 🔹 Output Schema
# -----------------------------
class GoalAnalysisOutput(BaseModel):
    structured_goal: Dict[str, Any] = Field(..., description="Standardized goal representation")
    weekly_targets: Dict[int, float] = Field(..., description="Weekly milestones")
    risk_assessment: str = Field(..., description="Risk level of goal pace")
    suggested_actions: List[str] = Field(..., description="Action steps to achieve goal")
    confidence_score: float = Field(..., ge=0, le=1, description="Estimated achievability (0 to 1)")


# -----------------------------
# 🔹 Tool Implementation
# -----------------------------
class GoalAnalyzerTool(BaseTool):
    """
    Health Goal Analyzer Tool

    Parses natural language health goals and converts them into measurable plans with:
    - Weekly progress targets
    - Risk assessment
    - Actionable recommendations
    """

    @classmethod
    def name(cls) -> str:
        return "goal_analyzer"

    @classmethod
    def description(cls) -> str:
        return (
            "Analyzes and structures health/fitness goals into measurable plans. "
            "Provides weekly targets, risk levels, recommendations, and confidence scores."
        )

    @classmethod
    def input_schema(cls) -> Type[BaseModel]:
        return GoalInput

    @classmethod
    def output_schema(cls) -> Type[BaseModel]:
        return GoalAnalysisOutput

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        logger.info(f"Analyzing goal: {input_data['goal_description']}")

        current = input_data.get("current_value", 0.0)
        target = input_data["target_value"]
        unit = input_data["unit"]
        weeks = input_data["timeframe_weeks"]

        weekly_change = (target - current) / weeks

        structured_goal = {
            "metric": unit,
            "current_value": current,
            "target_value": target,
            "timeframe_weeks": weeks,
            "start_date": date.today().isoformat(),
            "goal_type": self._detect_goal_type(input_data["goal_description"])
        }

        weekly_targets = {
            week: round(current + week * weekly_change, 2)
            for week in range(1, weeks + 1)
        }

        risk = self._assess_risk(weekly_change, unit, input_data["goal_description"])
        actions = self._generate_actions(input_data["goal_description"], weekly_change, context)
        confidence = self._calculate_confidence(weekly_change, unit)

        if context:
            context.update_progress(
                f"Goal set: {input_data['goal_description']}",
                metric=unit,
                value=current
            )
            context.goal = structured_goal

        return {
            "structured_goal": structured_goal,
            "weekly_targets": weekly_targets,
            "risk_assessment": risk,
            "suggested_actions": actions,
            "confidence_score": confidence
        }

    def _assess_risk(self, weekly_change: float, unit: str, description: str) -> str:
        if "maintain" in description.lower():
            return "Low"

        thresholds = {"kg": 1.0, "lbs": 2.2, "%": 1.5, "bmi": 0.5}
        threshold = thresholds.get(unit, 1.0)
        abs_change = abs(weekly_change)

        if abs_change > threshold * 1.5:
            return "High"
        elif abs_change > threshold:
            return "Moderate"
        return "Low"

    def _generate_actions(
        self,
        description: str,
        weekly_change: float,
        context: Optional[UserSessionContext] = None
    ) -> List[str]:
        actions = []
        desc = description.lower()

        if weekly_change < 0:
            actions += [
                "Maintain caloric deficit (300–500 kcal/day)",
                "Do cardio 3–5x per week",
                "Add strength training 2–3x per week"
            ]
        else:
            actions += [
                "Increase calorie intake by 200–300 kcal/day",
                "Do resistance training with progressive overload",
                "Consume high-protein meals (1.6–2.2g/kg)"
            ]

        if context:
            if context.dietary_preferences:
                actions.append(f"Adjust meals for {context.dietary_preferences} diet")
            if context.injury_notes:
                actions.append("Modify workouts to avoid injury strain")

        return actions

    def _calculate_confidence(self, weekly_change: float, unit: str) -> float:
        safe_ranges = {"kg": 0.5, "lbs": 1.0, "%": 0.7, "bmi": 0.3}
        threshold = safe_ranges.get(unit, 0.5)
        abs_change = abs(weekly_change)

        if abs_change <= threshold:
            return 0.9
        elif abs_change <= threshold * 1.5:
            return 0.7
        elif abs_change <= threshold * 2:
            return 0.5
        return 0.3

    def _detect_goal_type(self, description: str) -> str:
        desc = description.lower()
        if any(word in desc for word in ["lose", "reduce", "decrease"]):
            return "weight_loss"
        elif any(word in desc for word in ["gain", "increase", "build"]):
            return "weight_gain"
        elif "maintain" in desc:
            return "maintenance"
        return "improvement"
