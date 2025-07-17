# planner.py
import os
import asyncio
import logging
from typing import List, Optional, Dict, AsyncGenerator
from openai import AsyncOpenAI
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum

from context import UserSessionContext

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent Types
class AgentType(str, Enum):
    WELLNESS = "wellness"
    NUTRITION = "nutrition"
    INJURY = "injury"
    ESCALATION = "escalation"

class WellnessPlanner:
    """Main application class for Health & Wellness Planner"""

    def __init__(self):
        self.agent_prompts = {
            AgentType.WELLNESS: "You are a friendly health assistant. Provide general wellness advice.",
            AgentType.NUTRITION: "You are a certified nutritionist. Give specific dietary recommendations.",
            AgentType.INJURY: "You are a physical therapist. Suggest recovery advice for injuries.",
            AgentType.ESCALATION: "You handle escalations to human experts. Collect key user needs professionally."
        }

        self.config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 300,
            "streaming": True
        }

        # Load environment
        if not os.getenv("MOCK_MODE", "false").lower() == "true":
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("✅ OpenAI client initialized")
        else:
            self.client = None
            logger.info("🚧 Running in MOCK mode")

    async def get_agent_response(
        self,
        agent: AgentType,
        message: str,
        context: UserSessionContext,
        streaming: bool = False
    ) -> AsyncGenerator[str, None]:
        """Stream or get full response from GPT agent"""
        if self.client is None:
            yield self._get_mock_response(agent, message)
            return

        messages = [
            {"role": "system", "content": self.agent_prompts[agent]},
            *[msg.model_dump() for msg in context.conversation_history],
            {"role": "user", "content": message}
        ]

        try:
            if streaming:
                stream = await self.client.chat.completions.create(
                    model=self.config["model"],
                    messages=messages,
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"],
                    stream=True
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                response = await self.client.chat.completions.create(
                    model=self.config["model"],
                    messages=messages,
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"]
                )
                yield response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            yield "I'm experiencing technical difficulties. Please try again later."

    def _get_mock_response(self, agent: AgentType, message: str) -> str:
        """Mock responses for testing without API"""
        responses = {
            AgentType.WELLNESS: "Daily 30-minute walks and a balanced diet are great for general wellness.",
            AgentType.NUTRITION: "Focus on lean protein, complex carbs, and healthy fats.",
            AgentType.INJURY: "Apply RICE (rest, ice, compress, elevate) and consult a doctor if pain persists.",
            AgentType.ESCALATION: "Transferring you to a specialist. Please explain your concerns in detail."
        }
        return responses.get(agent, "How can I assist you with your health goals?")

    async def determine_next_agent(self, message: str, current: AgentType) -> AgentType:
        """Determine next agent based on message"""
        if self.client is None:
            return self._mock_agent_decision(message)

        prompt = f"""Analyze this message and choose the most suitable agent.
Current Agent: {current.value}
Message: {message}
Options: {[a.value for a in AgentType]}
Respond ONLY with the agent name."""

        try:
            response = await self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )
            agent_name = response.choices[0].message.content.strip().lower()
            return AgentType(agent_name) if agent_name in AgentType._value2member_map_ else current
        except Exception as e:
            logger.warning(f"Agent decision fallback: {e}")
            return current

    def _mock_agent_decision(self, message: str) -> AgentType:
        """Simple rules for mock switching"""
        msg = message.lower()
        if any(word in msg for word in ["diet", "food", "meal"]):
            return AgentType.NUTRITION
        elif any(word in msg for word in ["pain", "injury", "recover"]):
            return AgentType.INJURY
        elif "talk to human" in msg:
            return AgentType.ESCALATION
        return AgentType.WELLNESS

    async def run_conversation(
        self,
        messages: List[str],
        context: Optional[UserSessionContext] = None,
        streaming: bool = False
    ) -> UserSessionContext:
        """Run conversation and manage agent switching"""
        ctx = context or UserSessionContext()
        for msg in messages:
            logger.info(f"User: {msg}")
            ctx.add_message("user", msg)

            response_text = ""
            async for chunk in self.get_agent_response(ctx.current_agent, msg, ctx, streaming):
                if streaming:
                    print(chunk, end="", flush=True)
                response_text += chunk

            if streaming:
                print()

            ctx.add_message("assistant", response_text)
            logger.info(f"{ctx.current_agent.value.capitalize()} Agent: {response_text}")

            next_agent = await self.determine_next_agent(msg, ctx.current_agent)
            if next_agent != ctx.current_agent:
                ctx.log_handoff(ctx.current_agent, next_agent, f"User said: {msg}")
                ctx.current_agent = next_agent

        ctx.end_time = asyncio.get_event_loop().time()
        return ctx
