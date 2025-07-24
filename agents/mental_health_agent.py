from typing import AsyncGenerator, List, Optional

from agents.base import BaseAgent

class MentalHealthAgent(BaseAgent):
    """Specialized mental health and wellness agent, streams all response sections."""

    def __init__(self):
        super().__init__(
            name="mental_health",
            description="Agent providing evidence-based mental health support, mindfulness, and crisis awareness.",
            system_prompt=(
                "You are a mental health and emotional wellness support agent. "
                "Provide science-backed stress reduction, sleep optimization, mood improvement, and healthy habit methods. "
                "Carefully screen for crisis and serious concerns, and always recommend professional human support if needed."
            )
        )
        self.capabilities = [
            "Stress management techniques",
            "Sleep optimization",
            "Mindfulness and meditation",
            "Habit formation support",
            "Emotional wellness guidance",
            "Crisis resource referrals"
        ]

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        msg = message.lower()

        # Dispatch topic
        if any(word in msg for word in ['stress', 'stressed', 'overwhelmed']):
            response = await self._handle_stress_management(message)
        elif any(word in msg for word in ['sleep', 'insomnia', 'tired', 'exhausted']):
            response = await self._handle_sleep_issues(message)
        elif any(word in msg for word in ['anxiety', 'anxious', 'worried', 'panic']):
            response = await self._handle_anxiety_support(message)
        elif any(word in msg for word in ['meditation', 'mindfulness', 'breathing']):
            response = await self._handle_mindfulness_guidance(message)
        elif any(word in msg for word in ['habit', 'routine', 'consistency']):
            response = await self._handle_habit_formation(message)
        elif any(word in msg for word in ['mood', 'depression', 'sad', 'down']):
            response = await self._handle_mood_support(message)
        else:
            response = await self._handle_general_mental_health(message)

        # Stream by paragraph for real-time interface
        for para in response.strip().split('\n\n'):
            yield para + "\n\n"

    async def _handle_stress_management(self, message: str) -> str:
        response = (
            "🧘‍♀️ Stress Management Strategies\n\n"
            "🎯 **Immediate Stress Relief** (use right now):\n\n"
            "1. **4-7-8 Breathing**:\n"
            "   - Inhale for 4 counts\n"
            "   - Hold for 7 counts\n"
            "   - Exhale for 8 counts\n"
            "   - Repeat 3-4 times\n\n"
            "2. **Progressive Muscle Relaxation**:\n"
            "   - Tense and release each muscle group\n"
            "   - Start with toes, work up to head\n"
            "   - Hold tension for 5 seconds, then release\n\n"
            "3. **Grounding Technique (5-4-3-2-1)**:\n"
            "   - 5 things you can see\n"
            "   - 4 things you can touch\n"
            "   - 3 things you can hear\n"
            "   - 2 things you can smell\n"
            "   - 1 thing you can taste\n\n"
            "🛡️ **Long-term Stress Management**:\n\n"
            "• **Regular Exercise**: 30 minutes daily reduces cortisol\n"
            "• **Adequate Sleep**: 7-9 hours for stress recovery\n"
            "• **Healthy Boundaries**: Learn to say no to overcommitment\n"
            "• **Time Management**: Prioritize tasks and delegate when possible\n"
            "• **Social Support**: Connect with friends and family regularly\n"
            "• **Mindfulness Practice**: 10-15 minutes daily meditation\n\n"
            "⚠️ **When to Seek Professional Help**:\n"
            "• Stress interferes with daily functioning\n"
            "• Physical symptoms (headaches, stomach issues)\n"
            "• Sleep problems persist for weeks\n"
            "• Feeling overwhelmed most days\n\n"
            "Tips:\n"
            "• Start with one technique and practice it consistently\n"
            "• Identify your personal stress triggers\n"
            "• Create a daily stress-relief routine\n"
            "• Remember that some stress is normal and manageable\n\n"
            "Next Steps:\n"
            "• Try the 4-7-8 breathing technique right now\n"
            "• Identify your top 3 stress triggers\n"
            "• Schedule 10 minutes daily for stress relief\n"
        )
        return response

    async def _handle_sleep_issues(self, message: str) -> str:
        response = (
            "😴 Sleep Optimization Guide\n\n"
            "🌙 **Sleep Hygiene Fundamentals**:\n\n"
            "1. **Consistent Schedule**:\n"
            "   - Same bedtime and wake time daily (even weekends)\n"
            "   - Aim for 7-9 hours of sleep\n"
            "   - Avoid 'catching up' on sleep\n\n"
            "2. **Bedroom Environment**:\n"
            "   - Cool temperature (65-68°F / 18-20°C)\n"
            "   - Dark room (blackout curtains, eye mask)\n"
            "   - Quiet environment (earplugs, white noise)\n"
            "   - Comfortable mattress and pillows\n\n"
            "3. **Pre-Sleep Routine** (1-2 hours before bed):\n"
            "   - Dim lights and avoid screens\n"
            "   - Light stretching or reading\n"
            "   - Warm bath or shower\n"
            "   - Relaxation techniques\n\n"
            "☕ **What to Avoid**:\n"
            "• Caffeine after 2 PM\n"
            "• Large meals 3 hours before bed\n"
            "• Alcohol (disrupts sleep quality)\n"
            "• Intense exercise 4 hours before bed\n"
            "• Daytime naps longer than 20 minutes\n\n"
            "🧘 **If You Can't Fall Asleep**:\n"
            "• Don't lie in bed awake for more than 20 minutes\n"
            "• Get up and do a quiet, non-stimulating activity\n"
            "• Return to bed when you feel sleepy\n"
            "• Practice the 4-7-8 breathing technique\n\n"
            "⚠️ **When to Consult a Doctor**:\n"
            "• Chronic insomnia (3+ weeks)\n"
            "• Loud snoring or breathing interruptions\n"
            "• Excessive daytime sleepiness\n"
            "• Sleep issues affecting daily life\n\n"
            "Tips:\n"
            "• Changes take 2-4 weeks to show full effect\n"
            "• Be patient and consistent with new habits\n"
            "• Track your sleep patterns to identify issues\n"
            "• Consider a sleep diary for 1-2 weeks\n\n"
            "Next Steps:\n"
            "• Set a consistent bedtime starting tonight\n"
            "• Create a 30-minute wind-down routine\n"
            "• Optimize your bedroom environment\n"
        )
        return response

    async def _handle_anxiety_support(self, message: str) -> str:
        response = (
            "🌸 Anxiety Management Support\n\n"
            "💙 Remember: Anxiety is treatable, and you're not alone in this experience.\n\n"
            "🆘 **Immediate Anxiety Relief**:\n\n"
            "1. **Box Breathing**:\n"
            "   - Inhale for 4 counts\n"
            "   - Hold for 4 counts\n"
            "   - Exhale for 4 counts\n"
            "   - Hold empty for 4 counts\n"
            "   - Repeat 5-10 times\n\n"
            "2. **Grounding Techniques**:\n"
            "   - Name 5 things you can see\n"
            "   - Feel your feet on the ground\n"
            "   - Hold a cold object or splash cold water\n"
            "   - Focus on your immediate surroundings\n\n"
            "3. **Challenge Anxious Thoughts**:\n"
            "   - Is this thought realistic?\n"
            "   - What would I tell a friend in this situation?\n"
            "   - What's the worst that could realistically happen?\n"
            "   - How likely is that outcome?\n\n"
            "🛠️ **Long-term Anxiety Management**:\n\n"
            "• **Regular Exercise**: Reduces anxiety hormones naturally\n"
            "• **Mindfulness Meditation**: 10-20 minutes daily\n"
            "• **Limit Caffeine**: Can worsen anxiety symptoms\n"
            "• **Adequate Sleep**: Poor sleep increases anxiety\n"
            "• **Social Connection**: Talk to trusted friends/family\n"
            "• **Journaling**: Write down worries and thoughts\n\n"
            "🚨 **Seek Professional Help If**:\n"
            "• Anxiety interferes with daily activities\n"
            "• Physical symptoms (rapid heartbeat, sweating)\n"
            "• Avoiding situations due to anxiety\n"
            "• Panic attacks occur regularly\n"
            "• Thoughts of self-harm\n\n"
            "📞 **Crisis Resources**:\n"
            "• National Suicide Prevention Lifeline: 988\n"
            "• Crisis Text Line: Text HOME to 741741\n"
            "• Emergency Services: 911\n\n"
            "Tips:\n"
            "• Anxiety is your body's alarm system - it's trying to protect you\n"
            "• Practice anxiety management techniques when calm, not just during anxiety\n"
            "• Small, consistent steps are more effective than big changes\n"
            "• Consider therapy - it's highly effective for anxiety\n\n"
            "Next Steps:\n"
            "• Practice box breathing for 5 minutes today\n"
            "• Identify your anxiety triggers\n"
            "• Consider reaching out to a mental health professional\n"
        )
        return response

    async def _handle_mindfulness_guidance(self, message: str) -> str:
        response = (
            "🧘 Mindfulness & Meditation Guide\n\n"
            "🌟 **What is Mindfulness?**\n"
            "Mindfulness is the practice of being fully present and engaged in the current moment, without judgment or distraction.\n\n"
            "🎯 **Benefits of Regular Practice**:\n"
            "• Reduced stress and anxiety\n"
            "• Improved focus and concentration\n"
            "• Better emotional regulation\n"
            "• Enhanced self-awareness\n"
            "• Improved sleep quality\n"
            "• Lower blood pressure\n\n"
            "🧘‍♀️ **Simple Meditation Techniques**:\n\n"
            "1. **Breath Awareness** (5-20 minutes):\n"
            "   - Sit comfortably with eyes closed\n"
            "   - Focus on your natural breathing\n"
            "   - When mind wanders, gently return to breath\n"
            "   - No judgment, just gentle redirection\n\n"
            "2. **Body Scan** (10-30 minutes):\n"
            "   - Lie down comfortably\n"
            "   - Start at toes, slowly move attention up body\n"
            "   - Notice sensations without trying to change them\n"
            "   - Great for relaxation and body awareness\n\n"
            "3. **Loving-Kindness** (10-20 minutes):\n"
            "   - Send good wishes to yourself\n"
            "   - Extend to loved ones, neutral people, difficult people\n"
            "   - Use phrases like 'May you be happy, may you be peaceful'\n"
            "   - Builds compassion and reduces negative emotions\n\n"
            "📱 **Mindfulness Throughout the Day**:\n"
            "• **Mindful Eating**: Pay attention to taste, texture, smell\n"
            "• **Walking Meditation**: Focus on each step and breath\n"
            "• **Mindful Listening**: Give full attention to sounds around you\n"
            "• **Pause Practice**: Take 3 conscious breaths before transitions\n\n"
            "🎯 **Getting Started**:\n"
            "• Start with just 5 minutes daily\n"
            "• Choose a consistent time (morning often works best)\n"
            "• Use guided meditations initially (apps like Headspace, Calm)\n"
            "• Be patient - benefits develop over time\n"
            "• Don't judge your practice - there's no 'perfect' meditation\n\n"
            "Tips:\n"
            "• Consistency matters more than duration\n"
            "• It's normal for your mind to wander - that's not failure\n"
            "• Start small and gradually increase practice time\n"
            "• Find a quiet space but don't worry about perfect conditions\n\n"
            "Next Steps:\n"
            "• Try 5 minutes of breath awareness today\n"
            "• Download a meditation app for guidance\n"
            "• Set a daily reminder for practice time\n"
        )
        return response

    async def _handle_habit_formation(self, message: str) -> str:
        response = (
            "🔄 Habit Formation & Behavior Change\n\n"
            "🧠 **How Habits Work** (The Habit Loop):\n"
            "1. **Cue**: Environmental trigger\n"
            "2. **Routine**: The behavior itself\n"
            "3. **Reward**: The benefit you get\n\n"
            "✅ **Building Good Habits**:\n\n"
            "1. **Start Incredibly Small**:\n"
            "   - Want to exercise? Start with 1 push-up\n"
            "   - Want to meditate? Start with 1 minute\n"
            "   - Want to read? Start with 1 page\n\n"
            "2. **Stack Habits**:\n"
            "   - Attach new habit to existing routine\n"
            "   - 'After I brush my teeth, I will do 5 squats'\n"
            "   - 'After I pour my coffee, I will write 3 gratitudes'\n\n"
            "3. **Design Your Environment**:\n"
            "   - Make good habits obvious and easy\n"
            "   - Put workout clothes by your bed\n"
            "   - Keep healthy snacks visible\n\n"
            "4. **Track Your Progress**:\n"
            "   - Use a simple habit tracker\n"
            "   - Mark an X for each day completed\n"
            "   - Celebrate small wins\n\n"
            "❌ **Breaking Bad Habits**:\n\n"
            "1. **Identify Triggers**:\n"
            "   - What situations lead to the bad habit?\n"
            "   - Emotional states, times, places, people\n\n"
            "2. **Change the Environment**:\n"
            "   - Remove temptations when possible\n"
            "   - Make bad habits harder to do\n\n"
            "3. **Replace, Don't Just Remove**:\n"
            "   - Substitute a better behavior\n"
            "   - Keep the same cue and reward\n\n"
            "⏰ **The 21-Day Myth**:\n"
            "Reality: Habits take 18-254 days to form (average: 66 days)\n"
            "• Simple habits form faster\n"
            "• Complex habits take longer\n"
            "• Missing one day won't ruin progress\n\n"
            "🎯 **Habit Success Strategies**:\n"
            "• Focus on one habit at a time\n"
            "• Be specific about when and where\n"
            "• Plan for obstacles and setbacks\n"
            "• Find an accountability partner\n"
            "• Reward yourself for consistency\n\n"
            "Tips:\n"
            "• Make it so easy you can't say no\n"
            "• Focus on showing up, not perfect performance\n"
            "• Identity change drives behavior change\n"
            "• Progress, not perfection, is the goal\n\n"
            "Next Steps:\n"
            "• Choose ONE habit to focus on\n"
            "• Make it incredibly small to start\n"
            "• Identify your cue and reward\n"
        )
        return response

    async def _handle_mood_support(self, message: str) -> str:
        response = (
            "💙 Mood & Emotional Wellness Support\n\n"
            "🤗 Remember: It's okay to not be okay sometimes. Your feelings are valid.\n\n"
            "🌈 **Natural Mood Boosters**:\n\n"
            "1. **Physical Activity**:\n"
            "   - Even 10 minutes of walking helps\n"
            "   - Exercise releases endorphins\n"
            "   - Try dancing to your favorite song\n\n"
            "2. **Sunlight & Nature**:\n"
            "   - 15-30 minutes of sunlight daily\n"
            "   - Spend time outdoors when possible\n"
            "   - Even looking at nature photos helps\n\n"
            "3. **Social Connection**:\n"
            "   - Reach out to a friend or family member\n"
            "   - Join a community group or class\n"
            "   - Volunteer for a cause you care about\n\n"
            "4. **Creative Expression**:\n"
            "   - Draw, write, sing, or play music\n"
            "   - Try adult coloring books\n"
            "   - Cook or bake something new\n\n"
            "🧘 **Emotional Regulation Techniques**:\n\n"
            "• **Journaling**: Write about your feelings without judgment\n"
            "• **Gratitude Practice**: List 3 things you're grateful for daily\n"
            "• **Deep Breathing**: Activates the relaxation response\n"
            "• **Progressive Muscle Relaxation**: Releases physical tension\n"
            "• **Mindfulness**: Observe emotions without being overwhelmed\n\n"
            "🛠️ **Daily Mood Maintenance**:\n"
            "• Maintain regular sleep schedule\n"
            "• Eat nutritious, regular meals\n"
            "• Limit alcohol and caffeine\n"
            "• Stay hydrated\n"
            "• Practice self-compassion\n"
            "• Set realistic daily goals\n\n"
            "🚨 **When to Seek Professional Help**:\n"
            "• Persistent sadness for 2+ weeks\n"
            "• Loss of interest in activities you used to enjoy\n"
            "• Significant changes in sleep or appetite\n"
            "• Difficulty concentrating or making decisions\n"
            "• Thoughts of self-harm or suicide\n"
            "• Mood interferes with work, relationships, or daily life\n\n"
            "📞 **Crisis Resources**:\n"
            "• National Suicide Prevention Lifeline: 988\n"
            "• Crisis Text Line: Text HOME to 741741\n"
            "• Emergency Services: 911\n\n"
            "Tips:\n"
            "• Small actions can lead to big mood improvements\n"
            "• Be patient with yourself - healing takes time\n"
            "• Professional help is a sign of strength, not weakness\n"
            "• You don't have to face difficult emotions alone\n\n"
            "Next Steps:\n"
            "• Try one mood-boosting activity today\n"
            "• Consider keeping a mood journal\n"
            "• Reach out to someone you trust\n"
        )
        return response

    async def _handle_general_mental_health(self, message: str) -> str:
        response = (
            "🧠 Hello! I'm your mental health and wellness specialist.\n\n"
            "I'm here to support your emotional and psychological well-being. "
            "While I can't replace professional therapy, I can provide evidence-based strategies and resources.\n\n"
            "🌟 **Areas I Can Help With**:\n"
            "• Stress management and coping strategies\n"
            "• Sleep optimization and insomnia support\n"
            "• Anxiety management techniques\n"
            "• Mindfulness and meditation guidance\n"
            "• Habit formation and behavior change\n"
            "• Mood support and emotional wellness\n"
            "• Crisis resources and professional referrals\n\n"
            "💡 **Mental Health Fundamentals**:\n"
            "• **Self-Care**: Regular activities that support your well-being\n"
            "• **Boundaries**: Protecting your time and energy\n"
            "• **Support Systems**: Maintaining healthy relationships\n"
            "• **Professional Help**: Therapy and counseling when needed\n"
            "• **Lifestyle Factors**: Sleep, exercise, nutrition, and stress management\n\n"
            "🤝 **Remember**:\n"
            "• Mental health is just as important as physical health\n"
            "• It's okay to ask for help\n"
            "• Small steps can lead to significant improvements\n"
            "• You're not alone in your struggles\n\n"
            "Tips:\n"
            "• Mental health is a journey, not a destination\n"
            "• What works for others might not work for you - that's okay\n"
            "• Consistency in self-care practices is key\n"
            "• Professional support can be incredibly valuable\n\n"
            "Next Steps:\n"
            "• Tell me about any specific mental health concerns\n"
            "• Share what areas you'd like to work on\n"
            "• Let me know how I can best support you\n"
        )
        return response

    async def should_handoff(self, message: str) -> Optional[str]:
        """
        Returns 'human_coach' for crisis or severe mental health issues,
        otherwise None for processing by this agent.
        """
        msg = message.lower()
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'hurt myself', 'self harm', 'overdose', "can't go on"
        ]
        if any(keyword in msg for keyword in crisis_keywords):
            return "human_coach"
        severe_keywords = [
            'severe depression', 'bipolar', 'schizophrenia', 'psychosis',
            'eating disorder', 'addiction', 'substance abuse'
        ]
        if any(keyword in msg for keyword in severe_keywords):
            return "human_coach"
        return None

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        return self.capabilities
