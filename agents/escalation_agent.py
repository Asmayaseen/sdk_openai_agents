from .base_agent import BaseAgent
from openai import Assistant
from typing import Dict, Optional
from ..context import UserSessionContext, GoalType
from datetime import datetime, timedelta

class EscalationAgent(BaseAgent):
    """Agent for handling requests to speak with human coaches"""
    
    def __init__(self):
        super().__init__(
            name="EscalationAgent",
            description="Handles requests to speak with human coaches or support",
            tools=[self.handle_escalation]
        )
        self.available_coaches = [
            {"name": "Alex", "specialty": "Weight Loss", "availability": "Weekdays 9-5"},
            {"name": "Jordan", "specialty": "Strength Training", "availability": "Weekends"},
            {"name": "Taylor", "specialty": "General Wellness", "availability": "Weekdays 10-6"}
        ]
        self._scheduled_sessions: Dict[str, Dict] = {}

    @Assistant.tool
    async def handle_escalation(
        self, 
        reason: str, 
        context: Optional[UserSessionContext] = None
    ) -> str:
        """
        Handles escalation to human coach by scheduling a callback.
        
        Args:
            reason: Reason for requesting human coach
            context: User session context
            
        Returns:
            str: Confirmation and next steps
        """
        # Validate input
        if not reason or not isinstance(reason, str):
            return "Please provide a valid reason for requesting a human coach"
        
        # Update context
        if context:
            context.add_progress_update(
                event_type="note",
                description=f"Requested human coach due to: {reason}",
                metric="escalation_request"
            )
            context.log_handoff(
                from_agent=self.name,
                to_agent="Human Coach",
                reason=reason
            )

        # Determine specialty based on user's goal
        specialty = "General Wellness"
        if context and context.goal_type:
            if context.goal_type == GoalType.WEIGHT_LOSS:
                specialty = "Weight Loss"
            elif context.goal_type == GoalType.WEIGHT_GAIN or context.goal_type == GoalType.MUSCLE_BUILDING:
                specialty = "Strength Training"
        
        # Match coach based on specialty
        available = [c for c in self.available_coaches if c["specialty"] == specialty]
        if not available:
            available = self.available_coaches
        
        coach = available[0]
        session_id = f"session_{len(self._scheduled_sessions)+1}"

        # Store session info
        self._scheduled_sessions[session_id] = {
            "coach": coach["name"],
            "specialty": coach["specialty"],
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "user_context": context.model_dump() if context else None
        }

        # Calculate schedule time
        schedule_time = self._get_next_available_time(coach["availability"])

        return (
            f"I've scheduled a callback with coach {coach['name']} "
            f"(specialty: {coach['specialty']}).\n"
            f"They'll contact you on {schedule_time}.\n"
            f"Reason noted: {reason}\n"
            f"Reference ID: {session_id}"
        )

    def _get_next_available_time(self, availability: str) -> str:
        """Calculate next available time based on coach's schedule"""
        now = datetime.now()

        if "Weekdays" in availability:
            if now.weekday() < 5:
                return f"today between {availability.split()[-1]}"
            days_until_weekday = (7 - now.weekday()) % 7 + 1
            next_day = now + timedelta(days=days_until_weekday)
            return f"{next_day.strftime('%A')} between {availability.split()[-1]}"
        else:  # Weekends
            if now.weekday() >= 5:
                return "today"
            days_until_weekend = (5 - now.weekday())
            next_day = now + timedelta(days=days_until_weekend)
            return f"{next_day.strftime('%A')}"

    def get_scheduled_sessions(self) -> Dict[str, Dict]:
        """Get all scheduled coaching sessions"""
        return {k: v.copy() for k, v in self._scheduled_sessions.items()}
