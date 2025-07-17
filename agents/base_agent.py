from openai_agents import Assistant  # ✅ Correct import here
from typing import Optional, Dict, Any, List, Type
from pydantic import BaseModel
from datetime import datetime
from ..context import UserSessionContext
from ..tools.base_tool import BaseTool


class BaseAgent(Assistant):
    """
    Base class for AI agents with context management, handoff tracking,
    lifecycle hooks, and support for tools.
    """

    def __init__(
        self,
        name: str,
        description: str,
        tools: Optional[List[Type[BaseTool]]] = None,
        **kwargs: Any
    ):
        super().__init__(
            name=name,
            description=description,
            tools=[tool() for tool in (tools or [])],
            **kwargs
        )
        self._context: Optional[UserSessionContext] = None
        self._handoff_history: List[Dict[str, Any]] = []
        self._last_activity: Optional[datetime] = None

    @property
    def context(self) -> Optional[UserSessionContext]:
        return self._context

    @context.setter
    def context(self, value: UserSessionContext) -> None:
        if not isinstance(value, UserSessionContext):
            raise TypeError("Context must be of type UserSessionContext")
        self._context = value
        self._update_activity()

    def _update_activity(self) -> None:
        self._last_activity = datetime.now()

    async def on_handoff(
        self,
        target_agent_name: str,
        reason: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        if not target_agent_name.strip():
            raise ValueError("Target agent name cannot be empty")

        handoff_record = {
            "timestamp": datetime.now().isoformat(),
            "from_agent": self.name,
            "to_agent": target_agent_name,
            "reason": reason,
            "metadata": kwargs,
            "context_snapshot": self.context.model_dump() if self.context else None
        }

        self._handoff_history.append(handoff_record)

        if self.context:
            self.context.log_handoff(
                from_agent=self.name,
                to_agent=target_agent_name,
                reason=reason
            )
            self.context.add_progress_update(
                event_type="handoff",
                description=f"Handoff initiated to {target_agent_name}",
                metric="agent_handoff",
                value=len(self._handoff_history)
            )

    def get_handoff_history(self) -> List[Dict[str, Any]]:
        return [record.copy() for record in self._handoff_history]

    async def before_run(self, input: str) -> None:
        self._update_activity()
        if self.context:
            self.context.add_progress_update(
                event_type="input",
                description=f"Processing input: {input[:50]}..." if len(input) > 50 else f"Processing input: {input}",
                metric="user_input",
                value=len(input)
            )

    async def after_run(self, output: str) -> None:
        self._update_activity()
        if self.context:
            self.context.add_progress_update(
                event_type="output",
                description=f"Generated response: {output[:50]}..." if len(output) > 50 else f"Generated response: {output}",
                metric="agent_response",
                value=len(output)
            )

    def get_last_activity(self) -> Optional[datetime]:
        return self._last_activity


class AgentConfig(BaseModel):
    name: str
    description: str
    tools: List[str] = []
