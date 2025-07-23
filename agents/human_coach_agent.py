from typing import List, Dict, Any, Optional, Tuple
from .base import BaseAgent
from context import UserSessionContext, AgentType

class HumanCoachAgent(BaseAgent):
    """Human coach connection and crisis support agent"""
    
    def __init__(self):
        super().__init__(AgentType.HUMAN_COACH)
        self.capabilities = [
            "Professional referrals",
            "Crisis support resources",
            "Complex case management",
            "Human coach connections",
            "Emergency intervention",
            "Specialized care coordination"
        ]
    
    async def process_message(self, message: str, context: UserSessionContext) -> str:
        """Process requests for human support"""
        message_lower = message.lower()
        
        # Handle different types of human support requests
        if any(word in message_lower for word in ['crisis', 'emergency', 'suicide', 'hurt myself']):
            return await self._handle_crisis_support(message, context)
        elif any(word in message_lower for word in ['therapist', 'counselor', 'psychologist', 'psychiatrist']):
            return await self._provide_mental_health_referrals(message, context)
        elif any(word in message_lower for word in ['doctor', 'physician', 'medical']):
            return await self._provide_medical_referrals(message, context)
        elif any(word in message_lower for word in ['nutritionist', 'dietitian']):
            return await self._provide_nutrition_referrals(message, context)
        elif any(word in message_lower for word in ['trainer', 'coach', 'fitness professional']):
            return await self._provide_fitness_referrals(message, context)
        else:
            return await self._handle_general_human_support(message, context)
    
    async def _handle_crisis_support(self, message: str, context: UserSessionContext) -> str:
        """Handle crisis situations with immediate resources"""
        response = "🚨 IMMEDIATE CRISIS SUPPORT\n\n"
        response += "🆘 **If you're in immediate danger, please contact emergency services: 911**\n\n"
        
        response += "📞 **24/7 Crisis Resources**:\n\n"
        response += "🇺🇸 **United States**:\n"
        response += "• **National Suicide Prevention Lifeline**: 988\n"
        response += "  - Available 24/7, free and confidential\n"
        response += "  - Chat online at suicidepreventionlifeline.org\n\n"
        
        response += "• **Crisis Text Line**: Text HOME to 741741\n"
        response += "  - Free, 24/7 crisis support via text\n"
        response += "  - Trained crisis counselors available\n\n"
        
        response += "• **National Domestic Violence Hotline**: 1-800-799-7233\n"
        response += "  - 24/7 support for domestic violence situations\n\n"
        
        response += "• **SAMHSA National Helpline**: 1-800-662-4357\n"
        response += "  - Mental health and substance abuse support\n"
        response += "  - Treatment referral and information service\n\n"
        
        response += "🌍 **International Resources**:\n"
        response += "• **Canada**: Talk Suicide Canada - 1-833-456-4566\n"
        response += "• **UK**: Samaritans - 116 123\n"
        response += "• **Australia**: Lifeline - 13 11 14\n"
        response += "• **International**: befrienders.org\n\n"
        
        response += "🏥 **Immediate Steps**:\n"
        response += "1. **Stay Safe**: Remove any means of self-harm\n"
        response += "2. **Reach Out**: Call one of the numbers above\n"
        response += "3. **Stay Connected**: Don't isolate yourself\n"
        response += "4. **Go to ER**: If in immediate physical danger\n"
        response += "5. **Tell Someone**: Inform a trusted friend or family member\n\n"
        
        response += "💙 **Remember**:\n"
        response += "• You are not alone in this\n"
        response += "• Crisis feelings are temporary\n"
        response += "• Help is available and effective\n"
        response += "• Your life has value and meaning\n"
        response += "• Many people have felt this way and recovered\n\n"
        
        response += "🤝 **Next Steps After Crisis**:\n"
        response += "• Follow up with a mental health professional\n"
        response += "• Create a safety plan with support people\n"
        response += "• Consider intensive outpatient programs\n"
        response += "• Build a strong support network\n"
        
        # Log this as a critical interaction
        context.add_conversation(message, "Crisis support provided", "emergency_intervention")
        
        return response
    
    async def _provide_mental_health_referrals(self, message: str, context: UserSessionContext) -> str:
        """Provide mental health professional referrals"""
        response = "🧠 Mental Health Professional Referrals\n\n"
        
        response += "🎯 **Types of Mental Health Professionals**:\n\n"
        response += "1. **Psychologist (PhD/PsyD)**:\n"
        response += "   - Provides therapy and psychological testing\n"
        response += "   - Cannot prescribe medication (in most states)\n"
        response += "   - Specializes in various therapy approaches\n\n"
        
        response += "2. **Psychiatrist (MD)**:\n"
        response += "   - Medical doctor specializing in mental health\n"
        response += "   - Can prescribe medication\n"
        response += "   - Often focuses on medication management\n\n"
        
        response += "3. **Licensed Clinical Social Worker (LCSW)**:\n"
        response += "   - Provides therapy and counseling\n"
        response += "   - Often works with individuals, families, and groups\n"
        response += "   - May specialize in specific populations\n\n"
        
        response += "4. **Licensed Professional Counselor (LPC)**:\n"
        response += "   - Provides individual and group therapy\n"
        response += "   - Various specializations available\n"
        response += "   - Often more affordable than psychologists\n\n"
        
        response += "🔍 **How to Find a Mental Health Professional**:\n\n"
        response += "• **Insurance Provider Directory**:\n"
        response += "  - Check your insurance website for covered providers\n"
        response += "  - Call member services for assistance\n\n"
        
        response += "• **Psychology Today**:\n"
        response += "  - psychologytoday.com\n"
        response += "  - Search by location, insurance, and specialization\n"
        response += "  - Read provider profiles and approaches\n\n"
        
        response += "• **Your Primary Care Doctor**:\n"
        response += "  - Can provide referrals to trusted professionals\n"
        response += "  - May coordinate care between providers\n\n"
        
        response += "• **Employee Assistance Program (EAP)**:\n"
        response += "  - Many employers offer free counseling sessions\n"
        response += "  - Check with HR about available resources\n\n"
        
        response += "💰 **Cost Considerations**:\n"
        response += "• Check insurance coverage and copays\n"
        response += "• Ask about sliding scale fees\n"
        response += "• Community mental health centers often offer lower-cost options\n"
        response += "• Some therapists offer payment plans\n\n"
        
        response += "❓ **Questions to Ask Potential Therapists**:\n"
        response += "• What is your experience with my specific concerns?\n"
        response += "• What therapeutic approaches do you use?\n"
        response += "• What are your fees and payment options?\n"
        response += "• How often would we meet?\n"
        response += "• What should I expect from therapy?\n"
        
        tips = [
            "It's okay to 'shop around' for the right therapist",
            "The therapeutic relationship is crucial for success",
            "Don't give up if the first therapist isn't a good fit",
            "Be honest about your concerns and goals"
        ]
        
        next_steps = [
            "Check your insurance coverage for mental health",
            "Research therapists in your area",
            "Schedule initial consultations with 2-3 providers"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _provide_medical_referrals(self, message: str, context: UserSessionContext) -> str:
        """Provide medical professional referrals"""
        response = "🏥 Medical Professional Referrals\n\n"
        
        response += "⚠️ **Important**: This AI system cannot diagnose medical conditions or replace professional medical advice.\n\n"
        
        response += "👨‍⚕️ **When to See Your Primary Care Doctor**:\n"
        response += "• Annual wellness checkups\n"
        response += "• New or concerning symptoms\n"
        response += "• Chronic condition management\n"
        response += "• Medication reviews\n"
        response += "• Referrals to specialists\n"
        response += "• Health screenings and preventive care\n\n"
        
        response += "🩺 **Specialists You Might Need**:\n\n"
        response += "**For Weight Management**:\n"
        response += "• Endocrinologist (hormone-related weight issues)\n"
        response += "• Bariatric surgeon (surgical weight loss options)\n"
        response += "• Registered dietitian (nutrition counseling)\n\n"
        
        response += "**For Fitness-Related Issues**:\n"
        response += "• Sports medicine physician\n"
        response += "• Physical therapist\n"
        response += "• Orthopedic surgeon (for injuries)\n\n"
        
        response += "**For Mental Health**:\n"
        response += "• Psychiatrist (medication management)\n"
        response += "• Neurologist (if neurological symptoms)\n\n"
        
        response += "🔍 **How to Find Medical Professionals**:\n\n"
        response += "• **Insurance Provider Directory**\n"
        response += "• **Hospital System Websites**\n"
        response += "• **State Medical Board Directories**\n"
        response += "• **Referrals from Current Doctors**\n"
        response += "• **Healthgrades.com or similar rating sites**\n\n"
        
        response += "📋 **Preparing for Medical Appointments**:\n"
        response += "• List current symptoms and when they started\n"
        response += "• Bring current medications and supplements\n"
        response += "• Prepare questions in advance\n"
        response += "• Bring insurance cards and ID\n"
        response += "• Consider bringing a support person\n\n"
        
        response += "🚨 **When to Seek Immediate Medical Care**:\n"
        response += "• Chest pain or difficulty breathing\n"
        response += "• Severe abdominal pain\n"
        response += "• Signs of stroke (FAST: Face, Arms, Speech, Time)\n"
        response += "• Severe allergic reactions\n"
        response += "• High fever with concerning symptoms\n"
        response += "• Any situation where you feel something is seriously wrong\n"
        
        tips = [
            "Don't hesitate to seek medical care when concerned",
            "Keep a health journal to track symptoms",
            "Be honest with healthcare providers about all symptoms",
            "Ask questions if you don't understand something"
        ]
        
        next_steps = [
            "Schedule a wellness checkup if overdue",
            "Research specialists if needed",
            "Prepare questions for your next appointment"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _provide_nutrition_referrals(self, message: str, context: UserSessionContext) -> str:
        """Provide nutrition professional referrals"""
        response = "🥗 Nutrition Professional Referrals\n\n"
        
        response += "👩‍⚕️ **Types of Nutrition Professionals**:\n\n"
        response += "1. **Registered Dietitian Nutritionist (RDN)**:\n"
        response += "   - Nationally credentialed nutrition expert\n"
        response += "   - Completed accredited education and internship\n"
        response += "   - Can provide medical nutrition therapy\n"
        response += "   - Often covered by insurance\n\n"
        
        response += "2. **Certified Nutrition Specialist (CNS)**:\n"
        response += "   - Advanced degree in nutrition\n"
        response += "   - Board certification in nutrition\n"
        response += "   - Focus on personalized nutrition approaches\n\n"
        
        response += "3. **Certified Nutritionist**:\n"
        response += "   - Varies by state (some states don't regulate this title)\n"
        response += "   - Check credentials and education carefully\n"
        response += "   - May not be covered by insurance\n\n"
        
        response += "🎯 **When to See a Nutrition Professional**:\n"
        response += "• Weight management goals\n"
        response += "• Medical conditions requiring dietary changes\n"
        response += "• Food allergies or intolerances\n"
        response += "• Eating disorders (with specialized training)\n"
        response += "• Sports nutrition needs\n"
        response += "• Digestive issues\n"
        response += "• Pregnancy and breastfeeding nutrition\n\n"
        
        response += "🔍 **How to Find a Qualified Professional**:\n\n"
        response += "• **Academy of Nutrition and Dietetics**: eatright.org\n"
        response += "  - 'Find an Expert' tool\n"
        response += "  - Search by location and specialty\n\n"
        
        response += "• **Insurance Provider Directory**\n"
        response += "  - Many insurance plans cover RDN services\n"
        response += "  - May require physician referral\n\n"
        
        response += "• **Hospital and Medical Center Websites**\n"
        response += "  - Many have outpatient nutrition services\n\n"
        
        response += "• **Your Doctor's Referral**\n"
        response += "  - Primary care or specialist referral\n"
        response += "  - May be required for insurance coverage\n\n"
        
        response += "💰 **Cost and Insurance**:\n"
        response += "• Many insurance plans cover RDN services\n"
        response += "• Medical nutrition therapy often covered for certain conditions\n"
        response += "• Ask about sliding scale fees\n"
        response += "• Some employers offer nutrition counseling benefits\n\n"
        
        response += "📋 **What to Expect**:\n"
        response += "• Comprehensive nutrition assessment\n"
        response += "• Personalized meal planning\n"
        response += "• Education about nutrition and health\n"
        response += "• Ongoing support and monitoring\n"
        response += "• Coordination with other healthcare providers\n"
        
        tips = [
            "Look for RDN credential for most reliable expertise",
            "Ask about their experience with your specific needs",
            "Check if your insurance covers nutrition counseling",
            "Be prepared to discuss your complete health history"
        ]
        
        next_steps = [
            "Check insurance coverage for nutrition services",
            "Get a referral from your doctor if needed",
            "Research RDNs in your area with relevant specialties"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _provide_fitness_referrals(self, message: str, context: UserSessionContext) -> str:
        """Provide fitness professional referrals"""
        response = "🏋️‍♀️ Fitness Professional Referrals\n\n"
        
        response += "💪 **Types of Fitness Professionals**:\n\n"
        response += "1. **Certified Personal Trainer**:\n"
        response += "   - One-on-one or small group training\n"
        response += "   - Customized workout programs\n"
        response += "   - Form correction and motivation\n"
        response += "   - Look for certifications: NASM, ACSM, ACE, NSCA\n\n"
        
        response += "2. **Exercise Physiologist**:\n"
        response += "   - Advanced degree in exercise science\n"
        response += "   - Specializes in exercise for medical conditions\n"
        response += "   - Often works in clinical settings\n\n"
        
        response += "3. **Physical Therapist**:\n"
        response += "   - Licensed healthcare professional\n"
        response += "   - Specializes in injury recovery and prevention\n"
        response += "   - Can address movement dysfunctions\n\n"
        
        response += "4. **Group Fitness Instructor**:\n"
        response += "   - Leads classes in various formats\n"
        response += "   - More affordable than personal training\n"
        response += "   - Good for motivation and community\n\n"
        
        response += "🎯 **When to Work with a Fitness Professional**:\n"
        response += "• New to exercise or returning after long break\n"
        response += "• Specific fitness goals (strength, endurance, sport)\n"
        response += "• Injury history or physical limitations\n"
        response += "• Plateau in current fitness routine\n"
        response += "• Need motivation and accountability\n"
        response += "• Want to learn proper form and technique\n\n"
        
        response += "🔍 **How to Find Qualified Professionals**:\n\n"
        response += "• **Local Gyms and Fitness Centers**\n"
        response += "  - Many have certified trainers on staff\n"
        response += "  - Can often try a session before committing\n\n"
        
        response += "• **Professional Organization Directories**:\n"
        response += "  - NASM: nasm.org\n"
        response += "  - ACSM: acsm.org\n"
        response += "  - ACE: acefitness.org\n"
        response += "  - NSCA: nsca.com\n\n"
        
        response += "• **Online Platforms**:\n"
        response += "  - Thumbtack, ClassPass, Trainiac\n"
        response += "  - Read reviews and check credentials\n\n"
        
        response += "• **Referrals**:\n"
        response += "  - Ask friends, family, or healthcare providers\n"
        response += "  - Check with local sports medicine clinics\n\n"
        
        response += "💰 **Cost Considerations**:\n"
        response += "• Personal training: $30-100+ per session\n"
        response += "• Group classes: $15-30 per class\n"
        response += "• Package deals often reduce per-session cost\n"
        response += "• Some insurance plans cover exercise therapy\n"
        response += "• Community centers may offer lower-cost options\n\n"
        
        response += "❓ **Questions to Ask Potential Trainers**:\n"
        response += "• What certifications do you hold?\n"
        response += "• What's your experience with my goals/conditions?\n"
        response += "• What's your training philosophy?\n"
        response += "• Can you provide references?\n"
        response += "• What are your rates and cancellation policy?\n"
        response += "• How do you track progress?\n"
        
        tips = [
            "Look for nationally recognized certifications",
            "Ask for a consultation or trial session",
            "Make sure their personality and style fit you",
            "Check that they carry liability insurance"
        ]
        
        next_steps = [
            "Research certified trainers in your area",
            "Schedule consultations with 2-3 candidates",
            "Ask about their experience with your specific goals"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    async def _handle_general_human_support(self, message: str, context: UserSessionContext) -> str:
        """Handle general requests for human support"""
        response = f"🤝 Human Support & Professional Resources\n\n"
        
        response += f"Hello {context.user_name}! I understand you'd like to connect with human professionals. "
        response += "That's a great step in your health and wellness journey.\n\n"
        
        response += "👥 **Types of Human Support Available**:\n\n"
        response += "🧠 **Mental Health Professionals**:\n"
        response += "• Therapists and counselors\n"
        response += "• Psychiatrists for medication management\n"
        response += "• Crisis counselors for immediate support\n\n"
        
        response += "🏥 **Medical Professionals**:\n"
        response += "• Primary care physicians\n"
        response += "• Specialists for specific conditions\n"
        response += "• Preventive care providers\n\n"
        
        response += "🥗 **Nutrition Professionals**:\n"
        response += "• Registered Dietitian Nutritionists (RDNs)\n"
        response += "• Certified Nutrition Specialists\n"
        response += "• Medical nutrition therapists\n\n"
        
        response += "🏋️‍♀️ **Fitness Professionals**:\n"
        response += "• Certified personal trainers\n"
        response += "• Exercise physiologists\n"
        response += "• Physical therapists\n\n"
        
        response += "🎯 **Why Human Support is Valuable**:\n"
        response += "• Personalized assessment and care\n"
        response += "• Professional expertise and credentials\n"
        response += "• Accountability and ongoing support\n"
        response += "• Ability to address complex or serious issues\n"
        response += "• Integration with your overall healthcare\n\n"
        
        response += "🔍 **Getting Started**:\n"
        response += "1. **Identify Your Needs**: What type of support do you need most?\n"
        response += "2. **Check Insurance**: What professionals are covered?\n"
        response += "3. **Get Referrals**: Ask your doctor or trusted friends\n"
        response += "4. **Research Credentials**: Verify professional qualifications\n"
        response += "5. **Schedule Consultations**: Meet with potential providers\n\n"
        
        response += "💡 **Remember**:\n"
        response += "• Seeking professional help is a sign of strength\n"
        response += "• It's okay to 'shop around' for the right fit\n"
        response += "• Many professionals offer initial consultations\n"
        response += "• You can continue using AI support alongside human professionals\n"
        
        tips = [
            "Don't wait until problems become severe to seek help",
            "Professional support can accelerate your progress",
            "The right professional relationship can be life-changing",
            "Many issues are best addressed with human expertise"
        ]
        
        next_steps = [
            "Identify which type of professional you need most",
            "Check your insurance coverage and benefits",
            "Ask me for specific referral guidance in any area"
        ]
        
        return self.format_response(response, tips, next_steps)
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
