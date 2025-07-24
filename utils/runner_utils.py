from typing import AsyncGenerator, Optional, Dict, Any
from context import UserSessionContext
from datetime import datetime

# Agent should have a .name attribute and an async process_message() method
class ConversationRunner:
    """
    Conversation streaming manager for multi-agent Gemini-based chat.
    - Streams responses as user types to agent(s)
    - Handles agent handoff (if agent returns a 'next_agent')
    - Keeps conversation history
    """

    def __init__(
        self,
        starting_agent: Any,  # Your agent class, e.g., WellnessAgent
        context: Optional[UserSessionContext] = None
    ):
        self.current_agent = starting_agent
        self.context = context or UserSessionContext()
        self.handoff_history = []

    async def stream_conversation(
        self,
        user_input: str,
        max_turns: int = 10
    ) -> AsyncGenerator[str, None]:
        """
        Streams the conversation in real time,
        yields responses and logs handoffs live.
        """
        turn_count = 0
        current_input = user_input

        while turn_count < max_turns:
            agent = self.current_agent
            context = self.context

            # Key point: process_message yields text (or use return if not streaming)
            response_gen = agent.process_message(current_input, context)
            # If it's an async generator, stream as chunks, else treat as full reply.
            if hasattr(response_gen, "__aiter__"):
                async for reply in response_gen:
                    yield reply
            else:
                # If your agent returns response, not yields
                reply = await response_gen
                yield reply

            # --- Example: agent "handoff"
            # If you use a pattern (like .next_agent, or agent returns a new_agent)
            # insert your own handoff logic here if needed.
            if hasattr(agent, "next_agent") and agent.next_agent:
                self._log_handoff(agent.next_agent)
                yield f"\n[→ Switching to {agent.next_agent.name}]\n"
                self.current_agent = agent.next_agent
                # If agent.next_agent expects context, set as needed.
                if hasattr(self.current_agent, "set_context"):
                    self.current_agent.set_context(self.context)
                # next agent will handle next turn
            else:
                break  # No more handoffs; end

            turn_count += 1

    def _log_handoff(self, new_agent: Any) -> None:
        """
        Log agent transitions for audit and traceability.
        """
        self.handoff_history.append({
            "timestamp": datetime.now().isoformat(),
            "from": getattr(self.current_agent, "name", str(self.current_agent)),
            "to": getattr(new_agent, "name", str(new_agent)),
            "context": self.context.model_dump() \
                            if hasattr(self.context, "model_dump") else str(self.context)
        })
        if hasattr(self.context, "log_handoff"):
            self.context.log_handoff(
                from_agent=getattr(self.current_agent, "name", str(self.current_agent)),
                to_agent=getattr(new_agent, "name", str(new_agent)),
                reason=f"Handoff at {datetime.now().isoformat()}"
            )

# --- Simple functional streaming utility for your Gemini agents

async def gemini_stream_conversation(
    agent: Any,
    user_input: str,
    context: UserSessionContext
) -> AsyncGenerator[str, None]:
    """
    Stateless streaming for Gemini-based agent (single-turn, yields response chunks).
    Args:
        agent: Any Gemini-based agent with async process_message(user_input, context)
        user_input: The user's input message
        context: UserSessionContext
    Yields:
        Streaming string chunks (can be piped to CLI, API, or UI)
    """
    response_gen = agent.process_message(user_input, context)
    if hasattr(response_gen, "__aiter__"):
        async for chunk in response_gen:
            yield chunk
    else:
        reply = await response_gen
        yield reply
