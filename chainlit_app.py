import os
import chainlit as cl
from openai import AsyncOpenAI
from typing import AsyncGenerator
from datetime import datetime

from context import UserSessionContext, GoalType, GoalUnit, DietaryPreference, MedicalCondition
from utils.report import generate_pdf_report
from app_config import config
from utils.transform import transform_input

client = AsyncOpenAI(api_key=config.openai_api_key)

class WellnessAssistant:
    def __init__(self):
        self.system_prompt = (
            "You are a certified nutritionist and wellness coach. "
            "Provide scientifically-validated, personalized advice with clear explanations "
            "in simple terms. Offer culturally appropriate suggestions."
        )
        self.safety_instructions = (
            "If a request violates content policies, respond with: "
            "\"🔒 I can't assist with that request, but I'm happy to help "
            "with nutrition and wellness advice.\""
        )

    async def generate_response(self, prompt: str, context: UserSessionContext) -> AsyncGenerator[str, None]:
        full_prompt = self._build_prompt(prompt, context)

        try:
            stream = await client.chat.completions.create(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                stream=True,
                temperature=0.7
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield self._handle_error(e)

    def _build_prompt(self, prompt: str, context: UserSessionContext) -> str:
        return f"""
        [User Profile]
        User ID: {context.user_id}
        Goal: {context.goal_type} - {context.goal_target}{context.goal_unit} by {context.goal_deadline}
        Dietary Preferences: {context.dietary_preference}
        Allergies: {', '.join(context.food_allergies)}
        Medical Conditions: {', '.join([mc.value for mc in context.medical_conditions])}
        Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

        [Instructions]
        {self.safety_instructions}

        [Current Request]
        {prompt}
        """

    def _handle_error(self, error: Exception) -> str:
        if "content policy" in str(error).lower():
            return "🔒 I can't assist with that request due to content policies."
        return "⚠️ Technical difficulty: Please try again later."


assistant = WellnessAssistant()

@cl.on_chat_start
async def init_session():
    raw_data = {
        "name": "Asma Yaseen",
        "uid": "00436743",
        "goal": "Lose 5kg in 2 months",
        "diet_preferences": "Vegetarian",
        "lifestyle": "Busy office worker",
        "handoff_logs": [],
        "progress_logs": []
    }

    context = UserSessionContext(**transform_input(raw_data))
    cl.user_session.set("context", context)

    welcome = cl.Message(content="")
    await welcome.send()

    await welcome.stream_token(
        """🌿 **Welcome to Your Wellness Assistant!**

I'm here to help you with:
- Personalized meal planning 🍎
- Nutrition guidance 📊
- Healthy lifestyle tips 🏋️
- Progress tracking 📈

How can I assist you today?"""
    )

@cl.on_message
async def handle_message(message: cl.Message):
    context: UserSessionContext = cl.user_session.get("context")
    if not context:
        await cl.Message(content="⚠️ Session error. Please refresh.").send()
        return

    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    is_meal_plan = any(kw in message.content.lower() for kw in ["meal plan", "diet plan", "eating plan"])

    try:
        async for chunk in assistant.generate_response(message.content, context):
            full_response += chunk
            await msg.stream_token(chunk)

        if hasattr(context, "add_progress_update"):
            context.add_progress_update(
                event_type="goal_update" if is_meal_plan else "note",
                description=message.content[:100]
            )

        if is_meal_plan:
            await _handle_meal_plan(context, full_response)

    except Exception as e:
        await msg.stream_token(f"❌ Error: {str(e)}")
        if hasattr(context, "add_progress_update"):
            context.add_progress_update(
                event_type="system",
                description=f"Error during processing: {str(e)}"
            )

async def _handle_meal_plan(context: UserSessionContext, full_response: str):
    try:
        if hasattr(context, "log_handoff"):
            context.log_handoff(
                from_agent="WellnessAssistant",
                to_agent="MealPlanModule",
                reason="Generated meal plan based on user request",
                context_snapshot={"response": full_response}
            )

        report_path = generate_pdf_report(context)

        if os.path.exists(report_path):
            await cl.Message(
                content="📄 Here's your personalized meal plan:",
                elements=[
                    cl.File(
                        name=f"meal_plan_{datetime.now().date()}.pdf",
                        path=report_path,
                        display="inline",
                        description="Your personalized meal plan"
                    )
                ]
            ).send()
    except Exception as e:
        await cl.Message(content=f"⚠️ Couldn't generate PDF: {str(e)}").send()
