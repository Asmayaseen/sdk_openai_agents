from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Literal, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ---------------- ENUMS ----------------

class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_BUILDING = "muscle_building"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"


class GoalUnit(str, Enum):
    KG = "kg"
    LBS = "lbs"
    CM = "cm"
    INCHES = "inches"
    MILES = "miles"
    KM = "km"


class DietaryPreference(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    OMNIVORE = "omnivore"


class MedicalCondition(str, Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    HIGH_CHOLESTEROL = "high_cholesterol"
    NONE = "none"


# ---------------- TYPES ----------------

class WorkoutPlan(TypedDict):
    days_per_week: Annotated[int, Field(ge=1, le=7)]
    duration_minutes: Annotated[int, Field(ge=10, le=180)]
    intensity: Literal["low", "medium", "high"]
    exercises: List[Dict[str, str]]


class MealPlanDay(BaseModel):
    day: str = Field(..., description="Day of the week")
    breakfast: str = Field(..., min_length=1)
    lunch: str = Field(..., min_length=1)
    dinner: str = Field(..., min_length=1)
    snacks: Optional[str] = Field(None, min_length=1)


class HandoffLog(BaseModel):
    model_config = ConfigDict(extra='forbid')

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    from_agent: str = Field(..., min_length=1)
    to_agent: str = Field(..., min_length=1)
    reason: Optional[str] = Field(None, max_length=200)
    context_snapshot: Optional[Dict] = None

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        datetime.fromisoformat(v)
        return v


class ProgressLog(BaseModel):
    model_config = ConfigDict(extra='forbid')

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: Literal["goal_update", "measurement", "note", "system"]
    description: str = Field(..., max_length=500)
    metric: Optional[str] = Field(None, max_length=50)
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=20)

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None and not info.data.get('metric'):
            raise ValueError("Metric must be specified when providing a value")
        return v


# ---------------- MAIN CONTEXT ----------------

class UserSessionContext(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True)

    # User Identification
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Health Goals and Preferences
    goal_type: GoalType
    goal_target: float = Field(..., ge=0.1, le=1000)
    goal_unit: GoalUnit
    goal_deadline: str
    dietary_preference: DietaryPreference
    food_allergies: List[str] = Field(default_factory=list, max_length=50)
    medical_conditions: List[MedicalCondition] = Field(default_factory=list)

    # Optional Plans & Notes
    workout_plan: Optional[WorkoutPlan] = None
    meal_plan: Optional[List[MealPlanDay]] = None
    injury_notes: Optional[str] = Field(None, max_length=500)

    # System Tracking
    handoff_history: List[HandoffLog] = Field(default_factory=list)
    progress_history: List[ProgressLog] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

    # ----------- Validators ------------

    @field_validator('goal_deadline')
    @classmethod
    def validate_deadline(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            datetime.fromisoformat(v)
        return v

    @field_validator('medical_conditions')
    @classmethod
    def validate_medical_conditions(cls, v: List[MedicalCondition]) -> List[MedicalCondition]:
        if MedicalCondition.NONE in v and len(v) > 1:
            raise ValueError("Cannot have 'none' with other medical conditions")
        return v

    @field_validator('food_allergies', mode='before')
    @classmethod
    def normalize_allergies(cls, v: List[str]) -> List[str]:
        return [allergy.lower().strip() for allergy in v]

    # ----------- Methods ------------

    def add_progress_update(
        self,
        event_type: Literal["goal_update", "measurement", "note", "system"],
        description: str,
        metric: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[str] = None
    ) -> None:
        self.progress_history.append(
            ProgressLog(
                event_type=event_type,
                description=description,
                metric=metric,
                value=value,
                unit=unit
            )
        )
        self._update_timestamp()

    def log_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: Optional[str] = None,
        context_snapshot: Optional[Dict] = None
    ) -> None:
        self.handoff_history.append(
            HandoffLog(
                from_agent=from_agent,
                to_agent=to_agent,
                reason=reason,
                context_snapshot=context_snapshot or self.get_snapshot()
            )
        )
        self._update_timestamp()

    def get_snapshot(self) -> Dict:
        return {
            "goal": {
                "type": self.goal_type,
                "target": self.goal_target,
                "unit": self.goal_unit,
                "deadline": self.goal_deadline
            },
            "diet": {
                "preference": self.dietary_preference,
                "allergies": self.food_allergies
            },
            "medical": {
                "conditions": self.medical_conditions,
                "injuries": self.injury_notes
            },
            "last_updated": self.last_updated
        }

    def clear_session_data(self) -> None:
        self.goal_type = None
        self.goal_target = None
        self.goal_unit = None
        self.goal_deadline = None
        self.dietary_preference = None
        self.food_allergies = []
        self.workout_plan = None
        self.meal_plan = None
        self.injury_notes = None
        self.medical_conditions = []
        self._update_timestamp()

    def get_session_duration(self) -> float:
        start = datetime.fromisoformat(self.created_at)
        end = datetime.fromisoformat(self.last_updated)
        return (end - start).total_seconds()

    def _update_timestamp(self) -> None:
        self.last_updated = datetime.now().isoformat()
