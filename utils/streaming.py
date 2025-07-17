# utils/streaming.py

from typing import AsyncGenerator
from openai_agents.runner import Runner
from openai_agents.agent import Agent  
from ..context import UserSessionContext


async def stream_conversation(
    agent: Agent,
    user_input: str,
    context: UserSessionContext,
    max_turns: int = 5
) -> AsyncGenerator[str, None]:
    """
    Stream responses from an agent in real-time, supporting up to `max_turns`.

    Args:
        agent (Agent): The starting agent handling the conversation.
        user_input (str): Initial user message or query.
        context (UserSessionContext): Shared context for conversation and memory.
        max_turns (int): Maximum number of conversation turns to execute.

    Yields:
        str: Agent's streamed response text (pretty_output).
    """
    turn_count = 0
    current_input = user_input

    while turn_count < max_turns:
        async for step in Runner.stream(
            starting_agent=agent,
            input=current_input,
            context=context
        ):
            if step.pretty_output:
                yield step.pretty_output

            if step.is_final:
                return  # Stop if conversation naturally ends
        
        turn_count += 1

        # 🔒 For demo or stateless use, we break after 1 turn.
        break
