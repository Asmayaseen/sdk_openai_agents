# Standard Library Imports
from datetime import datetime
from typing import Dict, Optional, Union, Literal, Any
import re
import logging

# Third-party Imports
from pydantic import BaseModel, Field, field_validator

# Local Imports
from context import UserSessionContext

logger = logging.getLogger(__name__)


class ProgressTrackerTool:
    """
    📊 Progress Tracker Tool

    Description:
    Tracks user progress on different health metrics like weight, body fat %, heart rate, etc.
    Validates input, saves updates in the user session context, and returns structured results.

    Features:
    - Input validation (e.g., positive values, allowed units, correct metric names)
    - Stores progress history and latest values
    - Records timestamp and optional user notes
    - Integrates with session state (UserSessionContext)
    """

    @classmethod
    def name(cls) -> str:
        return "progress_tracker"

    @classmethod
    def description(cls) -> str:
        return (
            "Tracks and validates user progress updates across various metrics. "
            "Maintains complete history in session context."
        )

    # -------------------- Input Schema --------------------
    class InputModel(BaseModel):
        metric: str = Field(
            ...,
            min_length=2,
            max_length=50,
            description="The metric being tracked (e.g., weight, heart_rate, steps)"
        )
        value: float = Field(
            ...,
            gt=0,
            description="The measurement value (must be greater than 0)"
        )
        unit: Literal["kg", "lbs", "cm", "in", "%", "bpm", "kcal", ""] = Field(
            "",
            description="Optional unit for the value (e.g., kg, %, bpm)"
        )
        notes: Optional[str] = Field(
            None,
            max_length=200,
            description="Optional notes related to this measurement"
        )
        timestamp: Optional[datetime] = Field(
            None,
            description="When the measurement was recorded (defaults to now)"
        )

        @field_validator('metric')
        @classmethod
        def validate_metric(cls, v: str) -> str:
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_ -]*$", v):
                raise ValueError(
                    "Metric must contain only letters, numbers, spaces, underscores or dashes."
                )
            return v.strip().lower()

    # -------------------- Output Schema --------------------
    class OutputModel(BaseModel):
        success: bool = Field(..., description="Indicates whether tracking was successful")
        message: str = Field(..., description="Status or error message")
        data: Optional[Dict[str, Any]] = Field(None, description="Validated tracking data")

    # -------------------- Tool Interface Methods --------------------
    @classmethod
    def input_schema(cls) -> type[BaseModel]:
        return cls.InputModel

    @classmethod
    def output_schema(cls) -> type[BaseModel]:
        return cls.OutputModel

    async def execute(
        self,
        update: Dict[str, Union[str, float, datetime, None]],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Union[bool, str, Dict[str, Any]]]:
        """
        Executes progress tracking tool.
        
        Parameters:
            update (dict): A dictionary with keys - metric, value, unit, notes, timestamp.
            context (UserSessionContext, optional): Stores user state/history.

        Returns:
            dict: Includes success flag, status message, and validated data.
        """
        logger.info("🔄 Tracking progress update...")

        try:
            validated_update = self.InputModel(**update)

            # Set current time if timestamp missing
            if validated_update.timestamp is None:
                validated_update.timestamp = datetime.now()

            if context:
                self._update_context(context, validated_update)
                logger.debug(f"✅ Context updated for metric: {validated_update.metric}")

            return {
                "success": True,
                "message": (
                    f"{validated_update.metric.capitalize()} updated to "
                    f"{validated_update.value}{validated_update.unit}"
                ),
                "data": validated_update.model_dump()
            }

        except ValueError as ve:
            logger.warning(f"⚠️ Validation failed: {ve}")
            return {
                "success": False,
                "message": f"Invalid progress data: {str(ve)}",
                "data": None
            }
        except Exception as e:
            logger.error(f"❌ Error in tracking: {e}")
            return {
                "success": False,
                "message": f"Failed to track progress: {str(e)}",
                "data": None
            }

    # -------------------- Context Update Helper --------------------
    def _update_context(self, context: UserSessionContext, update: InputModel) -> None:
        """
        Updates the user's session context with the latest progress and history.
        """
        # Add to progress history using the context method
        context.add_progress_update(
            metric=update.metric,
            value=update.value,
            unit=update.unit,
            notes=update.notes
        )

        # Log the progress to context
        context.update_progress(
            f"{update.metric} update",
            metric=update.metric,
            value=update.value,
            unit=update.unit
        )
