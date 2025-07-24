"""
Chainlit Health & Wellness Coach
Multi-agent health assistance with chat interface (Gemini version)
"""

import os
import chainlit as cl
from typing import AsyncGenerator, Optional
import google.generativeai as genai
from agents.wellness_agent import WellnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.fitness_agent import FitnessAgent
from context import UserSessionContext
from database import init_db, save_conversation

# Initialize Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "gemini-1.5-flash"

# Initialize agents
wellness_agent = WellnessAgent()
nutrition_agent = NutritionAgent()
fitness_agent = FitnessAgent()

AGENTS = {
    "wellness": ("🌟 Wellness Coach", wellness_agent),
    "nutrition": ("🥗 Nutrition Coach", nutrition_agent),
    "fitness": ("💪 Fitness Coach", fitness_agent),
}

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    init_db()
    user_id = f"chainlit_user_{cl.user_session.get('id', 'anonymous')}"
    # Ask for user's name!
    name_prompt = await cl.AskUserMessage(
        content="👋 Welcome to Health & Wellness Coach!\n\nWhat's your name?",
        timeout=60
    ).send()
    name = name_prompt.get("output", "").strip() if name_prompt else "Guest"

    # Create the full context
    context = UserSessionContext(name=name, user_id=user_id)
    cl.user_session.set("context", context)
    cl.user_session.set("current_agent", "wellness")

    actions = [
    cl.Action(
        name="select_wellness",
        payload={"value": "wellness"},
        label="🌟 Wellness Coach",
        description="General health guidance and wellness advice"
    ),
    cl.Action(
        name="select_nutrition",
        payload={"value": "nutrition"},
        label="🥗 Nutrition Coach",
        description="Diet planning and nutritional guidance"
    ),
    cl.Action(
        name="select_fitness",
        payload={"value": "fitness"},
        label="💪 Fitness Coach",
        description="Workout plans and exercise recommendations"
    ),
]

        
    await cl.Message(
        content=(
            f"Hi {name}! I'm your AI-powered health assistant 🏥\n\n"
            "## Available Coaches:\n"
            "- 🌟 Wellness Coach: General health guidance, lifestyle advice, and motivation\n"
            "- 🥗 Nutrition Coach: Personalized meal planning, dietary recommendations, and nutrition education\n"
            "- 💪 Fitness Coach: Custom workout plans, exercise guidance, and fitness strategies\n\n"
            "Please select a coach to start, or just type your health question and I'll route you to the right specialist!\n"
            "---\n"
            "*This AI coach provides general wellness information only. Always consult healthcare professionals for urgent medical concerns*"
        ),
        actions=actions
    ).send()

@cl.action_callback("select_wellness")
async def on_wellness_selected():
    cl.user_session.set("current_agent", "wellness")
    await cl.Message(
        content="🌟 **Wellness Coach activated!**\nWhat would you like to discuss today?"
    ).send()

@cl.action_callback("select_nutrition")
async def on_nutrition_selected():
    cl.user_session.set("current_agent", "nutrition")
    await cl.Message(
        content="🥗 **Nutrition Coach activated!**\nWhat nutrition goals are you working on?"
    ).send()

@cl.action_callback("select_fitness")
async def on_fitness_selected():
    cl.user_session.set("current_agent", "fitness")
    await cl.Message(
        content="💪 **Fitness Coach activated!**\nWhat's your fitness objective?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    context: Optional[UserSessionContext] = cl.user_session.get("context")
    current_agent_key = cl.user_session.get("current_agent") or "wellness"
    _, agent = AGENTS[current_agent_key]

    # Add to conversation history if wanted
    if context:
        # Safely initialize if missing
        if not hasattr(context, 'conversation_history') or context.conversation_history is None:
            context.conversation_history = []
        context.conversation_history.append({
            "role": "user",
            "content": message.content,
            # fallback: you may want to import datetime for timestamp
        })

    msg = cl.Message(content="")
    await msg.send()

    try:
        response_text = ""
        # Streaming response (make sure your agents implement async generators)
        async for chunk in agent.process_message(message.content):
            response_text += chunk
            await msg.stream_token(chunk)
        await msg.update()

        # Save conversation, if DB enabled
        if context and context.user_id:
            save_conversation(
                context.user_id,
                message.content,
                response_text,
                current_agent_key
            )
        if context and hasattr(context, 'conversation_history'):
            context.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "agent": current_agent_key,
            })

        # Suggest agent switch if needed
        if should_suggest_agent_switch(response_text):
            actions = []
            if "nutrition" in response_text.lower() or "diet" in response_text.lower():
                actions.append(
                    cl.Action(
                        name="switch_nutrition",
                        value="nutrition",
                        label="🥗 Switch to Nutrition Coach",
                        description="Get specialized dietary guidance"
                    )
                )
            if "exercise" in response_text.lower() or "workout" in response_text.lower():
                actions.append(
                    cl.Action(
                        name="switch_fitness",
                        value="fitness",
                        label="💪 Switch to Fitness Coach",
                        description="Get personalized workout plans"
                    )
                )
            if actions:
                await cl.Message(
                    content="💡 Would you like specialized help with this topic?",
                    actions=actions
                ).send()

    except Exception as e:
        await cl.Message(
            content=f"❌ I encountered an error: {str(e)}\n\nPlease try your question again or contact support if the issue persists."
        ).send()

@cl.action_callback("switch_nutrition")
async def switch_to_nutrition():
    cl.user_session.set("current_agent", "nutrition")
    await cl.Message(
        content="🥗 **Switched to Nutrition Coach!**\nHow can I help with your nutritional goals?"
    ).send()

@cl.action_callback("switch_fitness")
async def switch_to_fitness():
    cl.user_session.set("current_agent", "fitness")
    await cl.Message(
        content="💪 **Switched to Fitness Coach!**\nWhat workout/exercise questions do you have?"
    ).send()

def should_suggest_agent_switch(response_text: str) -> bool:
    nutrition_keywords = ["meal", "diet", "calories", "nutrition", "food", "eating"]
    fitness_keywords = ["exercise", "workout", "fitness", "training", "gym", "strength"]
    text_lower = response_text.lower()
    has_nutrition = any(keyword in text_lower for keyword in nutrition_keywords)
    has_fitness = any(keyword in text_lower for keyword in fitness_keywords)
    return has_nutrition or has_fitness

@cl.on_stop
async def on_stop():
    context = cl.user_session.get("context")
    if context:
        print(f"Session ended for user: {context.user_id}")

if __name__ == "__main__":
    print("Chainlit Health & Wellness Coach")
    print("Run with: chainlit run chainlit_app.py")
