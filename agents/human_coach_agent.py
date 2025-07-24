from typing import AsyncGenerator, List
from .base import BaseAgent

class HumanCoachAgent(BaseAgent):
    """Human coach connection and crisis support agent, streams responses."""

    def __init__(self):
        super().__init__(
            name="human_coach",
            description="Agent providing human coach/crisis support and professional referrals.",
            system_prompt=(
                "You are an empathetic human coach escalation agent. If the user expresses a need for crisis help, " 
                "help them get to appropriate crisis or emergency resources. Otherwise, connect users to trusted, real-world professionals "
                "for complex health, nutrition, mental health, and fitness needs. Never provide direct medical crisis intervention; always escalate."
            )
        )
        self.capabilities = [
            "Professional referrals",
            "Crisis support resources",
            "Complex case management",
            "Human coach connections",
            "Emergency intervention",
            "Specialized care coordination"
        ]

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Streams response chunks per your assignment SDK."""
        msg = message.lower()

        # Route based on content/intent
        crisis_keywords = ['crisis', 'emergency', 'suicide', 'hurt myself']
        if any(word in msg for word in crisis_keywords):
            response = await self._handle_crisis_support(message)
        elif any(word in msg for word in ['therapist', 'counselor', 'psychologist', 'psychiatrist']):
            response = await self._provide_mental_health_referrals(message)
        elif any(word in msg for word in ['doctor', 'physician', 'medical']):
            response = await self._provide_medical_referrals(message)
        elif any(word in msg for word in ['nutritionist', 'dietitian']):
            response = await self._provide_nutrition_referrals(message)
        elif any(word in msg for word in ['trainer', 'coach', 'fitness professional']):
            response = await self._provide_fitness_referrals(message)
        else:
            response = await self._handle_general_human_support(message)

        # Stream each paragraph/tip separately for real-time UI
        for block in response.strip().split('\n\n'):
            yield block + "\n\n"

    async def _handle_crisis_support(self, message: str) -> str:
        ctx = self.context
        response = "🚨 IMMEDIATE CRISIS SUPPORT\n\n" \
                   "🆘 **If you're in immediate danger, please contact emergency services: 911**\n\n" \
                   "📞 **24/7 Crisis Resources**:\n\n" \
                   "🇺🇸 **United States**:\n" \
                   "• **National Suicide Prevention Lifeline**: 988\n" \
                   "  - Available 24/7, free and confidential\n" \
                   "  - Chat online at suicidepreventionlifeline.org\n\n" \
                   "• **Crisis Text Line**: Text HOME to 741741\n" \
                   "  - Free, 24/7 crisis support via text\n" \
                   "  - Trained crisis counselors available\n\n" \
                   "• **National Domestic Violence Hotline**: 1-800-799-7233\n" \
                   "  - 24/7 support for domestic violence situations\n\n" \
                   "• **SAMHSA National Helpline**: 1-800-662-4357\n" \
                   "  - Mental health and substance abuse support\n" \
                   "  - Treatment referral and information service\n\n" \
                   "🌍 **International Resources**:\n" \
                   "• **Canada**: Talk Suicide Canada - 1-833-456-4566\n" \
                   "• **UK**: Samaritans - 116 123\n" \
                   "• **Australia**: Lifeline - 13 11 14\n" \
                   "• **International**: befrienders.org\n\n" \
                   "🏥 **Immediate Steps**:\n" \
                   "1. **Stay Safe**: Remove any means of self-harm\n" \
                   "2. **Reach Out**: Call a number above\n" \
                   "3. **Stay Connected**: Don't isolate yourself\n" \
                   "4. **Go to ER**: If in immediate danger\n" \
                   "5. **Tell Someone**: Inform a trusted friend\n\n" \
                   "💙 **Remember**:\n" \
                   "• You are not alone\n" \
                   "• Crisis feelings are temporary\n" \
                   "• Help is available and effective\n" \
                   "• Your life has value and meaning\n" \
                   "• Many people have recovered\n\n" \
                   "🤝 **Next Steps After Crisis**:\n" \
                   "• Follow up with a mental health professional\n" \
                   "• Create a safety plan with support\n" \
                   "• Consider intensive outpatient programs\n" \
                   "• Build a support network\n"
        # Conversation logging, if desired
        if ctx:
            ctx.add_message(role="user", content=message)
            ctx.add_message(role="assistant", content="Crisis support provided.", agent_type="human_coach")
        return response

    async def _provide_mental_health_referrals(self, message: str) -> str:
        # ... [Identical content from your original, but use self.context and stream formatting as above]
        response = (
            "🧠 Mental Health Professional Referrals\n\n"
            # ... rest of your paragraph blocks, unchanged for brevity ...
        )
        return response

    async def _provide_medical_referrals(self, message: str) -> str:
        response = ("🏥 Medical Professional Referrals\n\n"
            # ... same, see your content above ...
        )
        return response

    async def _provide_nutrition_referrals(self, message: str) -> str:
        response = ("🥗 Nutrition Professional Referrals\n\n"
            # ... and so on ...
        )
        return response

    async def _provide_fitness_referrals(self, message: str) -> str:
        response = ("🏋️‍♀️ Fitness Professional Referrals\n\n"
            # ... and so on ...
        )
        return response

    async def _handle_general_human_support(self, message: str) -> str:
        ctx = self.context
        name = ctx.name if ctx else "User"
        response = (
            f"🤝 Human Support & Professional Resources\n\n"
            f"Hello {name}! I understand you'd like to connect with human professionals. That's a great step.\n\n"
            # ... rest of your sectioned content here ...
        )
        return response

    def get_capabilities(self) -> List[str]:
        return self.capabilities


