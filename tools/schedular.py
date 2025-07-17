# tools/scheduler.py

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Literal, Any
import logging

from pydantic import BaseModel, Field, field_validator
from openai import tool  

from ..context import UserSessionContext

logger = logging.getLogger(__name__)


class CheckinSchedulerTool:
    """
    Check-in Scheduling Tool

    Features:
    - Validates and parses user preferences
    - Calculates the next check-in datetime
    - Returns a structured schedule output
    - Updates context with schedule data
    """

    @classmethod
    def name(cls) -> str:
        return "checkin_scheduler"

    @classmethod
    def description(cls) -> str:
        return (
            "Schedules recurring progress check-ins based on user preferences. "
            "Validates inputs and calculates next check-in datetime."
        )

    class InputModel(BaseModel):
        """Validated check-in schedule input model"""
        days: str = Field(
            ...,
            description="Comma-separated days (e.g., 'Monday,Wednesday,Friday')"
        )
        time: str = Field(
            ...,
            description="Preferred time in HH:MM format (24-hour)"
        )
        frequency: Literal["weekly", "biweekly", "monthly"] = Field(
            "weekly",
            description="Check-in frequency (weekly/biweekly/monthly)"
        )

        @field_validator('days', mode='before')
        @classmethod
        def validate_days(cls, v: str) -> str:
            valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
            days = [day.strip().capitalize() for day in v.split(',')]
            filtered_days = [day for day in days if day in valid_days]
            if not filtered_days:
                raise ValueError("Must include at least one valid day of the week")
            return ','.join(filtered_days)

        @field_validator('time')
        @classmethod
        def validate_time(cls, v: str) -> str:
            try:
                time.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError("Time must be in HH:MM format (24-hour)")

    class OutputModel(BaseModel):
        """Structured check-in schedule output"""
        days_of_week: List[str] = Field(..., description="List of valid capitalized weekdays")
        reminder_time: str = Field(..., description="Time in HH:MM format")
        frequency: str = Field(..., description="weekly/biweekly/monthly")
        next_checkin: datetime = Field(..., description="Calculated next check-in datetime")
        message: str = Field(..., description="User-friendly schedule message")

    @classmethod
    def input_schema(cls) -> type[BaseModel]:
        return cls.InputModel

    @classmethod
    def output_schema(cls) -> type[BaseModel]:
        return cls.OutputModel

    @tool
    async def execute(
        self,
        preferences: Dict[str, str],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        """
        Executes check-in scheduling logic.
        Validates inputs, calculates next check-in, updates context.
        """
        logger.info("Starting check-in scheduling")

        try:
            validated_input = self.InputModel(**preferences)
            schedule = self._calculate_schedule(validated_input)

            if context:
                self._update_context(context, schedule)

            logger.info(f"Scheduled check-ins: {schedule}")
            return schedule.model_dump()

        except ValueError as e:
            logger.error(f"Failed to schedule check-in: {str(e)}")
            raise ValueError(f"Schedule creation failed: {str(e)}")

    def _calculate_schedule(self, inputs: InputModel) -> OutputModel:
        now = datetime.now()
        reminder_time = time.fromisoformat(inputs.time)
        days = [d.strip().capitalize() for d in inputs.days.split(',')]

        # Calculate next valid check-in date
        next_checkin = None
        for offset in range(7):
            day_candidate = now + timedelta(days=offset)
            if day_candidate.strftime('%A') in days:
                dt_candidate = datetime.combine(day_candidate.date(), reminder_time)
                if dt_candidate > now:
                    next_checkin = dt_candidate
                    break

        if next_checkin is None:
            raise ValueError("Could not find a valid check-in day")

        # Adjust for frequency
        if inputs.frequency == "biweekly":
            next_checkin += timedelta(weeks=1)
        elif inputs.frequency == "monthly":
            next_checkin += timedelta(weeks=3)

        return self.OutputModel(
            days_of_week=days,
            reminder_time=inputs.time,
            frequency=inputs.frequency,
            next_checkin=next_checkin,
            message=f"Scheduled {len(days)} {inputs.frequency} check-ins at {inputs.time}"
        )

    def _update_context(self, context: UserSessionContext, schedule: OutputModel):
        context.update_progress(
            "Created check-in schedule",
            metric="checkins",
            value=f"{len(schedule.days_of_week)}/{schedule.frequency}"
        )

        if not hasattr(context, 'checkin_schedules'):
            context.checkin_schedules = []

        context.checkin_schedules.append({
            "days": schedule.days_of_week,
            "time": schedule.reminder_time,
            "frequency": schedule.frequency,
            "next_checkin": schedule.next_checkin.isoformat()
        })
