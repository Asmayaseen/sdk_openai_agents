"""
Injury Support Agent - Handles physical limitations and injury-related modifications
Provides safe exercise alternatives and recovery support
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# OpenAI Agents SDK imports
from openai_agents import Agent

from context import UserSessionContext

class InjurySupportAgent(Agent[UserSessionContext]):
    """
    Specialized agent for injury support and physical limitations
    Provides safe exercise modifications and recovery guidance
    """
    
    def __init__(self):
        super().__init__(
            name="InjurySupportAgent",
            instructions=self._get_instructions()
        )
        
        # Common injuries and modifications
        self.injury_modifications = {
            'back_pain': {
                'safe_exercises': [
                    'Walking on flat surfaces',
                    'Swimming (if comfortable)',
                    'Gentle stretching',
                    'Pelvic tilts',
                    'Knee-to-chest stretches',
                    'Cat-cow stretches'
                ],
                'exercises_to_avoid': [
                    'Heavy lifting',
                    'High-impact activities',
                    'Twisting movements',
                    'Toe touches',
                    'Sit-ups with straight legs'
                ],
                'modifications': [
                    'Use proper lifting technique',
                    'Maintain neutral spine position',
                    'Start with low-impact activities',
                    'Focus on core strengthening',
                    'Use heat/ice as recommended'
                ]
            },
            'knee_pain': {
                'safe_exercises': [
                    'Swimming',
                    'Water walking',
                    'Stationary cycling (low resistance)',
                    'Upper body strength training',
                    'Seated exercises',
                    'Gentle yoga'
                ],
                'exercises_to_avoid': [
                    'Running on hard surfaces',
                    'Deep squats',
                    'Lunges (if painful)',
                    'High-impact jumping',
                    'Stair climbing (if painful)'
                ],
                'modifications': [
                    'Use proper footwear',
                    'Avoid activities that cause pain',
                    'Strengthen quadriceps and hamstrings',
                    'Focus on range of motion',
                    'Consider knee support if recommended'
                ]
            },
            'shoulder_pain': {
                'safe_exercises': [
                    'Walking',
                    'Lower body exercises',
                    'Gentle shoulder rolls',
                    'Pendulum exercises',
                    'Wall slides',
                    'Isometric exercises'
                ],
                'exercises_to_avoid': [
                    'Overhead pressing',
                    'Pull-ups/chin-ups',
                    'Heavy lifting above shoulder level',
                    'Aggressive stretching',
                    'Contact sports'
                ],
                'modifications': [
                    'Keep movements below shoulder level',
                    'Use lighter weights',
                    'Focus on pain-free range of motion',
                    'Strengthen rotator cuff muscles',
                    'Maintain good posture'
                ]
            },
            'ankle_injury': {
                'safe_exercises': [
                    'Upper body strength training',
                    'Seated exercises',
                    'Swimming (if comfortable)',
                    'Ankle circles and flexion',
                    'Calf raises (if pain-free)',
                    'Balance exercises (when appropriate)'
                ],
                'exercises_to_avoid': [
                    'Running',
                    'Jumping activities',
                    'Sports with cutting movements',
                    'Uneven surface activities',
                    'High-impact exercises'
                ],
                'modifications': [
                    'Use ankle support if recommended',
                    'Focus on non-weight bearing exercises initially',
                    'Progress gradually to weight-bearing',
                    'Work on balance and proprioception',
                    'Strengthen surrounding muscles'
                ]
            },
            'wrist_injury': {
                'safe_exercises': [
                    'Walking',
                    'Lower body exercises',
                    'Cardio machines without hand support',
                    'Gentle wrist stretches',
                    'Finger exercises',
                    'Elbow and shoulder exercises'
                ],
                'exercises_to_avoid': [
                    'Push-ups',
                    'Planks',
                    'Weight-bearing on hands',
                    'Heavy gripping exercises',
                    'Racquet sports'
                ],
                'modifications': [
                    'Use wrist supports if recommended',
                    'Avoid weight-bearing on hands',
                    'Focus on pain-free movements',
                    'Strengthen forearm muscles',
                    'Maintain wrist in neutral position'
                ]
            }
        }
        
        # Recovery phases and guidelines
        self.recovery_phases = {
            'acute': {
                'timeframe': '0-72 hours post-injury',
                'focus': 'Protection, rest, ice, compression, elevation (PRICE)',
                'activities': 'Gentle range of motion if pain-free',
                'avoid': 'Aggressive movement, heat, alcohol, running, massage'
            },
            'subacute': {
                'timeframe': '3 days to 6 weeks',
                'focus': 'Gentle movement, pain-free exercises',
                'activities': 'Progressive range of motion, light strengthening',
                'avoid': 'Activities that increase pain or swelling'
            },
            'chronic': {
                'timeframe': 'Beyond 6 weeks',
                'focus': 'Strengthening, functional movement, return to activity',
                'activities': 'Progressive loading, sport-specific training',
                'avoid': 'Sudden increases in activity level'
            }
        }
    
    def _get_instructions(self) -> str:
        """Get agent instructions"""
        return """
        You are an Injury Support Agent specializing in safe exercise modifications.
        
        Your role is to:
        1. Provide safe exercise alternatives for common injuries
        2. Educate about injury recovery phases
        3. Recommend appropriate modifications for physical limitations
        4. Emphasize the importance of professional medical care
        5. Promote safe return to activity
        
        CRITICAL: Always emphasize that serious injuries require professional 
        medical evaluation. You provide general guidance but cannot diagnose 
        or treat injuries. Safety is the absolute priority.
        """
    
    async def process_message(self, message: str, context: UserSessionContext) -> str:
        """Process injury support requests"""
        try:
            # Simulate async processing
            await asyncio.sleep(0.4)
            
            # Log the handoff
            context.add_handoff_log(
                from_agent="HealthWellnessAgent",
                to_agent="InjurySupportAgent",
                reason="User has injury or physical limitation requiring specialized exercise modifications"
            )
            
            # Store injury information in context
            context.injury_notes = message
            
            # Determine injury type and severity
            injury_assessment = self._assess_injury_type(message, context)
            
            # Generate appropriate response
            response = await self._generate_injury_support_response(injury_assessment, message, context)
            
            return response
            
        except Exception as e:
            return f"❌ I encountered an error while providing injury support guidance. Please consult with a healthcare provider or physical therapist for personalized advice. Error: {str(e)}"
    
    def _assess_injury_type(self, message: str, context: UserSessionContext) -> Dict[str, Any]:
        """Assess injury type and severity from user input"""
        message_lower = message.lower()
        
        # Determine injury location
        injury_location = 'general'
        if any(word in message_lower for word in ['back', 'spine', 'lower back', 'upper back']):
            injury_location = 'back_pain'
        elif any(word in message_lower for word in ['knee', 'kneecap', 'patella']):
            injury_location = 'knee_pain'
        elif any(word in message_lower for word in ['shoulder', 'rotator cuff']):
            injury_location = 'shoulder_pain'
        elif any(word in message_lower for word in ['ankle', 'foot']):
            injury_location = 'ankle_injury'
        elif any(word in message_lower for word in ['wrist', 'hand']):
            injury_location = 'wrist_injury'
        elif any(word in message_lower for word in ['hip', 'groin']):
            injury_location = 'hip_injury'
        elif any(word in message_lower for word in ['neck', 'cervical']):
            injury_location = 'neck_injury'
        
        # Assess severity indicators
        severity = 'mild'
        if any(word in message_lower for word in ['severe', 'intense', 'unbearable', 'can\'t move']):
            severity = 'severe'
        elif any(word in message_lower for word in ['moderate', 'significant', 'limiting']):
            severity = 'moderate'
        
        # Determine if acute or chronic
        chronicity = 'unknown'
        if any(word in message_lower for word in ['just happened', 'today', 'yesterday', 'recent']):
            chronicity = 'acute'
        elif any(word in message_lower for word in ['chronic', 'ongoing', 'months', 'years']):
            chronicity = 'chronic'
        elif any(word in message_lower for word in ['weeks', 'few weeks']):
            chronicity = 'subacute'
        
        # Check for red flags
        red_flags = []
        if any(word in message_lower for word in ['numbness', 'tingling', 'weakness']):
            red_flags.append('neurological_symptoms')
        if any(word in message_lower for word in ['fever', 'infection', 'swelling']):
            red_flags.append('inflammatory_signs')
        if any(word in message_lower for word in ['can\'t bear weight', 'can\'t walk']):
            red_flags.append('functional_limitation')
        
        return {
            'location': injury_location,
            'severity': severity,
            'chronicity': chronicity,
            'red_flags': red_flags,
            'needs_immediate_care': len(red_flags) > 0 or severity == 'severe'
        }
    
    async def _generate_injury_support_response(self, assessment: Dict[str, Any], message: str, context: UserSessionContext) -> str:
        """Generate injury support response based on assessment"""
        
        # Check if immediate medical care is needed
        if assessment['needs_immediate_care']:
            return await self._handle_urgent_injury(assessment, message, context)
        
        # Provide injury-specific guidance
        if assessment['location'] in self.injury_modifications:
            return await self._handle_specific_injury(assessment, message, context)
        else:
            return await self._handle_general_injury(assessment, message, context)
    
    async def _handle_urgent_injury(self, assessment: Dict[str, Any], message: str, context: UserSessionContext) -> str:
        """Handle injuries that need immediate medical attention"""
        
        response = f"🚨 **URGENT: Immediate Medical Attention Recommended**\n\n"
        response += f"Hi {context.name}, based on your description, I'm concerned about your injury and strongly recommend seeking immediate medical care.\n\n"
        
        response += "⚠️ **Seek Emergency Care Immediately If You Have**:\n"
        response += "• Severe pain that doesn't improve with rest\n"
        response += "• Numbness, tingling, or weakness\n"
        response += "• Inability to bear weight or use the injured area\n"
        response += "• Signs of infection (fever, warmth, redness)\n"
        response += "• Deformity or suspected fracture\n"
        response += "• Loss of function in the injured area\n\n"
        
        response += "🏥 **Where to Seek Care**:\n"
        response += "• **Emergency Room**: For severe injuries, suspected fractures, or neurological symptoms\n"
        response += "• **Urgent Care**: For moderate injuries that need prompt attention\n"
        response += "• **Your Doctor**: For evaluation and referral to specialists\n\n"
        
        response += "🩹 **Immediate Care While Seeking Medical Attention**:\n"
        response += "• **Rest**: Avoid using the injured area\n"
        response += "• **Ice**: Apply for 15-20 minutes every 2-3 hours (if no contraindications)\n"
        response += "• **Compression**: Use elastic bandage if appropriate\n"
        response += "• **Elevation**: Raise injured area above heart level if possible\n"
        response += "• **Pain Management**: Over-the-counter pain relievers as directed\n\n"
        
        response += "❌ **Avoid These Until Seen by Medical Professional**:\n"
        response += "• Continuing activities that cause pain\n"
        response += "• Applying heat to acute injuries\n"
        response += "• Aggressive stretching or massage\n"
        response += "• Ignoring worsening symptoms\n\n"
        
        response += "📞 **Important Numbers**:\n"
        response += "• **Emergency Services**: 911\n"
        response += "• **Your Primary Care Doctor**\n"
        response += "• **Urgent Care Centers** in your area\n\n"
        
        response += "Please prioritize getting medical evaluation for your injury. Your safety and proper healing are most important! 🏥"
        
        return response
    
    async def _handle_specific_injury(self, assessment: Dict[str, Any], message: str, context: UserSessionContext) -> str:
        """Handle specific injury types with targeted guidance"""
        
        injury_location = assessment['location']
        injury_info = self.injury_modifications[injury_location]
        
        response = f"🩹 **{injury_location.replace('_', ' ').title()} Support**\n\n"
        response += f"Hi {context.name}, I understand you're dealing with {injury_location.replace('_', ' ')}. Let me provide specialized guidance for safe exercise modifications.\n\n"
        
        response += "⚠️ **IMPORTANT MEDICAL DISCLAIMER**:\n"
        response += "• This guidance is educational and general in nature\n"
        response += "• Always consult healthcare providers for proper diagnosis\n"
        response += "• Stop any activity that increases pain\n"
        response += "• Consider physical therapy for comprehensive care\n\n"
        
        # Recovery phase guidance
        if assessment['chronicity'] in self.recovery_phases:
            phase_info = self.recovery_phases[assessment['chronicity']]
            response += f"📅 **Recovery Phase**: {assessment['chronicity'].title()}\n"
            response += f"• **Timeframe**: {phase_info['timeframe']}\n"
            response += f"• **Focus**: {phase_info['focus']}\n"
            response += f"• **Appropriate Activities**: {phase_info['activities']}\n"
            response += f"• **Avoid**: {phase_info['avoid']}\n\n"
        
        response += "✅ **Safe Exercises You Can Try**:\n"
        for exercise in injury_info['safe_exercises']:
            response += f"• {exercise}\n"
        response += "\n"
        
        response += "❌ **Exercises to Avoid**:\n"
        for exercise in injury_info['exercises_to_avoid']:
            response += f"• {exercise}\n"
        response += "\n"
        
        response += "🔧 **Exercise Modifications**:\n"
        for modification in injury_info['modifications']:
            response += f"• {modification}\n"
        response += "\n"
        
        # Specific guidance based on injury location
        if injury_location == 'back_pain':
            response += await self._add_back_pain_specifics()
        elif injury_location == 'knee_pain':
            response += await self._add_knee_pain_specifics()
        elif injury_location == 'shoulder_pain':
            response += await self._add_shoulder_pain_specifics()
        
        response += "🎯 **Progressive Return to Activity**:\n"
        response += "1. **Start with pain-free movements**\n"
        response += "2. **Gradually increase activity level**\n"
        response += "3. **Monitor symptoms closely**\n"
        response += "4. **Don't rush the process**\n"
        response += "5. **Consider professional guidance**\n\n"
        
        response += "👨‍⚕️ **Professional Support Options**:\n"
        response += "• **Physical Therapist**: Comprehensive rehabilitation\n"
        response += "• **Sports Medicine Doctor**: Specialized injury care\n"
        response += "• **Orthopedic Specialist**: For complex or persistent issues\n"
        response += "• **Massage Therapist**: For muscle tension and recovery\n\n"
        
        response += "🚨 **Seek Medical Care If**:\n"
        response += "• Pain worsens or doesn't improve\n"
        response += "• New symptoms develop\n"
        response += "• You experience numbness or weakness\n"
        response += "• Function doesn't return to normal\n\n"
        
        response += "Remember: Healing takes time, and it's better to progress slowly than to re-injure yourself! 🌟"
        
        return response
    
    async def _add_back_pain_specifics(self) -> str:
        """Add back pain specific guidance"""
        specifics = "🔙 **Back Pain Specific Guidance**:\n\n"
        specifics += "**Daily Activities**:\n"
        specifics += "• Use proper lifting technique (bend knees, not back)\n"
        specifics += "• Sleep with pillow between knees if side sleeping\n"
        specifics += "• Take frequent breaks from sitting\n"
        specifics += "• Use ergonomic workstation setup\n\n"
        
        specifics += "**Gentle Stretches** (if pain-free):\n"
        specifics += "• Knee-to-chest stretch\n"
        specifics += "• Pelvic tilts\n"
        specifics += "• Cat-cow stretches\n"
        specifics += "• Gentle spinal twists\n\n"
        
        return specifics
    
    async def _add_knee_pain_specifics(self) -> str:
        """Add knee pain specific guidance"""
        specifics = "🦵 **Knee Pain Specific Guidance**:\n\n"
        specifics += "**Strengthening Focus**:\n"
        specifics += "• Quadriceps strengthening (straight leg raises)\n"
        specifics += "• Hamstring strengthening\n"
        specifics += "• Glute strengthening\n"
        specifics += "• Calf strengthening\n\n"
        
        specifics += "**Activity Modifications**:\n"
        specifics += "• Use handrails on stairs\n"
        specifics += "• Avoid deep squatting\n"
        specifics += "• Choose low-impact activities\n"
        specifics += "• Consider knee support during activity\n\n"
        
        return specifics
    
    async def _add_shoulder_pain_specifics(self) -> str:
        """Add shoulder pain specific guidance"""
        specifics = "🤲 **Shoulder Pain Specific Guidance**:\n\n"
        specifics += "**Range of Motion Exercises**:\n"
        specifics += "• Pendulum swings\n"
        specifics += "• Wall slides\n"
        specifics += "• Cross-body arm stretches\n"
        specifics += "• Gentle shoulder rolls\n\n"
        
        specifics += "**Daily Activity Tips**:\n"
        specifics += "• Avoid reaching overhead\n"
        specifics += "• Sleep on uninjured side\n"
        specifics += "• Use both hands for lifting\n"
        specifics += "• Maintain good posture\n\n"
        
        return specifics
    
    async def _handle_general_injury(self, assessment: Dict[str, Any], message: str, context: UserSessionContext) -> str:
        """Handle general injury support"""
        
        response = f"🩹 **General Injury Support**\n\n"
        response += f"Hi {context.name}, I understand you're dealing with an injury or physical limitation. Let me provide general guidance for safe exercise modifications.\n\n"
        
        response += "⚠️ **IMPORTANT SAFETY PRINCIPLES**:\n"
        response += "• **Listen to your body** - pain is a warning signal\n"
        response += "• **Start slowly** and progress gradually\n"
        response += "• **Stop if pain increases** during or after activity\n"
        response += "• **Seek professional help** for proper diagnosis and treatment\n\n"
        
        response += "🏃‍♀️ **General Exercise Modifications**:\n\n"
        response += "**Low-Impact Alternatives**:\n"
        response += "• Walking instead of running\n"
        response += "• Swimming or water exercises\n"
        response += "• Stationary cycling\n"
        response += "• Elliptical machine\n"
        response += "• Chair exercises\n\n"
        
        response += "**Strength Training Modifications**:\n"
        response += "• Use lighter weights\n"
        response += "• Focus on pain-free range of motion\n"
        response += "• Try resistance bands instead of weights\n"
        response += "• Work around the injured area\n"
        response += "• Emphasize proper form over intensity\n\n"
        
        response += "**Flexibility and Mobility**:\n"
        response += "• Gentle stretching within pain-free range\n"
        response += "• Hold stretches for 15-30 seconds\n"
        response += "• Avoid bouncing or aggressive stretching\n"
        response += "• Focus on maintaining mobility\n\n"
        
        response += "🔄 **RICE Protocol for Acute Injuries**:\n"
        response += "• **Rest**: Avoid activities that cause pain\n"
        response += "• **Ice**: Apply for 15-20 minutes every 2-3 hours\n"
        response += "• **Compression**: Use elastic bandage if appropriate\n"
        response += "• **Elevation**: Raise injured area above heart level\n\n"
        
        response += "📈 **Progressive Return to Activity**:\n"
        response += "1. **Phase 1**: Rest and protect the injured area\n"
        response += "2. **Phase 2**: Gentle range of motion exercises\n"
        response += "3. **Phase 3**: Light strengthening exercises\n"
        response += "4. **Phase 4**: Functional movement patterns\n"
        response += "5. **Phase 5**: Gradual return to full activity\n\n"
        
        response += "🚨 **Red Flags - Seek Medical Care If**:\n"
        response += "• Severe or worsening pain\n"
        response += "• Numbness, tingling, or weakness\n"
        response += "• Inability to bear weight or use the area\n"
        response += "• Signs of infection (fever, warmth, redness)\n"
        response += "• No improvement after several days\n\n"
        
        response += "👨‍⚕️ **Professional Support Team**:\n"
        response += "• **Primary Care Doctor**: Initial evaluation and referrals\n"
        response += "• **Physical Therapist**: Rehabilitation and exercise prescription\n"
        response += "• **Sports Medicine Doctor**: Specialized injury care\n"
        response += "• **Orthopedic Specialist**: For complex musculoskeletal issues\n\n"
        
        response += "💡 **Remember**:\n"
        response += "• Injuries heal at different rates for different people\n"
        response += "• Patience is key to proper recovery\n"
        response += "• Professional guidance can speed recovery and prevent re-injury\n"
        response += "• Staying active within safe limits is usually beneficial\n\n"
        
        response += "Could you share more specific details about your injury so I can provide more targeted guidance?"
        
        return response
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "Safe exercise modifications for common injuries",
            "Recovery phase guidance and education",
            "Low-impact exercise alternatives",
            "Injury prevention strategies",
            "Professional referral recommendations",
            "RICE protocol education",
            "Progressive return-to-activity planning",
            "Red flag identification for urgent care"
        ]
