from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Generic, TypeVar

# Define a generic type variable
T = TypeVar("T")

class Agent(ABC, Generic[T]):
    """
    Abstract base class for all agents.
    """

    def __init__(self, name: str, system_prompt: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.config = config or {}

    @abstractmethod
    async def run(self, user_input: str, context: T) -> str:
        """
        Run the agent logic for a given input and return the response.
        Must be implemented by subclasses.
        """
        pass

    async def stream_response(self, user_input: str, context: T):
        """
        Optional: Override for streaming responses.
        """
        response = await self.run(user_input, context)
        yield response
