# openai_agents/runner.py

from typing import AsyncGenerator, Any, Dict
from openai_agents.agent import Agent


class Step:
    """
    Represents a step in the agent's conversation.
    """
    def __init__(self, output: str, is_final: bool = False):
        self.pretty_output = output
        self.is_final = is_final


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
            yield Step(output, is_final=True)  # For simplicity, we assume one step

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
