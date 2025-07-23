"""
Chainlit Health & Wellness Coach
Multi-agent health assistance with chat interface
"""

import os
import chainlit as cl
from openai import AsyncOpenAI
from typing import AsyncGenerator

from agents.wellness_agent import WellnessAgent
from agents.nutrition_expert_agent import NutritionAgent
from agents.fitness_agent import FitnessAgent
from context import UserSessionContext
from database import init_db, save_conversation

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize agents
wellness_agent = WellnessAgent()
nutrition_agent = NutritionAgent()
fitness_agent = FitnessAgent()

# Agent mapping for easy selection
AGENTS = {
    "wellness": ("🌟 Wellness Coach", wellness_agent),
    "nutrition": ("🥗 Nutrition Coach", nutrition_agent),
    "fitness": ("💪 Fitness Coach", fitness_agent),
}


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Initialize database
    init_db()
    
    # Create user context
    user_id = f"chainlit_user_{cl.user_session.get('id', 'anonymous')}"
    context = UserSessionContext(user_id=user_id)
    
    # Store in session
    cl.user_session.set("context", context)
    cl.user_session.set("current_agent", "wellness")
    
    # Welcome message with agent selection
    actions = [
        cl.Action(
            name="select_wellness",
            value="wellness",
            label="🌟 Wellness Coach",
            description="General health guidance and wellness advice"
        ),
        cl.Action(
            name="select_nutrition", 
            value="nutrition",
            label="🥗 Nutrition Coach",
            description="Diet planning and nutritional guidance"
        ),
        cl.Action(
            name="select_fitness",
            value="fitness", 
            label="💪 Fitness Coach",
            description="Workout plans and exercise recommendations"
        ),
    ]
    
    await cl.Message(
        content="""# 🏥 Welcome to Health & Wellness Coach!

I'm your AI-powered health assistant with specialized coaches to help you achieve your wellness goals.

## Available Coaches:
- **🌟 Wellness Coach**: General health guidance, lifestyle advice, and motivation
- **🥗 Nutrition Coach**: Personalized meal planning, dietary recommendations, and nutrition education  
- **💪 Fitness Coach**: Custom workout plans, exercise guidance, and fitness strategies

Please select a coach to start our conversation, or just type your health question and I'll route you to the right specialist!

---
*Remember: This AI coach provides general wellness information only. Always consult healthcare professionals for medical concerns.*
""",
        actions=actions
    ).send()


@cl.action_callback("select_wellness")
async def on_wellness_selected(action):
    """Handle wellness coach selection."""
    cl.user_session.set("current_agent", "wellness")
    await cl.Message(
        content="🌟 **Wellness Coach activated!**\n\nI'm here to help with general health questions, lifestyle advice, motivation, and overall wellness guidance. What would you like to discuss today?"
    ).send()


@cl.action_callback("select_nutrition")
async def on_nutrition_selected(action):
    """Handle nutrition coach selection."""
    cl.user_session.set("current_agent", "nutrition")
    await cl.Message(
        content="🥗 **Nutrition Coach activated!**\n\nI'm ready to help with meal planning, dietary advice, nutritional analysis, and healthy eating strategies. What nutrition goals are you working on?"
    ).send()


@cl.action_callback("select_fitness")
async def on_fitness_selected(action):
    """Handle fitness coach selection."""
    cl.user_session.set("current_agent", "fitness")
    await cl.Message(
        content="💪 **Fitness Coach activated!**\n\nLet's work on your fitness goals! I can help create workout plans, suggest exercises, provide form guidance, and adapt routines for your needs. What's your fitness objective?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Process user messages and route to appropriate agent."""
    context = cl.user_session.get("context")
    current_agent_key = cl.user_session.get("current_agent", "wellness")
    
    # Get the selected agent
    agent_name, agent = AGENTS[current_agent_key]
    
    # Update context with message history
    if context:
        # Store conversation in context
        if not hasattr(context, 'conversation_history'):
            context.conversation_history = []
        context.conversation_history.append({
            "role": "user",
            "content": message.content,
            "timestamp": cl.context.session.created_at
        })
    
    # Create message placeholder
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # Stream response from agent
        response_text = ""
        async for chunk in agent.process_message(message.content, context):
            if chunk:
                response_text += chunk
                await msg.stream_token(chunk)
        
        await msg.update()
        
        # Save to database
        if context and context.user_id:
            save_conversation(
                context.user_id,
                message.content,
                response_text,
                current_agent_key
            )
            
        # Update context with response
        if context and hasattr(context, 'conversation_history'):
            context.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "agent": current_agent_key,
                "timestamp": cl.context.session.created_at
            })
            
        # Add agent switching actions if the response suggests it
        if should_suggest_agent_switch(response_text):
            actions = []
            
            # Suggest other agents based on response content
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
async def switch_to_nutrition(action):
    """Switch to nutrition coach."""
    cl.user_session.set("current_agent", "nutrition")
    await cl.Message(
        content="🥗 **Switched to Nutrition Coach!**\n\nI'm now ready to provide specialized dietary and nutrition guidance. How can I help with your nutritional goals?"
    ).send()


@cl.action_callback("switch_fitness")
async def switch_to_fitness(action):
    """Switch to fitness coach."""
    cl.user_session.set("current_agent", "fitness")
    await cl.Message(
        content="💪 **Switched to Fitness Coach!**\n\nReady to help with your fitness journey! What workout or exercise questions do you have?"
    ).send()


def should_suggest_agent_switch(response_text: str) -> bool:
    """Determine if we should suggest switching to a different agent."""
    # Simple keyword detection for agent switching suggestions
    nutrition_keywords = ["meal", "diet", "calories", "nutrition", "food", "eating"]
    fitness_keywords = ["exercise", "workout", "fitness", "training", "gym", "strength"]
    
    text_lower = response_text.lower()
    
    # Check if response contains keywords for other agents
    has_nutrition = any(keyword in text_lower for keyword in nutrition_keywords)
    has_fitness = any(keyword in text_lower for keyword in fitness_keywords)
    
    return has_nutrition or has_fitness


@cl.on_stop
async def on_stop():
    """Handle session cleanup."""
    context = cl.user_session.get("context")
    if context:
        # Could add session summary or final recommendations here
        print(f"Session ended for user: {context.user_id}")


if __name__ == "__main__":
    # This is for development - Chainlit runs automatically
    print("Chainlit Health & Wellness Coach")
    print("Run with: chainlit run chainlit_app.py")
    