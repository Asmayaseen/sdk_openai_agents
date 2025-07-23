from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
import logging
from openai import AsyncOpenAI

from context import UserSessionContext
from config import config

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all health and wellness agents."""
    
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.context: Optional[UserSessionContext] = None
        
        # Initialize OpenAI client
        if config.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning(f"No OpenAI API key provided for agent {name}")

    def set_context(self, context: UserSessionContext) -> None:
        """Set the user session context."""
        self.context = context

    @abstractmethod
    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process a user message and yield response chunks."""
        pass

    async def should_handoff(self, message: str) -> Optional[str]:
        """Determine if this agent should hand off to another agent."""
        # Default implementation - can be overridden
        return None

    async def get_openai_response(self, message: str, max_tokens: int = None) -> AsyncGenerator[str, None]:
        """Get streaming response from OpenAI."""
        if not self.client:
            yield "I'm sorry, I'm currently unable to provide AI-powered responses. Please check the configuration."
            return

        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history
        if self.context and self.context.conversation_history:
            for msg in self.context.get_recent_messages(10):
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        messages.append({"role": "user", "content": message})

        try:
            stream = await self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                max_tokens=max_tokens or config.MAX_TOKENS,
                temperature=config.DEFAULT_TEMPERATURE,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI API error in {self.name}: {e}")
            yield f"I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"

    def build_context_prompt(self, message: str) -> str:
        """Build a context-aware prompt."""
        if not self.context:
            return message
        
        context_info = []
        
        if self.context.goal_type:
            context_info.append(f"User Goal: {self.context.goal_type.value}")
        
        if self.context.dietary_preference:
            context_info.append(f"Dietary Preference: {self.context.dietary_preference.value}")
        
        if self.context.medical_conditions:
            conditions = [c.value for c in self.context.medical_conditions if c.value != "none"]
            if conditions:
                context_info.append(f"Medical Conditions: {', '.join(conditions)}")
        
        if self.context.injury_notes:
            context_info.append(f"Injury Notes: {self.context.injury_notes}")
        
        if self.context.food_allergies:
            context_info.append(f"Food Allergies: {', '.join(self.context.food_allergies)}")
        
        context_str = "\n".join(context_info) if context_info else ""
        
        return f"""
        [User Context]
        {context_str}
        
        [User Message]
        {message}
        """
