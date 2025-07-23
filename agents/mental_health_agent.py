from typing import List, Dict, Any, Optional, Tuple
from .base import BaseAgent
from context import UserSessionContext, AgentType

class MentalHealthAgent(BaseAgent):
    """Specialized mental health and wellness agent"""
    
    def __init__(self):
        super().__init__(AgentType.MENTAL_HEALTH)
        self.capabilities = [
            "Stress management techniques",
            "Sleep optimization",
            "Mindfulness and meditation",
            "Habit formation support",
            "Emotional wellness guidance",
            "Crisis resource referrals"
        ]
    
    async def process_message(self, message: str, context: UserSessionContext) -> str:
        """Process mental health-related messages"""
        message_lower = message.lower()
        
        # Handle different mental health topics
        if any(word in message_lower for word in ['stress', 'stressed', 'overwhelmed']):
            return await self._handle_stress_management(message, context)
        elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'exhausted']):
            return await self._handle_sleep_issues(message, context)
        elif any(word in message_lower for word in ['anxiety', 'anxious', 'worried', 'panic']):
            return await self._handle_anxiety_support(message, context)
        elif any(word in message_lower for word in ['meditation', 'mindfulness', 'breathing']):
            return await self._handle_mindfulness_guidance(message, context)
        elif any(word in message_lower for word in ['habit', 'routine', 'consistency']):
            return await self._handle_habit_formation(message, context)
        elif any(word in message_lower for word in ['mood', 'depression', 'sad', 'down']):
            return await self._handle_mood_support(message, context)
        else:
            return await self._handle_general_mental_health(message, context)
    
    async def _handle_stress_management(self, message: str, context: UserSessionContext) -> str:
        """Provide stress management strategies"""
        response = "🧘‍♀️ Stress Management Strategies\n\n"
        
        response += "🎯 **Immediate Stress Relief** (use right now):\n\n"
        response += "1. **4-7-8 Breathing**:\n"
        response += "   - Inhale for 4 counts\n"
        response += "   - Hold for 7 counts\n"
        response += "   - Exhale for 8 counts\n"
        response += "   - Repeat 3-4 times\n\n"
        
        response += "2. **Progressive Muscle Relaxation**:\n"
        response += "   - Tense and release each muscle group\n"
        response += "   - Start with toes, work up to head\n"
        response += "   - Hold tension for 5 seconds, then release\n\n"
        
        response += "3. **Grounding Technique (5-4-3-2-1)**:\n"
        response += "   - 5 things you can see\n"
        response += "   - 4 things you can touch\n"
        response += "   - 3 things you can hear\n"
        response += "   - 2 things you can smell\n"
        response += "   - 1 thing you can taste\n\n"
        
        response += "🛡️ **Long-term Stress Management**:\n\n"
        response += "• **Regular Exercise**: 30 minutes daily reduces cortisol\n"
        response += "• **Adequate Sleep**: 7-9 hours for stress recovery\n"
        response += "• **Healthy Boundaries**: Learn to say no to overcommitment\n"
        response += "• **Time Management**: Prioritize tasks and delegate when possible\n"
        response += "• **Social Support**: Connect with friends and family regularly\n"
        response += "• **Mindfulness Practice**: 10-15 minutes daily meditation\n\n"
        
        response += "⚠️ **When to Seek Professional Help**:\n"
        response += "• Stress interferes with daily functioning\n"
        response += "• Physical symptoms (headaches, stomach issues)\n"
        response += "• Sleep problems persist for weeks\n"
        response += "• Feeling overwhelmed most days\n"
        
        tips = [
            "Start with one technique and practice it consistently",
            "Identify your personal stress triggers",
            "Create a daily stress-relief routine",
            "Remember that some stress is normal and manageable"
        ]
        
        next_steps = [
            "Try the 4-7-8 breathing technique right now",
            "Identify your top 3 stress triggers",
            "Schedule 10 minutes daily for stress relief"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_sleep_issues(self, message: str, context: UserSessionContext) -> str:
        """Provide sleep optimization guidance"""
        response = "😴 Sleep Optimization Guide\n\n"
        
        response += "🌙 **Sleep Hygiene Fundamentals**:\n\n"
        response += "1. **Consistent Schedule**:\n"
        response += "   - Same bedtime and wake time daily (even weekends)\n"
        response += "   - Aim for 7-9 hours of sleep\n"
        response += "   - Avoid 'catching up' on sleep\n\n"
        
        response += "2. **Bedroom Environment**:\n"
        response += "   - Cool temperature (65-68°F / 18-20°C)\n"
        response += "   - Dark room (blackout curtains, eye mask)\n"
        response += "   - Quiet environment (earplugs, white noise)\n"
        response += "   - Comfortable mattress and pillows\n\n"
        
        response += "3. **Pre-Sleep Routine** (1-2 hours before bed):\n"
        response += "   - Dim lights and avoid screens\n"
        response += "   - Light stretching or reading\n"
        response += "   - Warm bath or shower\n"
        response += "   - Relaxation techniques\n\n"
        
        response += "☕ **What to Avoid**:\n"
        response += "• Caffeine after 2 PM\n"
        response += "• Large meals 3 hours before bed\n"
        response += "• Alcohol (disrupts sleep quality)\n"
        response += "• Intense exercise 4 hours before bed\n"
        response += "• Daytime naps longer than 20 minutes\n\n"
        
        response += "🧘 **If You Can't Fall Asleep**:\n"
        response += "• Don't lie in bed awake for more than 20 minutes\n"
        response += "• Get up and do a quiet, non-stimulating activity\n"
        response += "• Return to bed when you feel sleepy\n"
        response += "• Practice the 4-7-8 breathing technique\n\n"
        
        response += "⚠️ **When to Consult a Doctor**:\n"
        response += "• Chronic insomnia (3+ weeks)\n"
        response += "• Loud snoring or breathing interruptions\n"
        response += "• Excessive daytime sleepiness\n"
        response += "• Sleep issues affecting daily life\n"
        
        tips = [
            "Changes take 2-4 weeks to show full effect",
            "Be patient and consistent with new habits",
            "Track your sleep patterns to identify issues",
            "Consider a sleep diary for 1-2 weeks"
        ]
        
        next_steps = [
            "Set a consistent bedtime starting tonight",
            "Create a 30-minute wind-down routine",
            "Optimize your bedroom environment"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_anxiety_support(self, message: str, context: UserSessionContext) -> str:
        """Provide anxiety management support"""
        response = "🌸 Anxiety Management Support\n\n"
        response += "💙 Remember: Anxiety is treatable, and you're not alone in this experience.\n\n"
        
        response += "🆘 **Immediate Anxiety Relief**:\n\n"
        response += "1. **Box Breathing**:\n"
        response += "   - Inhale for 4 counts\n"
        response += "   - Hold for 4 counts\n"
        response += "   - Exhale for 4 counts\n"
        response += "   - Hold empty for 4 counts\n"
        response += "   - Repeat 5-10 times\n\n"
        
        response += "2. **Grounding Techniques**:\n"
        response += "   - Name 5 things you can see\n"
        response += "   - Feel your feet on the ground\n"
        response += "   - Hold a cold object or splash cold water\n"
        response += "   - Focus on your immediate surroundings\n\n"
        
        response += "3. **Challenge Anxious Thoughts**:\n"
        response += "   - Is this thought realistic?\n"
        response += "   - What would I tell a friend in this situation?\n"
        response += "   - What's the worst that could realistically happen?\n"
        response += "   - How likely is that outcome?\n\n"
        
        response += "🛠️ **Long-term Anxiety Management**:\n\n"
        response += "• **Regular Exercise**: Reduces anxiety hormones naturally\n"
        response += "• **Mindfulness Meditation**: 10-20 minutes daily\n"
        response += "• **Limit Caffeine**: Can worsen anxiety symptoms\n"
        response += "• **Adequate Sleep**: Poor sleep increases anxiety\n"
        response += "• **Social Connection**: Talk to trusted friends/family\n"
        response += "• **Journaling**: Write down worries and thoughts\n\n"
        
        response += "🚨 **Seek Professional Help If**:\n"
        response += "• Anxiety interferes with daily activities\n"
        response += "• Physical symptoms (rapid heartbeat, sweating)\n"
        response += "• Avoiding situations due to anxiety\n"
        response += "• Panic attacks occur regularly\n"
        response += "• Thoughts of self-harm\n\n"
        
        response += "📞 **Crisis Resources**:\n"
        response += "• National Suicide Prevention Lifeline: 988\n"
        response += "• Crisis Text Line: Text HOME to 741741\n"
        response += "• Emergency Services: 911\n"
        
        tips = [
            "Anxiety is your body's alarm system - it's trying to protect you",
            "Practice anxiety management techniques when calm, not just during anxiety",
            "Small, consistent steps are more effective than big changes",
            "Consider therapy - it's highly effective for anxiety"
        ]
        
        next_steps = [
            "Practice box breathing for 5 minutes today",
            "Identify your anxiety triggers",
            "Consider reaching out to a mental health professional"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_mindfulness_guidance(self, message: str, context: UserSessionContext) -> str:
        """Provide mindfulness and meditation guidance"""
        response = "🧘 Mindfulness & Meditation Guide\n\n"
        
        response += "🌟 **What is Mindfulness?**\n"
        response += "Mindfulness is the practice of being fully present and engaged in the current moment, "
        response += "without judgment or distraction.\n\n"
        
        response += "🎯 **Benefits of Regular Practice**:\n"
        response += "• Reduced stress and anxiety\n"
        response += "• Improved focus and concentration\n"
        response += "• Better emotional regulation\n"
        response += "• Enhanced self-awareness\n"
        response += "• Improved sleep quality\n"
        response += "• Lower blood pressure\n\n"
        
        response += "🧘‍♀️ **Simple Meditation Techniques**:\n\n"
        response += "1. **Breath Awareness** (5-20 minutes):\n"
        response += "   - Sit comfortably with eyes closed\n"
        response += "   - Focus on your natural breathing\n"
        response += "   - When mind wanders, gently return to breath\n"
        response += "   - No judgment, just gentle redirection\n\n"
        
        response += "2. **Body Scan** (10-30 minutes):\n"
        response += "   - Lie down comfortably\n"
        response += "   - Start at toes, slowly move attention up body\n"
        response += "   - Notice sensations without trying to change them\n"
        response += "   - Great for relaxation and body awareness\n\n"
        
        response += "3. **Loving-Kindness** (10-20 minutes):\n"
        response += "   - Send good wishes to yourself\n"
        response += "   - Extend to loved ones, neutral people, difficult people\n"
        response += "   - Use phrases like 'May you be happy, may you be peaceful'\n"
        response += "   - Builds compassion and reduces negative emotions\n\n"
        
        response += "📱 **Mindfulness Throughout the Day**:\n"
        response += "• **Mindful Eating**: Pay attention to taste, texture, smell\n"
        response += "• **Walking Meditation**: Focus on each step and breath\n"
        response += "• **Mindful Listening**: Give full attention to sounds around you\n"
        response += "• **Pause Practice**: Take 3 conscious breaths before transitions\n\n"
        
        response += "🎯 **Getting Started**:\n"
        response += "• Start with just 5 minutes daily\n"
        response += "• Choose a consistent time (morning often works best)\n"
        response += "• Use guided meditations initially (apps like Headspace, Calm)\n"
        response += "• Be patient - benefits develop over time\n"
        response += "• Don't judge your practice - there's no 'perfect' meditation\n"
        
        tips = [
            "Consistency matters more than duration",
            "It's normal for your mind to wander - that's not failure",
            "Start small and gradually increase practice time",
            "Find a quiet space but don't worry about perfect conditions"
        ]
        
        next_steps = [
            "Try 5 minutes of breath awareness today",
            "Download a meditation app for guidance",
            "Set a daily reminder for practice time"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_habit_formation(self, message: str, context: UserSessionContext) -> str:
        """Provide habit formation guidance"""
        response = "🔄 Habit Formation & Behavior Change\n\n"
        
        response += "🧠 **How Habits Work** (The Habit Loop):\n"
        response += "1. **Cue**: Environmental trigger\n"
        response += "2. **Routine**: The behavior itself\n"
        response += "3. **Reward**: The benefit you get\n\n"
        
        response += "✅ **Building Good Habits**:\n\n"
        response += "1. **Start Incredibly Small**:\n"
        response += "   - Want to exercise? Start with 1 push-up\n"
        response += "   - Want to meditate? Start with 1 minute\n"
        response += "   - Want to read? Start with 1 page\n\n"
        
        response += "2. **Stack Habits**:\n"
        response += "   - Attach new habit to existing routine\n"
        response += "   - 'After I brush my teeth, I will do 5 squats'\n"
        response += "   - 'After I pour my coffee, I will write 3 gratitudes'\n\n"
        
        response += "3. **Design Your Environment**:\n"
        response += "   - Make good habits obvious and easy\n"
        response += "   - Put workout clothes by your bed\n"
        response += "   - Keep healthy snacks visible\n\n"
        
        response += "4. **Track Your Progress**:\n"
        response += "   - Use a simple habit tracker\n"
        response += "   - Mark an X for each day completed\n"
        response += "   - Celebrate small wins\n\n"
        
        response += "❌ **Breaking Bad Habits**:\n\n"
        response += "1. **Identify Triggers**:\n"
        response += "   - What situations lead to the bad habit?\n"
        response += "   - Emotional states, times, places, people\n\n"
        
        response += "2. **Change the Environment**:\n"
        response += "   - Remove temptations when possible\n"
        response += "   - Make bad habits harder to do\n\n"
        
        response += "3. **Replace, Don't Just Remove**:\n"
        response += "   - Substitute a better behavior\n"
        response += "   - Keep the same cue and reward\n\n"
        
        response += "⏰ **The 21-Day Myth**:\n"
        response += "Reality: Habits take 18-254 days to form (average: 66 days)\n"
        response += "• Simple habits form faster\n"
        response += "• Complex habits take longer\n"
        response += "• Missing one day won't ruin progress\n\n"
        
        response += "🎯 **Habit Success Strategies**:\n"
        response += "• Focus on one habit at a time\n"
        response += "• Be specific about when and where\n"
        response += "• Plan for obstacles and setbacks\n"
        response += "• Find an accountability partner\n"
        response += "• Reward yourself for consistency\n"
        
        tips = [
            "Make it so easy you can't say no",
            "Focus on showing up, not perfect performance",
            "Identity change drives behavior change",
            "Progress, not perfection, is the goal"
        ]
        
        next_steps = [
            "Choose ONE habit to focus on",
            "Make it incredibly small to start",
            "Identify your cue and reward"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_mood_support(self, message: str, context: UserSessionContext) -> str:
        """Provide mood and emotional support"""
        response = "💙 Mood & Emotional Wellness Support\n\n"
        response += "🤗 Remember: It's okay to not be okay sometimes. Your feelings are valid.\n\n"
        
        response += "🌈 **Natural Mood Boosters**:\n\n"
        response += "1. **Physical Activity**:\n"
        response += "   - Even 10 minutes of walking helps\n"
        response += "   - Exercise releases endorphins\n"
        response += "   - Try dancing to your favorite song\n\n"
        
        response += "2. **Sunlight & Nature**:\n"
        response += "   - 15-30 minutes of sunlight daily\n"
        response += "   - Spend time outdoors when possible\n"
        response += "   - Even looking at nature photos helps\n\n"
        
        response += "3. **Social Connection**:\n"
        response += "   - Reach out to a friend or family member\n"
        response += "   - Join a community group or class\n"
        response += "   - Volunteer for a cause you care about\n\n"
        
        response += "4. **Creative Expression**:\n"
        response += "   - Draw, write, sing, or play music\n"
        response += "   - Try adult coloring books\n"
        response += "   - Cook or bake something new\n\n"
        
        response += "🧘 **Emotional Regulation Techniques**:\n\n"
        response += "• **Journaling**: Write about your feelings without judgment\n"
        response += "• **Gratitude Practice**: List 3 things you're grateful for daily\n"
        response += "• **Deep Breathing**: Activates the relaxation response\n"
        response += "• **Progressive Muscle Relaxation**: Releases physical tension\n"
        response += "• **Mindfulness**: Observe emotions without being overwhelmed\n\n"
        
        response += "🛠️ **Daily Mood Maintenance**:\n"
        response += "• Maintain regular sleep schedule\n"
        response += "• Eat nutritious, regular meals\n"
        response += "• Limit alcohol and caffeine\n"
        response += "• Stay hydrated\n"
        response += "• Practice self-compassion\n"
        response += "• Set realistic daily goals\n\n"
        
        response += "🚨 **When to Seek Professional Help**:\n"
        response += "• Persistent sadness for 2+ weeks\n"
        response += "• Loss of interest in activities you used to enjoy\n"
        response += "• Significant changes in sleep or appetite\n"
        response += "• Difficulty concentrating or making decisions\n"
        response += "• Thoughts of self-harm or suicide\n"
        response += "• Mood interferes with work, relationships, or daily life\n\n"
        
        response += "📞 **Crisis Resources**:\n"
        response += "• National Suicide Prevention Lifeline: 988\n"
        response += "• Crisis Text Line: Text HOME to 741741\n"
        response += "• Emergency Services: 911\n"
        
        tips = [
            "Small actions can lead to big mood improvements",
            "Be patient with yourself - healing takes time",
            "Professional help is a sign of strength, not weakness",
            "You don't have to face difficult emotions alone"
        ]
        
        next_steps = [
            "Try one mood-boosting activity today",
            "Consider keeping a mood journal",
            "Reach out to someone you trust"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_general_mental_health(self, message: str, context: UserSessionContext) -> str:
        """Handle general mental health queries"""
        response = f"🧠 Hello! I'm your mental health and wellness specialist.\n\n"
        
        response += "I'm here to support your emotional and psychological well-being. "
        response += "While I can't replace professional therapy, I can provide evidence-based strategies and resources.\n\n"
        
        response += "🌟 **Areas I Can Help With**:\n"
        response += "• Stress management and coping strategies\n"
        response += "• Sleep optimization and insomnia support\n"
        response += "• Anxiety management techniques\n"
        response += "• Mindfulness and meditation guidance\n"
        response += "• Habit formation and behavior change\n"
        response += "• Mood support and emotional wellness\n"
        response += "• Crisis resources and professional referrals\n\n"
        
        response += "💡 **Mental Health Fundamentals**:\n"
        response += "• **Self-Care**: Regular activities that support your well-being\n"
        response += "• **Boundaries**: Protecting your time and energy\n"
        response += "• **Support Systems**: Maintaining healthy relationships\n"
        response += "• **Professional Help**: Therapy and counseling when needed\n"
        response += "• **Lifestyle Factors**: Sleep, exercise, nutrition, and stress management\n\n"
        
        response += "🤝 **Remember**:\n"
        response += "• Mental health is just as important as physical health\n"
        response += "• It's okay to ask for help\n"
        response += "• Small steps can lead to significant improvements\n"
        response += "• You're not alone in your struggles\n"
        
        tips = [
            "Mental health is a journey, not a destination",
            "What works for others might not work for you - that's okay",
            "Consistency in self-care practices is key",
            "Professional support can be incredibly valuable"
        ]
        
        next_steps = [
            "Tell me about any specific mental health concerns",
            "Share what areas you'd like to work on",
            "Let me know how I can best support you"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    def should_handoff(self, message: str, context: UserSessionContext) -> Optional[Tuple[AgentType, str]]:
        """Determine if handoff to human coach is needed for serious mental health concerns"""
        message_lower = message.lower()
        
        # Crisis keywords that require human intervention
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'hurt myself', 'self harm', 'overdose', 'can\'t go on'
        ]
        
        if any(keyword in message_lower for keyword in crisis_keywords):
            return (AgentType.HUMAN_COACH, "Crisis situation requiring immediate human support")
        
        # Severe mental health concerns
        severe_keywords = [
            'severe depression', 'bipolar', 'schizophrenia', 'psychosis',
            'eating disorder', 'addiction', 'substance abuse'
        ]
        
        if any(keyword in message_lower for keyword in severe_keywords):
            return (AgentType.HUMAN_COACH, "Complex mental health condition requiring professional support")
        
        return None
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
