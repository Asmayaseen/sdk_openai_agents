# Standard Library Imports
from datetime import datetime
from typing import Dict, List, Optional, Literal
from typing import Dict, List, Optional, Literal, Any
import logging

# Third-party Imports
from pydantic import BaseModel, Field, field_validator

# Local Imports
from context import UserSessionContext

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
        ),
        "Wednesday": WorkoutDay(
            focus="Recovery",
            exercises=[
                Exercise(
                    name="Gentle Yoga",
                    description="Light stretching and relaxation poses.",
                    equipment=["Yoga mat"],
                    target_muscles=["Full body"]
                )
            ],
            duration="20 mins",
            intensity="light"
        ),
        "Thursday": WorkoutDay(
            focus="Cardio",
            exercises=[
                Exercise(
                    name="Light Cycling",
                    description="Easy-paced cycling for 25 minutes.",
                    equipment=["Bicycle or stationary bike"],
                    target_muscles=["Legs", "Core"]
                )
            ],
            duration="25 mins"
        ),
        "Friday": WorkoutDay(
            focus="Strength",
            exercises=[
                Exercise(
                    name="Planks",
                    description="Hold plank position for 30 seconds, repeat 3 times.",
                    modifications=["Knee planks", "Wall planks"],
                    target_muscles=["Core", "Shoulders"]
                ),
                Exercise(
                    name="Lunges",
                    description="Perform 3 sets of 8 reps each leg.",
                    modifications=["Stationary lunges", "Chair-assisted lunges"],
                    target_muscles=["Quads", "Glutes", "Hamstrings"]
                )
            ],
            duration="20 mins"
        ),
        "Saturday": WorkoutDay(
            focus="Flexibility",
            exercises=[
                Exercise(
                    name="Full Body Stretching",
                    description="Comprehensive stretching routine for all major muscle groups.",
                    equipment=["Yoga mat"],
                    target_muscles=["Full body"]
                )
            ],
            duration="30 mins",
            intensity="light"
        ),
        "Sunday": WorkoutDay(
            focus="Recovery",
            exercises=[
                Exercise(
                    name="Leisurely Walk",
                    description="Gentle walk in nature or around the neighborhood.",
                    equipment=["Comfortable shoes"],
                    target_muscles=["Legs"]
                )
            ],
            duration="20 mins",
            intensity="light"
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
        ),
        "Tuesday": WorkoutDay(
            focus="Strength",
            exercises=[
                Exercise(
                    name="Weighted Squats",
                    description="4 sets of 12 reps with dumbbells.",
                    equipment=["Dumbbells"],
                    target_muscles=["Quads", "Glutes"]
                ),
                Exercise(
                    name="Push-up Variations",
                    description="3 sets of 15 standard push-ups.",
                    modifications=["Diamond push-ups", "Wide-grip push-ups"],
                    target_muscles=["Chest", "Triceps", "Shoulders"]
                )
            ],
            duration="40 mins"
        ),
        "Wednesday": WorkoutDay(
            focus="Cardio",
            exercises=[
                Exercise(
                    name="Circuit Training",
                    description="High-intensity circuit with burpees, jumping jacks, and mountain climbers.",
                    equipment=["None"],
                    target_muscles=["Full body"]
                )
            ],
            duration="35 mins",
            intensity="high"
        )
    }

    ADVANCED: Dict[str, WorkoutDay] = {
        "Monday": WorkoutDay(
            focus="Strength",
            exercises=[
                Exercise(
                    name="Deadlifts",
                    description="5 sets of 5 reps with progressive loading.",
                    equipment=["Barbell", "Weight plates"],
                    target_muscles=["Hamstrings", "Glutes", "Back"]
                ),
                Exercise(
                    name="Pull-ups",
                    description="4 sets to failure.",
                    modifications=["Assisted pull-ups", "Negative pull-ups"],
                    equipment=["Pull-up bar"],
                    target_muscles=["Lats", "Biceps"]
                )
            ],
            duration="60 mins",
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
            "advanced": cls.ADVANCED
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
        modified = {}
        
        for day, plan in workouts.items():
            updated_exercises = []
            for ex in plan.exercises:
                new_ex = Exercise(**ex.model_dump())  # Create a copy
                
                # Modify based on injury type
                if "knee" in injury.lower():
                    if any(keyword in ex.name.lower() for keyword in ["squat", "lunge", "jump"]):
                        new_ex.modifications = new_ex.modifications or []
                        new_ex.modifications.extend([
                            "Seated leg press",
                            "Straight leg raises",
                            "Swimming"
                        ])
                        new_ex.description += " (Modified for knee injury - use alternatives)"
                
                elif "back" in injury.lower():
                    if any(keyword in ex.name.lower() for keyword in ["deadlift", "row", "lift"]):
                        new_ex.modifications = new_ex.modifications or []
                        new_ex.modifications.extend([
                            "Light stretching",
                            "Swimming",
                            "Walking"
                        ])
                        new_ex.description += " (Modified for back injury - focus on gentle movements)"
                
                elif "shoulder" in injury.lower():
                    if any(keyword in ex.name.lower() for keyword in ["push", "pull", "press"]):
                        new_ex.modifications = new_ex.modifications or []
                        new_ex.modifications.extend([
                            "Lower body exercises",
                            "Core work",
                            "Walking"
                        ])
                        new_ex.description += " (Modified for shoulder injury - avoid overhead movements)"
                
                updated_exercises.append(new_ex)
            
            # Create new workout day with modified exercises
            modified[day] = WorkoutDay(
                focus=plan.focus,
                exercises=updated_exercises,
                duration=plan.duration,
                intensity=plan.intensity
            )

        return modified

class WorkoutRecommenderTool:
    """Tool for generating personalized workout recommendations."""

    @classmethod
    def name(cls) -> str:
        return "workout_recommender"

    @classmethod
    def description(cls) -> str:
        return "Generates personalized workout plans based on fitness level, goals, and limitations"

    class InputModel(BaseModel):
        goal: str = Field(..., description="Fitness goal (e.g., 'weight loss', 'muscle gain')")
        experience: Literal["beginner", "intermediate", "advanced"] = Field(
            default="beginner",
            description="User fitness level"
        )
        injury_notes: Optional[str] = Field(
            None,
            description="Any known physical limitations"
        )

    class OutputModel(BaseModel):
        success: bool = Field(..., description="Whether plan generation was successful")
        message: str = Field(..., description="Status message")
        schedule: Optional[Dict[str, Any]] = Field(None, description="Weekly workout schedule")

    async def execute(
        self,
        goal: str,
        experience: Literal["beginner", "intermediate", "advanced"] = "beginner",
        injury_notes: Optional[str] = None,
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Generates a structured weekly workout plan based on user goals, experience, and injuries.

        Args:
            goal: Fitness goal (e.g., 'weight loss', 'muscle gain').
            experience: User fitness level - beginner, intermediate, or advanced.
            injury_notes: Any known physical limitations.
            context: Optional session context to persist data.

        Returns:
            Dict with success status, message, and workout schedule.
        """
        logger.info(f"Generating workout for goal='{goal}', level='{experience}'")

        try:
            # Validate injury notes if provided
            validated_injury = None
            if injury_notes:
                validated_injury = injury_notes.strip()
                if context:
                    context.injury_notes = validated_injury
                    logger.debug(f"Stored injury: {validated_injury}")

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
            return {
                "success": True,
                "message": f"Generated {experience} level workout plan for {goal}",
                "schedule": {day: plan.model_dump() for day, plan in workouts.items()}
            }

        except Exception as e:
            logger.error(f"Workout plan generation failed: {str(e)}")
            return {
                "success": False,
                "message": f"Workout plan generation failed: {str(e)}",
                "schedule": None
            }
