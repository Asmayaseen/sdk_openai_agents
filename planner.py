import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from context import UserSessionContext, AgentType, GoalType
from agents import (
    WellnessAgent,
    NutritionAgent,
    FitnessAgent,
    MentalHealthAgent,
    HumanCoachAgent
)

class WellnessPlanner:
    def __init__(self):
        self.agents = {
            AgentType.WELLNESS: WellnessAgent(),
            AgentType.NUTRITION: NutritionAgent(),
            AgentType.FITNESS: FitnessAgent(),
            AgentType.MENTAL_HEALTH: MentalHealthAgent(),
            AgentType.HUMAN_COACH: HumanCoachAgent()
        }
        
        # Emergency keywords for crisis detection
        self.emergency_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'hurt myself', 'self harm', 'overdose', 'emergency',
            'crisis', 'help me', 'desperate', 'can\'t go on'
        ]
    
    def is_emergency(self, message: str) -> bool:
        """Check if message contains emergency keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.emergency_keywords)
    
    async def handle_emergency(self, message: str, context: UserSessionContext) -> str:
        """Handle emergency situations"""
        emergency_response = """
🚨 EMERGENCY SUPPORT RESOURCES 🚨

If you're in immediate danger, please contact:
• Emergency Services: 911
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741

You are not alone. Professional help is available 24/7.

Would you like me to connect you with a human coach or provide additional mental health resources?
        """
        
        # Log the emergency interaction
        context.add_conversation(message, emergency_response, "emergency_system")
        
        return emergency_response.strip()
    
    def determine_agent(self, message: str, context: UserSessionContext) -> AgentType:
        """Determine which agent should handle the message"""
        message_lower = message.lower()
        
        # Nutrition-related keywords
        nutrition_keywords = [
            'meal', 'diet', 'food', 'nutrition', 'calories', 'recipe',
            'eat', 'hungry', 'protein', 'carbs', 'fat', 'vitamin',
            'supplement', 'weight loss', 'weight gain', 'vegetarian',
            'vegan', 'keto', 'paleo', 'intermittent fasting'
        ]
        
        # Fitness-related keywords
        fitness_keywords = [
            'workout', 'exercise', 'gym', 'fitness', 'training',
            'muscle', 'strength', 'cardio', 'running', 'lifting',
            'yoga', 'pilates', 'sports', 'physical activity',
            'body building', 'endurance', 'flexibility'
        ]
        
        # Mental health keywords
        mental_health_keywords = [
            'stress', 'anxiety', 'depression', 'sleep', 'mood',
            'mental health', 'meditation', 'mindfulness', 'therapy',
            'counseling', 'emotional', 'overwhelmed', 'tired',
            'burnout', 'relaxation', 'breathing', 'panic'
        ]
        
        # Human coach keywords
        human_coach_keywords = [
            'human', 'coach', 'person', 'talk to someone',
            'professional', 'expert', 'counselor', 'therapist',
            'doctor', 'nutritionist', 'trainer', 'specialist'
        ]
        
        # Check for specific agent requests
        if any(keyword in message_lower for keyword in human_coach_keywords):
            return AgentType.HUMAN_COACH
        elif any(keyword in message_lower for keyword in nutrition_keywords):
            return AgentType.NUTRITION
        elif any(keyword in message_lower for keyword in fitness_keywords):
            return AgentType.FITNESS
        elif any(keyword in message_lower for keyword in mental_health_keywords):
            return AgentType.MENTAL_HEALTH
        else:
            return AgentType.WELLNESS
    
    async def run_conversation(
        self,
        messages: List[str],
        context: UserSessionContext,
        streaming: bool = False
    ) -> UserSessionContext:
        """Run a conversation with appropriate agent"""
        
        for message in messages:
            # Determine the appropriate agent
            target_agent = self.determine_agent(message, context)
            
            # Check if we need to hand off to a different agent
            if target_agent != context.current_agent:
                handoff_reason = f"User query requires {target_agent.value} expertise"
                context.log_handoff(
                    from_agent=context.current_agent.value,
                    to_agent=target_agent.value,
                    reason=handoff_reason
                )
                context.current_agent = target_agent
            
            # Get the appropriate agent
            agent = self.agents[context.current_agent]
            
            # Process the message with the agent
            try:
                response = await agent.process_message(message, context)
                
                # Add to conversation history
                context.add_conversation(message, response, context.current_agent.value)
                
                # Check if agent recommends handoff
                handoff_recommendation = agent.should_handoff(message, context)
                if handoff_recommendation:
                    recommended_agent, reason = handoff_recommendation
                    if recommended_agent != context.current_agent:
                        context.log_handoff(
                            from_agent=context.current_agent.value,
                            to_agent=recommended_agent.value,
                            reason=reason
                        )
                        context.current_agent = recommended_agent
                
            except Exception as e:
                error_response = f"I apologize, but I encountered an error processing your request: {str(e)}"
                context.add_conversation(message, error_response, "error")
        
        return context
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of each agent"""
        return {
            agent_type.value: agent.get_capabilities()
            for agent_type, agent in self.agents.items()
        }
    
    def get_conversation_summary(self, context: UserSessionContext) -> str:
        """Generate a summary of the conversation"""
        if not context.conversation_history:
            return "No conversations yet."
        
        total_conversations = len(context.conversation_history)
        agents_used = set(entry['agent_type'] for entry in context.conversation_history)
        handoffs = len(context.handoff_log)
        
        summary = f"""
Conversation Summary:
• Total messages: {total_conversations}
• Agents consulted: {', '.join(agents_used)}
• Agent handoffs: {handoffs}
• Current focus: {context.goal_type.value}
• Session duration: {(datetime.now() - context.session_start).total_seconds():.0f} seconds
        """
        
        return summary.strip()
