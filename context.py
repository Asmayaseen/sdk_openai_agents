# context.py
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum

# ----------------- Enums -----------------

class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"
    REHABILITATION = "rehabilitation"

class GoalUnit(str, Enum):
    KG = "kg"
    LBS = "lbs"
    PERCENT = "%"
    MINUTES = "minutes"

class DietaryPreference(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    NO_PREFERENCE = "no_preference"

class MedicalCondition(str, Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    HEART_DISEASE = "heart_disease"
    ARTHRITIS = "arthritis"
    NONE = "none"

# ----------------- Sub-Models -----------------

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(...)
    content: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_type: Optional[str] = None

class ProgressEntry(BaseModel):
    date: datetime = Field(default_factory=datetime.now)
    metric: str = Field(...)
    value: float = Field(...)
    unit: str = Field(default="")
    notes: Optional[str] = None

class HandoffLog(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    from_agent: str = Field(...)
    to_agent: str = Field(...)
    reason: str = Field(...)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)

# ----------------- Main Context Model -----------------

class UserSessionContext(BaseModel):
    """
    User session context for health and wellness agent.
    """

    # Assignment-required fields:
    uid: Optional[int] = None   # For assignment compatibility
    user_id: Optional[str] = None  # Prefer user_id, but both supported
    name: str = Field(...)

    # Health goals
    goal: Optional[dict] = None  # Populate from GoalAnalyzerTool
    goal_type: GoalType = Field(default=GoalType.GENERAL_FITNESS)
    goal_target: Optional[float] = None
    goal_unit: GoalUnit = Field(default=GoalUnit.KG)
    goal_deadline: Optional[date] = None

    # Personal info
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = "moderate"

    # Preferences and medical
    dietary_preference: DietaryPreference = Field(default=DietaryPreference.NO_PREFERENCE)
    diet_preferences: Optional[str] = None  # For assignment compatibility (string description)
    food_allergies: List[str] = Field(default_factory=list)
    medical_conditions: List[MedicalCondition] = Field(default_factory=list)
    injury_notes: Optional[str] = None

    # Plans
    meal_plan: Optional[List[str]] = None  # For assignment compatibility
    meal_plan_struct: Dict[str, Any] = Field(default_factory=dict)   # For full daywise plan, if needed
    workout_plan: Optional[Dict[str, Any]] = None

    # Conversation and progress logs
    conversation_history: List[ConversationMessage] = Field(default_factory=list)
    progress_history: List[ProgressEntry] = Field(default_factory=list)
    progress_logs: List[Dict[str, str]] = Field(default_factory=list)  # For assignment compatibility
    latest_metrics: Dict[str, Any] = Field(default_factory=dict)
    handoff_logs: List[str] = Field(default_factory=list)  # Assignment-compatible (str/log)
    handoff_struct_logs: List[HandoffLog] = Field(default_factory=list)

    # Session metadata
    current_agent: str = Field(default="wellness")
    session_start: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    theme: Literal["light", "dark"] = "light"

    # ----------------- Methods -----------------

    def add_message(self, role: str, content: str, agent_type: Optional[str] = None) -> None:
        """Add a message to conversation history."""
        message = ConversationMessage(
            role=role,
            content=content,
            agent_type=agent_type
        )
        self.conversation_history.append(message)
        self.last_activity = datetime.now()

    def add_progress_update(self, metric: str, value: float, unit: str = "", notes: Optional[str] = None) -> None:
        """Add a progress entry."""
        entry = ProgressEntry(
            metric=metric,
            value=value,
            unit=unit,
            notes=notes
        )
        self.progress_history.append(entry)
        self.progress_logs.append({"metric": metric, "value": value, "unit": unit, "notes": notes or ""})
        self.latest_metrics[metric] = {
            "value": value,
            "unit": unit,
            "timestamp": entry.date.isoformat(),
            "notes": notes
        }

    def log_handoff(self, from_agent: str, to_agent: str, reason: str, context_snapshot: Optional[Dict[str, Any]] = None) -> None:
        """Log agent handoff."""
        struct_log = HandoffLog(
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            context_snapshot=context_snapshot or {}
        )
        self.handoff_struct_logs.append(struct_log)
        self.handoff_logs.append(f"{datetime.now().isoformat()}: {from_agent} -> {to_agent} ({reason})")
        self.current_agent = to_agent

    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """Get recent conversation messages."""
        return self.conversation_history[-count:] if self.conversation_history else []

    def update_progress(self, event_type: str, **kwargs) -> None:
        """Update progress with flexible event logging."""
        notes = kwargs.get('notes', f"{event_type} event")
        metric = kwargs.get('metric', event_type)
        value = kwargs.get('value', 1.0)
        unit = kwargs.get('unit', '')
        self.add_progress_update(metric, value, unit, notes)

    def calculate_bmi(self) -> Optional[float]:
        """Calculate BMI if weight and height are available."""
        if self.weight and self.height:
            height_m = self.height / 100  # Convert cm to meters
            return round(self.weight / (height_m ** 2), 1)
        return None

# ----------------- Data Structures for Planning -----------------

class GoalStructure(BaseModel):
    goal: str
    category: str
    duration_weeks: Optional[int] = None
    difficulty: Optional[str] = None

class MealPlanStructure(BaseModel):
    day: str
    meals: List[str]
    total_calories: Optional[int] = None

class WorkoutPlanStructure(BaseModel):
    day: str
    workout_type: str
    duration_minutes: int
    intensity: Optional[str] = None

# ----------------- Test Block -----------------

if __name__ == "__main__":
    print("🚀 Testing UserSessionContext...")

    context = UserSessionContext(
        uid=1,
        user_id="asma001",
        name="Asma Yaseen",
        weight=60,
        height=165,
        age=25,
        diet_preferences="vegetarian"
    )

    print("✅ Context Created")
    print("📊 BMI:", context.calculate_bmi())

    context.add_message("user", "Hello! I want to lose weight.")
    context.add_progress_update("steps", 5000, "count", "Walked in the evening")

    print("🗨️ Recent Message:", context.get_recent_messages()[-1].content)
    print("📈 Latest Progress:", context.latest_metrics)
