# openai_agents/runner.py

from typing import AsyncGenerator, Any, Dict, Optional
from openai_agents.agent import Agent


class Step:
    """
    Represents a step in the agent's conversation.
    """
    def __init__(self, output: str, is_final: bool = False):
        self.pretty_output = output
        self.is_final = is_final


class RunContextWrapper:
    """
    Optional: Wraps agent run context with additional metadata or transformations.
    You can customize this as needed.
    """

    def __init__(self, context: Any, user_id: Optional[str] = None):
        self.context = context
        self.user_id = user_id

    def with_user(self, user_id: str) -> 'RunContextWrapper':
        self.user_id = user_id
        return self

    def unwrap(self) -> Any:
        # Return context as-is or inject user_id into it if needed
        if isinstance(self.context, dict):
            self.context["user_id"] = self.user_id
        return self.context


class Runner:
    """
    Responsible for managing agent execution in streaming or non-streaming mode.
    """

    @staticmethod
    async def stream(
        starting_agent: Agent,
        input: str,
        context: Any
    ) -> AsyncGenerator[Step, None]:
        """
        Stream agent responses one at a time using async generator.
        """
        async for output in starting_agent.stream_response(input, context):
            yield Step(output, is_final=True)  # Assume single step for now

    @staticmethod
    async def run(
        agent: Agent,
        input: str,
        context: Any
    ) -> Step:
        """
        Run the agent without streaming, return final Step.
        """
        response = await agent.run(input, context)
        return Step(response, is_final=True)
