from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
import logging
import google.generativeai as genai

from context import UserSessionContext
from config import config

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all health and wellness agents.
       Handles user context, Gemini API connection, and streaming infra.
    """

    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.context: Optional[UserSessionContext] = None

        # Configure Gemini API (ideally done once at app startup)
        if getattr(config, "GEMINI_API_KEY", None):
            genai.configure(api_key=config.GEMINI_API_KEY)
            model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
            self.client = genai.GenerativeModel(model_name=model_name)
        else:
            self.client = None
            logger.warning(f"[Agent: {name}] No Gemini API key provided.")

    def set_context(self, context: UserSessionContext) -> None:
        """Sets session context for the agent (user-specific info, goals, etc)."""
        self.context = context

    @abstractmethod
    async def process_message(self, message: str, *args, **kwargs) -> AsyncGenerator[str, None]:
        """
        Process a user message, streaming response chunks.
        All main agents/tools must implement this method.
        Accepts optional args/kwargs for future flexibility.
        """
        pass

    async def should_handoff(self, message: str) -> Optional[str]:
        """
        Determines if this agent should hand off control to another agent,
        based on message content. Default: None (no handoff).
        """
        return None

    async def get_gemini_response(self, message: str) -> AsyncGenerator[str, None]:
        """
        Streams response from the Gemini API to the UI/runner.
        Handles API key missing and error cases gracefully.
        """
        if not self.client:
            yield "AI is not available. Please check your API key configuration."
            return

        full_prompt = self.build_context_prompt(message)
        try:
            # Gemini's Python SDK is synchronous; run in executor to avoid blocking
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, lambda: self.client.generate_content(full_prompt, stream=True)
            )
            for chunk in response:
                if chunk and hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini API error in {self.name}: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"

    def build_context_prompt(self, message: str) -> str:
        """
        Builds a full prompt for Gemini including system instructions,
        user context, and the current message.
        """
        if not self.context:
            return f"{self.system_prompt}\n\nUser: {message}"

        context_info = []

        if getattr(self.context, "goal_type", None):
            value = getattr(self.context.goal_type, "value", str(self.context.goal_type))
            context_info.append(f"User Goal: {value}")

        if getattr(self.context, "dietary_preference", None):
            value = getattr(self.context.dietary_preference, "value", str(self.context.dietary_preference))
            context_info.append(f"Dietary Preference: {value}")

        if getattr(self.context, "medical_conditions", None):
            vals = [getattr(cond, "value", str(cond)) for cond in self.context.medical_conditions if str(cond) != "none"]
            if vals:
                context_info.append(f"Medical Conditions: {', '.join(vals)}")

        if getattr(self.context, "injury_notes", None):
            context_info.append(f"Injury Notes: {self.context.injury_notes}")

        if getattr(self.context, "food_allergies", None):
            if self.context.food_allergies:
                context_info.append(f"Food Allergies: {', '.join(self.context.food_allergies)}")

        context_str = "\n".join(context_info) if context_info else ""
        prompt = (
            f"{self.system_prompt}\n\n"
            f"[User Context]\n{context_str}\n\n"
            f"[User Message]\n{message}"
        ).strip()
        return prompt
