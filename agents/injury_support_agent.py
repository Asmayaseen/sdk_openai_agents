"""
Injury Support Agent - Handles physical limitations and injury-related modifications.
Provides safe exercise alternatives and recovery support.
"""
import asyncio
from typing import AsyncGenerator, Dict, Any, List

from agents.base import BaseAgent
from context import UserSessionContext

class InjurySupportAgent(BaseAgent):
    """
    Specialized agent for injury support and physical limitations.
    Streams safe exercise modifications and recovery guidance.
    """
    def __init__(self):
        super().__init__(
            name="injury_support",
            description="Specialized agent for injury support and exercise modifications.",
            system_prompt=self._get_instructions()
        )
        self.injury_modifications = {
            'back_pain': {
                'safe_exercises': [
                    'Walking on flat surfaces', 'Swimming (if comfortable)', 'Gentle stretching',
                    'Pelvic tilts', 'Knee-to-chest stretches', 'Cat-cow stretches'
                ],
                'exercises_to_avoid': [
                    'Heavy lifting','High-impact activities','Twisting movements',
                    'Toe touches', 'Sit-ups with straight legs'
                ],
                'modifications': [
                    'Use proper lifting technique','Maintain neutral spine position',
                    'Start with low-impact activities','Focus on core strengthening','Use heat/ice as recommended'
                ]
            },
            'knee_pain': {
                'safe_exercises': [
                    'Swimming','Water walking','Stationary cycling (low resistance)',
                    'Upper body strength training','Seated exercises','Gentle yoga'
                ],
                'exercises_to_avoid': [
                    'Running on hard surfaces','Deep squats','Lunges (if painful)',
                    'High-impact jumping','Stair climbing (if painful)'
                ],
                'modifications': [
                    'Use proper footwear','Avoid activities that cause pain',
                    'Strengthen quadriceps and hamstrings','Focus on range of motion',
                    'Consider knee support if recommended'
                ]
            },
            'shoulder_pain': {
                'safe_exercises': [
                    'Walking','Lower body exercises','Gentle shoulder rolls',
                    'Pendulum exercises','Wall slides','Isometric exercises'
                ],
                'exercises_to_avoid': [
                    'Overhead pressing','Pull-ups/chin-ups','Heavy lifting above shoulder level',
                    'Aggressive stretching','Contact sports'
                ],
                'modifications': [
                    'Keep movements below shoulder level','Use lighter weights',
                    'Focus on pain-free range of motion','Strengthen rotator cuff muscles','Maintain good posture'
                ]
            },
            'ankle_injury': {
                'safe_exercises': [
                    'Upper body strength training','Seated exercises','Swimming (if comfortable)',
                    'Ankle circles and flexion','Calf raises (if pain-free)','Balance exercises (when appropriate)'
                ],
                'exercises_to_avoid': [
                    'Running','Jumping activities','Sports with cutting movements',
                    'Uneven surface activities','High-impact exercises'
                ],
                'modifications': [
                    'Use ankle support if recommended','Focus on non-weight bearing exercises initially',
                    'Progress gradually to weight-bearing','Work on balance and proprioception','Strengthen surrounding muscles'
                ]
            },
            'wrist_injury': {
                'safe_exercises': [
                    'Walking','Lower body exercises','Cardio machines without hand support',
                    'Gentle wrist stretches','Finger exercises','Elbow and shoulder exercises'
                ],
                'exercises_to_avoid': [
                    'Push-ups','Planks','Weight-bearing on hands','Heavy gripping exercises','Racquet sports'
                ],
                'modifications': [
                    'Use wrist supports if recommended','Avoid weight-bearing on hands',
                    'Focus on pain-free movements','Strengthen forearm muscles','Maintain wrist in neutral position'
                ]
            }
        }
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
        return (
            "You are an Injury Support Agent specializing in safe exercise modifications.\n\n"
            "Your role is to:\n"
            "1. Provide safe exercise alternatives for common injuries\n"
            "2. Educate about injury recovery phases\n"
            "3. Recommend appropriate modifications for physical limitations\n"
            "4. Emphasize the importance of professional medical care\n"
            "5. Promote safe return to activity\n\n"
            "CRITICAL: Always emphasize that serious injuries require professional medical evaluation. "
            "You provide general guidance but cannot diagnose or treat injuries. Safety is the absolute priority."
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        await asyncio.sleep(0.2)
        ctx = self.context
        if ctx:
            ctx.injury_notes = message
            ctx.log_handoff(
                from_agent="wellness",
                to_agent="injury_support",
                reason="User has injury or physical limitation requiring exercise modifications",
                context_snapshot=ctx.dict()
            )

        assessment = self._assess_injury_type(message)
        if assessment['needs_immediate_care']:
            response = await self._handle_urgent_injury(assessment)
        elif assessment['location'] in self.injury_modifications:
            response = await self._handle_specific_injury(assessment)
        else:
            response = await self._handle_general_injury(assessment)
        for para in response.strip().split("\n\n"):
            yield para + "\n\n"

    def _assess_injury_type(self, message: str) -> Dict[str, Any]:
        msg = message.lower()
        injury_location = 'general'
        if any(word in msg for word in ['back', 'spine', 'lower back', 'upper back']):
            injury_location = 'back_pain'
        elif any(word in msg for word in ['knee', 'kneecap', 'patella']):
            injury_location = 'knee_pain'
        elif any(word in msg for word in ['shoulder', 'rotator cuff']):
            injury_location = 'shoulder_pain'
        elif any(word in msg for word in ['ankle', 'foot']):
            injury_location = 'ankle_injury'
        elif any(word in msg for word in ['wrist', 'hand']):
            injury_location = 'wrist_injury'
        elif any(word in msg for word in ['hip', 'groin']):
            injury_location = 'hip_injury'
        elif any(word in msg for word in ['neck', 'cervical']):
            injury_location = 'neck_injury'
        severity = 'mild'
        if any(word in msg for word in ['severe', 'intense', 'unbearable', 'can\'t move']):
            severity = 'severe'
        elif any(word in msg for word in ['moderate', 'significant', 'limiting']):
            severity = 'moderate'
        chronicity = 'unknown'
        if any(word in msg for word in ['just happened', 'today', 'yesterday', 'recent']):
            chronicity = 'acute'
        elif any(word in msg for word in ['chronic', 'ongoing', 'months', 'years']):
            chronicity = 'chronic'
        elif any(word in msg for word in ['weeks', 'few weeks']):
            chronicity = 'subacute'
        red_flags = []
        if any(word in msg for word in ['numbness', 'tingling', 'weakness']):
            red_flags.append('neurological_symptoms')
        if any(word in msg for word in ['fever', 'infection', 'swelling']):
            red_flags.append('inflammatory_signs')
        if any(word in msg for word in ['can\'t bear weight', 'can\'t walk']):
            red_flags.append('functional_limitation')
        return {
            'location': injury_location,
            'severity': severity,
            'chronicity': chronicity,
            'red_flags': red_flags,
            'needs_immediate_care': len(red_flags) > 0 or severity == 'severe'
        }

    async def _handle_urgent_injury(self, assessment: Dict[str, Any]) -> str:
        ctx = self.context
        return (
            f"🚨 **URGENT: Immediate Medical Attention Recommended**\n\n"
            f"Hi {ctx.name}, based on your description, I'm concerned about your injury and strongly recommend seeking immediate medical care.\n\n"
            "⚠️ **Seek Emergency Care Immediately If You Have**:\n"
            "• Severe pain that doesn't improve with rest\n"
            "• Numbness, tingling, or weakness\n"
            "• Inability to bear weight or use the injured area\n"
            "• Signs of infection (fever, warmth, redness)\n"
            "• Deformity or suspected fracture\n"
            "• Loss of function in the injured area\n\n"
            "🏥 **Where to Seek Care**:\n"
            "• **Emergency Room**: For severe injuries, suspected fractures, or neurological symptoms\n"
            "• **Urgent Care**: For moderate injuries that need prompt attention\n"
            "• **Your Doctor**: For evaluation and referral to specialists\n\n"
            "🩹 **Immediate Care While Seeking Medical Attention**:\n"
            "• **Rest**: Avoid using the injured area\n"
            "• **Ice**: Apply for 15-20 minutes every 2-3 hours (if no contraindications)\n"
            "• **Compression**: Use elastic bandage if appropriate\n"
            "• **Elevation**: Raise injured area above heart level if possible\n"
            "• **Pain Management**: Over-the-counter pain relievers as directed\n\n"
            "❌ **Avoid These Until Seen by Medical Professional**:\n"
            "• Continuing activities that cause pain\n"
            "• Applying heat to acute injuries\n"
            "• Aggressive stretching or massage\n"
            "• Ignoring worsening symptoms\n\n"
            "📞 **Important Numbers**:\n"
            "• **Emergency Services**: 911\n"
            "• **Your Primary Care Doctor**\n"
            "• **Urgent Care Centers** in your area\n\n"
            "Please prioritize getting medical evaluation for your injury. Your safety and proper healing are most important! 🏥"
        )

    async def _handle_specific_injury(self, assessment: Dict[str, Any]) -> str:
        ctx = self.context
        injury_location = assessment['location']
        injury_info = self.injury_modifications[injury_location]
        response = (
            f"🩹 **{injury_location.replace('_', ' ').title()} Support**\n\n"
            f"Hi {ctx.name}, I understand you're dealing with {injury_location.replace('_', ' ')}. Let me provide specialized guidance for safe exercise modifications.\n\n"
            "⚠️ **IMPORTANT MEDICAL DISCLAIMER**:\n"
            "• This guidance is educational and general in nature\n"
            "• Always consult healthcare providers for proper diagnosis\n"
            "• Stop any activity that increases pain\n"
            "• Consider physical therapy for comprehensive care\n\n"
        )

        if assessment['chronicity'] in self.recovery_phases:
            phase_info = self.recovery_phases[assessment['chronicity']]
            response += (
                f"📅 **Recovery Phase**: {assessment['chronicity'].title()}\n"
                f"• **Timeframe**: {phase_info['timeframe']}\n"
                f"• **Focus**: {phase_info['focus']}\n"
                f"• **Appropriate Activities**: {phase_info['activities']}\n"
                f"• **Avoid**: {phase_info['avoid']}\n\n"
            )
        response += "✅ **Safe Exercises You Can Try**:\n" + "".join(f"• {x}\n" for x in injury_info['safe_exercises']) + "\n"
        response += "❌ **Exercises to Avoid**:\n" + "".join(f"• {x}\n" for x in injury_info['exercises_to_avoid']) + "\n"
        response += "🔧 **Exercise Modifications**:\n" + "".join(f"• {x}\n" for x in injury_info['modifications']) + "\n"

        if injury_location == 'back_pain':
            response += await self._add_back_pain_specifics()
        elif injury_location == 'knee_pain':
            response += await self._add_knee_pain_specifics()
        elif injury_location == 'shoulder_pain':
            response += await self._add_shoulder_pain_specifics()

        response += (
            "🎯 **Progressive Return to Activity**:\n"
            "1. **Start with pain-free movements**\n"
            "2. **Gradually increase activity level**\n"
            "3. **Monitor symptoms closely**\n"
            "4. **Don't rush the process**\n"
            "5. **Consider professional guidance**\n\n"
            "👨‍⚕️ **Professional Support Options**:\n"
            "• **Physical Therapist**: Comprehensive rehabilitation\n"
            "• **Sports Medicine Doctor**: Specialized injury care\n"
            "• **Orthopedic Specialist**: For complex or persistent issues\n"
            "• **Massage Therapist**: For muscle tension and recovery\n\n"
            "🚨 **Seek Medical Care If**:\n"
            "• Pain worsens or doesn't improve\n"
            "• New symptoms develop\n"
            "• You experience numbness or weakness\n"
            "• Function doesn't return to normal\n\n"
            "Remember: Healing takes time, and it's better to progress slowly than to re-injure yourself! 🌟"
        )
        return response

    async def _add_back_pain_specifics(self) -> str:
        return (
            "🔙 **Back Pain Specific Guidance**:\n\n"
            "**Daily Activities**:\n"
            "• Use proper lifting technique (bend knees, not back)\n"
            "• Sleep with pillow between knees if side sleeping\n"
            "• Take frequent breaks from sitting\n"
            "• Use ergonomic workstation setup\n\n"
            "**Gentle Stretches** (if pain-free):\n"
            "• Knee-to-chest stretch\n"
            "• Pelvic tilts\n"
            "• Cat-cow stretches\n"
            "• Gentle spinal twists\n\n"
        )

    async def _add_knee_pain_specifics(self) -> str:
        return (
            "🦵 **Knee Pain Specific Guidance**:\n\n"
            "**Strengthening Focus**:\n"
            "• Quadriceps strengthening (straight leg raises)\n"
            "• Hamstring strengthening\n"
            "• Glute strengthening\n"
            "• Calf strengthening\n\n"
            "**Activity Modifications**:\n"
            "• Use handrails on stairs\n"
            "• Avoid deep squatting\n"
            "• Choose low-impact activities\n"
            "• Consider knee support during activity\n\n"
        )

    async def _add_shoulder_pain_specifics(self) -> str:
        return (
            "🤲 **Shoulder Pain Specific Guidance**:\n\n"
            "**Range of Motion Exercises**:\n"
            "• Pendulum swings\n"
            "• Wall slides\n"
            "• Cross-body arm stretches\n"
            "• Gentle shoulder rolls\n\n"
            "**Daily Activity Tips**:\n"
            "• Avoid reaching overhead\n"
            "• Sleep on uninjured side\n"
            "• Use both hands for lifting\n"
            "• Maintain good posture\n\n"
        )

    async def _handle_general_injury(self, assessment: Dict[str, Any]) -> str:
        ctx = self.context
        response = (
            "🩹 **General Injury Support**\n\n"
            f"Hi {ctx.name}, I understand you're dealing with an injury or physical limitation. Let me provide general guidance for safe exercise modifications.\n\n"
            "⚠️ **IMPORTANT SAFETY PRINCIPLES**:\n"
            "• **Listen to your body** - pain is a warning signal\n"
            "• **Start slowly** and progress gradually\n"
            "• **Stop if pain increases** during or after activity\n"
            "• **Seek professional help** for proper diagnosis and treatment\n\n"
            "🏃‍♀️ **General Exercise Modifications**:\n\n"
            "**Low-Impact Alternatives**:\n"
            "• Walking instead of running\n"
            "• Swimming or water exercises\n"
            "• Stationary cycling\n"
            "• Elliptical machine\n"
            "• Chair exercises\n\n"
            "**Strength Training Modifications**:\n"
            "• Use lighter weights\n"
            "• Focus on pain-free range of motion\n"
            "• Try resistance bands instead of weights\n"
            "• Work around the injured area\n"
            "• Emphasize proper form over intensity\n\n"
            "**Flexibility and Mobility**:\n"
            "• Gentle stretching within pain-free range\n"
            "• Hold stretches for 15-30 seconds\n"
            "• Avoid bouncing or aggressive stretching\n"
            "• Focus on maintaining mobility\n\n"
            "🔄 **RICE Protocol for Acute Injuries**:\n"
            "• **Rest**: Avoid activities that cause pain\n"
            "• **Ice**: Apply for 15-20 minutes every 2-3 hours\n"
            "• **Compression**: Use elastic bandage if appropriate\n"
            "• **Elevation**: Raise injured area above heart level\n\n"
            "📈 **Progressive Return to Activity**:\n"
            "1. **Phase 1**: Rest and protect the injured area\n"
            "2. **Phase 2**: Gentle range of motion exercises\n"
            "3. **Phase 3**: Light strengthening exercises\n"
            "4. **Phase 4**: Functional movement patterns\n"
            "5. **Phase 5**: Gradual return to full activity\n\n"
            "🚨 **Red Flags - Seek Medical Care If**:\n"
            "• Severe or worsening pain\n"
            "• Numbness, tingling, or weakness\n"
            "• Inability to bear weight or use the area\n"
            "• Signs of infection (fever, warmth, redness)\n"
            "• No improvement after several days\n\n"
            "👨‍⚕️ **Professional Support Team**:\n"
            "• **Primary Care Doctor**: Initial evaluation and referrals\n"
            "• **Physical Therapist**: Rehabilitation and exercise prescription\n"
            "• **Sports Medicine Doctor**: Specialized injury care\n"
            "• **Orthopedic Specialist**: For complex musculoskeletal issues\n\n"
            "💡 **Remember**:\n"
            "• Injuries heal at different rates for different people\n"
            "• Patience is key to proper recovery\n"
            "• Professional guidance can speed recovery and prevent re-injury\n"
            "• Staying active within safe limits is usually beneficial\n\n"
            "Could you share more specific details about your injury so I can provide more targeted guidance?"
        )
        return response

    def get_capabilities(self) -> List[str]:
        return [
            "Safe exercise modifications for common injuries","Recovery phase guidance and education",
            "Low-impact exercise alternatives","Injury prevention strategies",
            "Professional referral recommendations","RICE protocol education",
            "Progressive return-to-activity planning",
            "Red flag identification for urgent care"
        ]
