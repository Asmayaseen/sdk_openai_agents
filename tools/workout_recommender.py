# Standard Library Imports
from datetime import datetime
from typing import Dict, List, Optional, Literal
import logging

# Third-party Imports
from pydantic import BaseModel, Field, field_validator
from openai_agents import tool

# Local Imports
from ..context import UserSessionContext
from ..guardrails import WorkoutPlanOutput, InjuryInput

# Configure logging
logger = logging.getLogger(__name__)

class Exercise(BaseModel):
    """Structured exercise with optional modifications and equipment requirements."""
    name: str = Field(..., min_length=3, description="Name of the exercise")
    description: str = Field(..., description="How to perform the exercise")
    modifications: Optional[List[str]] = Field(
        default=None,
        description="Alternative options for users with injuries"
    )
    equipment: List[str] = Field(
        default_factory=list,
        description="Required equipment (e.g., dumbbells, mat)"
    )
    target_muscles: List[str] = Field(
        default_factory=list,
        description="Primary muscle groups targeted"
    )

class WorkoutDay(BaseModel):
    """Represents a single day in a workout plan."""
    focus: Literal["Cardio", "Strength", "Flexibility", "Recovery"] = Field(
        ..., description="Primary focus of the workout"
    )
    exercises: List[Exercise] = Field(
        ..., min_items=1, description="List of exercises for the day"
    )
    duration: str = Field(
        ..., description="Duration of the workout (e.g., '30 mins')"
    )
    intensity: Literal["light", "moderate", "high"] = Field(
        default="moderate", description="Relative intensity of the workout"
    )

class WorkoutDatabase:
    """Static class that provides pre-defined workout templates with injury support."""

    BEGINNER: Dict[str, WorkoutDay] = {
        "Monday": WorkoutDay(
            focus="Cardio",
            exercises=[
                Exercise(
                    name="Brisk Walking",
                    description="30 minutes of brisk walking at a moderate pace.",
                    equipment=["Comfortable shoes"],
                    target_muscles=["Legs", "Core"]
                )
            ],
            duration="30 mins"
        ),
        "Tuesday": WorkoutDay(
            focus="Strength",
            exercises=[
                Exercise(
                    name="Bodyweight Squats",
                    description="Perform 3 sets of 10 reps.",
                    modifications=["Chair squats", "Wall squats"],
                    target_muscles=["Quads", "Glutes"]
                ),
                Exercise(
                    name="Push-ups",
                    description="Perform 3 sets of 8 reps.",
                    modifications=["Knee push-ups", "Wall push-ups"],
                    target_muscles=["Chest", "Triceps"]
                )
            ],
            duration="25 mins"
        )
    }

    INTERMEDIATE: Dict[str, WorkoutDay] = {
        "Monday": WorkoutDay(
            focus="Cardio",
            exercises=[
                Exercise(
                    name="Interval Running",
                    description="Sprint for 45 seconds, walk for 90 seconds. Repeat 8 times.",
                    equipment=["Running shoes"],
                    target_muscles=["Full body"]
                )
            ],
            duration="30 mins",
            intensity="high"
        )
    }

    @classmethod
    def get_workouts(cls, level: str) -> Dict[str, WorkoutDay]:
        """
        Retrieves workouts by experience level.

        Args:
            level: User level - beginner, intermediate, or advanced.

        Returns:
            Dictionary of workout days. Defaults to beginner level if not matched.
        """
        levels = {
            "beginner": cls.BEGINNER,
            "intermediate": cls.INTERMEDIATE,
            "advanced": cls.INTERMEDIATE  # TODO: Add separate advanced workouts
        }
        return levels.get(level.lower(), cls.BEGINNER)

    @classmethod
    def modify_for_injury(cls, workouts: Dict[str, WorkoutDay], injury: str) -> Dict[str, WorkoutDay]:
        """
        Modifies workouts to accommodate user injuries.

        Args:
            workouts: Original workout dictionary.
            injury: Injury notes from the user (e.g., 'knee pain').

        Returns:
            Modified dictionary with safe alternatives where needed.
        """
        modified = workouts.copy()

        if "knee" in injury.lower():
            for day, plan in modified.items():
                updated_exercises = []
                for ex in plan.exercises:
                    if any(keyword in ex.name.lower() for keyword in ["squat", "lunge", "jump"]):
                        new_ex = ex.copy()
                        new_ex.modifications = [
                            "Seated leg press",
                            "Straight leg raises",
                            "Swimming"
                        ]
                        updated_exercises.append(new_ex)
                    else:
                        updated_exercises.append(ex)
                plan.exercises = updated_exercises
                modified[day] = plan

        return modified

@tool
async def recommend_workout(
    goal: str,
    experience: Literal["beginner", "intermediate", "advanced"] = "beginner",
    injury_notes: Optional[str] = None,
    context: Optional[UserSessionContext] = None
) -> WorkoutPlanOutput:
    """
    Generates a structured weekly workout plan based on user goals, experience, and injuries.

    Args:
        goal: Fitness goal (e.g., 'weight loss', 'muscle gain').
        experience: User fitness level - beginner, intermediate, or advanced.
        injury_notes: Any known physical limitations.
        context: Optional session context to persist data.

    Returns:
        WorkoutPlanOutput: Structured workout plan with daily schedules and safety adjustments.
    """
    logger.info(f"Generating workout for goal='{goal}', level='{experience}'")

    try:
        # Process injury notes through schema validation
        if injury_notes:
            validated_injury = InjuryInput(notes=injury_notes).notes
            if context:
                context.injury_notes = validated_injury
                logger.debug(f"Stored injury: {validated_injury}")
        else:
            validated_injury = None

        # Fetch base workouts based on experience
        workouts = WorkoutDatabase.get_workouts(experience)

        # Apply modifications if injury present
        if validated_injury:
            workouts = WorkoutDatabase.modify_for_injury(workouts, validated_injury)
            logger.info("Workout modified for injury adjustments.")

        # Update user session context
        if context:
            context.workout_plan = {day: plan.model_dump() for day, plan in workouts.items()}
            context.update_progress(
                f"Generated {experience} workout plan",
                metric="workouts",
                value=len(workouts)
            )
            logger.debug("Context updated with workout plan.")

        # Prepare and return structured output
        return WorkoutPlanOutput(
            schedule={day: plan.model_dump() for day, plan in workouts.items()}
        )

    except Exception as e:
        logger.error(f"Workout plan generation failed: {str(e)}")
        raise ValueError(f"Workout plan generation failed: {str(e)}")
