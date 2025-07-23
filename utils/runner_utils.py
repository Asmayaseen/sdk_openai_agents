# utils/runner_utils.py

from typing import AsyncGenerator, Optional, Union
from openai_agents.runner import Runner, Step  
from ..agent import HealthWellnessAgent
from ..context import UserSessionContext
from datetime import datetime

class ConversationRunner:
    """
    Enhanced conversation manager with streaming and handoff support.
    
    Features:
    - Real-time response streaming
    - Automatic agent handoffs
    - Conversation history tracking
    - Works in both streaming and non-streaming modes
    """
    
    def __init__(
        self, 
        starting_agent: HealthWellnessAgent,
        context: Optional[UserSessionContext] = None
    ):
        self.current_agent = starting_agent
        self.context = context or UserSessionContext()
        self.handoff_history = []
        self.current_agent.set_context(self.context)

    async def stream_conversation(
        self, 
        user_input: str,
        max_turns: int = 10
    ) -> AsyncGenerator[Union[str, Step], None]:
        """
        Stream conversation with automatic handoff handling.
        
        Args:
            user_input (str): User's initial input.
            max_turns (int): Maximum allowed turns in a session.
        
        Yields:
            Union[str, Step]: Streamed agent responses or raw step object.
        """
        turn_count = 0
        current_input = user_input
        
        while turn_count < max_turns:
            async for step in Runner.stream(
                starting_agent=self.current_agent,
                input=current_input,
                context=self.context
            ):
                if step.pretty_output:
                    yield step.pretty_output
                
                if step.next_agent:
                    self._log_handoff(step.next_agent)
                    self.current_agent = step.next_agent
                    self.current_agent.set_context(self.context)
                    yield f"\n[Handoff to {step.next_agent.name}]\n"
                    
            turn_count += 1

    async def run_to_completion(
        self,
        user_input: str,
        max_turns: int = 10
    ) -> str:
        """
        Run full conversation and collect output.
        
        Args:
            user_input (str): User's starting message.
            max_turns (int): Max number of steps to run.
        
        Returns:
            str: Full conversation transcript.
        """
        full_conversation = []
        async for response in self.stream_conversation(user_input, max_turns):
            full_conversation.append(str(response))
        return "\n".join(full_conversation)

    def _log_handoff(self, new_agent: HealthWellnessAgent) -> None:
        """
        Internal helper to log agent transitions.
        
        Args:
            new_agent (HealthWellnessAgent): Next agent in flow.
        """
        handoff_record = {
            "timestamp": datetime.now().isoformat(),
            "from": self.current_agent.name,
            "to": new_agent.name,
            "context": self.context.dict()
        }
        self.handoff_history.append(handoff_record)
        self.context.log_handoff(new_agent.name)


# --- Functional Utility Version ---

async def stream_conversation(
    agent: HealthWellnessAgent,
    user_input: str,
    context: UserSessionContext,
    max_turns: int = 5
) -> AsyncGenerator[Union[str, Step], None]:
    """
    Lightweight stateless streamer, good for short conversations.
    
    Args:
        agent (HealthWellnessAgent): Starting agent.
        user_input (str): Initial user message.
        context (UserSessionContext): Current session context.
        max_turns (int): Max loop iterations.
    
    Yields:
        Union[str, Step]: Response or agent Step.
    """
    current_agent = agent
    for _ in range(max_turns):
        async for step in Runner.stream(
            starting_agent=current_agent,
            input=user_input,
            context=context
        ):
            yield step

            if step.next_agent:
                current_agent = step.next_agent
                yield f"\n[Switching to {current_agent.name}]\n"
