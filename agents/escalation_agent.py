from typing import List
from .base import BaseAgent
from context import UserSessionContext

class EscalationAgent(BaseAgent):
    """
    Handles escalation to human professionals (medical, mental health, nutrition, and fitness).
    """

    def __init__(self):
        super().__init__(
            name="EscalationAgent",
            description="Handles referrals to human professionals",
            system_prompt="You are a helpful escalation agent who refers users to real-world professionals such as doctors, nutritionists, therapists, and fitness experts."
        )
    async def process_message(self, message: str, context: UserSessionContext) -> str:
        """Main entry point to route the message based on keywords"""
        msg = message.lower()

        if "medical" in msg:
            return await self._handle_medical_escalation(message, context)
        elif "nutrition" in msg or "diet" in msg:
            return await self._handle_nutrition_escalation(message, context)
        elif "fitness" in msg or "exercise" in msg:
            return await self._handle_fitness_escalation(message, context)
        else:
            return await self._handle_general_escalation(message, context)


    async def _handle_medical_escalation(self, message: str, context: UserSessionContext) -> str:
        response = f"🏥 **Medical Professional Support**\n\n"
        response += f"Hi {context.name}, seeking medical support is a smart step when it comes to your overall health. Here's a guide to help you navigate it:\n\n"

        response += "🩺 **When to See a Doctor**:\n"
        response += "• Chronic condition management\n"
        response += "• Medication reviews and adjustments\n"
        response += "• Health screenings and preventive care\n"
        response += "• Referrals to specialists\n"
        response += "• Medical clearance for exercise programs\n\n"

        response += "🧑‍⚕️ **Specialists for Health & Fitness**:\n\n"

        response += "**Endocrinologist**:\n"
        response += "• Hormone-related weight issues\n"
        response += "• Diabetes and metabolic disorders\n"
        response += "• Thyroid conditions\n\n"

        response += "**Sports Medicine Physician**:\n"
        response += "• Exercise-related injuries\n"
        response += "• Performance optimization\n"
        response += "• Safe return to activity after injury\n\n"

        response += "**Cardiologist**:\n"
        response += "• Heart conditions affecting exercise\n"
        response += "• Cardiovascular risk assessment\n"
        response += "• Exercise stress testing\n\n"

        response += "🔍 **How to Find Medical Professionals**:\n"
        response += "• Insurance provider directory\n"
        response += "• Hospital system websites\n"
        response += "• State medical board directories\n"
        response += "• Referrals from current doctors\n"
        response += "• Healthgrades.com or similar rating sites\n\n"

        response += "📋 **Preparing for Medical Appointments**:\n"
        response += "• List current symptoms and when they started\n"
        response += "• Bring current medications and supplements\n"
        response += "• Prepare questions in advance\n"
        response += "• Bring insurance cards and ID\n"
        response += "• Consider bringing a support person\n\n"

        response += "🚨 **Seek Immediate Medical Care For**:\n"
        response += "• Chest pain or difficulty breathing\n"
        response += "• Severe abdominal pain\n"
        response += "• Signs of stroke (FAST: Face, Arms, Speech, Time)\n"
        response += "• Severe allergic reactions\n"
        response += "• High fever with concerning symptoms\n\n"

        response += "Your health is the top priority. Don't hesitate to seek medical care when you have concerns! 🏥"
        return response

    async def _handle_nutrition_escalation(self, message: str, context: UserSessionContext) -> str:
        response = f"🥗 **Nutrition Professional Support**\n\n"
        response += f"Hi {context.name}, connecting with a nutrition professional is a great idea! Here's your guide:\n\n"

        response += "👩‍⚕️ **Types of Nutrition Professionals**:\n\n"

        response += "**Registered Dietitian Nutritionist (RDN)**:\n"
        response += "• Nationally credentialed nutrition expert\n"
        response += "• Completed accredited education and internship\n"
        response += "• Can provide medical nutrition therapy\n"
        response += "• Often covered by insurance\n"
        response += "• Most reliable credential to look for\n\n"

        response += "**Certified Nutrition Specialist (CNS)**:\n"
        response += "• Advanced degree in nutrition\n"
        response += "• Board certification in nutrition\n"
        response += "• Focus on personalized nutrition approaches\n\n"

        response += "🎯 **When to See a Nutrition Professional**:\n"
        response += "• Weight management goals\n"
        response += "• Medical conditions requiring dietary changes\n"
        response += "• Food allergies or intolerances\n"
        response += "• Eating disorders (with specialized training)\n"
        response += "• Sports nutrition needs\n"
        response += "• Digestive issues\n"
        response += "• Pregnancy and breastfeeding nutrition\n\n"

        response += "🔍 **How to Find a Qualified Professional**:\n"
        response += "• Visit eatright.org (Academy of Nutrition and Dietetics)\n"
        response += "• Use the 'Find an Expert' tool\n"
        response += "• Search by location and specialty\n\n"

        response += "**Insurance Coverage**:\n"
        response += "• Many insurance plans cover RDN services\n"
        response += "• May require physician referral\n"
        response += "• Often covered for diabetes, kidney disease, etc.\n\n"

        response += "**Other Options**:\n"
        response += "• Hospital and medical center nutrition departments\n"
        response += "• Your doctor’s referral\n"
        response += "• Employee wellness programs\n\n"

        response += "💰 **Cost Information**:\n"
        response += "• Initial consultation: $100–200\n"
        response += "• Follow-ups: $50–100\n"
        response += "• Insurance may cover some or all\n"
        response += "• Ask about sliding scale options\n\n"

        response += "📋 **What to Expect**:\n"
        response += "• Comprehensive nutrition assessment\n"
        response += "• Personalized meal planning\n"
        response += "• Ongoing education and monitoring\n"
        response += "• Coordination with other healthcare providers\n\n"

        response += "Working with a qualified nutrition professional can make a huge difference in reaching your health goals! 🌟"
        return response

    async def _handle_fitness_escalation(self, message: str, context: UserSessionContext) -> str:
        response = f"🏋️‍♀️ **Fitness Professional Support**\n\n"
        response += f"Hi {context.name}, working with a fitness professional is an excellent investment in your health!\n\n"

        response += "💪 **Types of Fitness Professionals**:\n\n"

        response += "**Certified Personal Trainer**:\n"
        response += "• Custom workout plans and form correction\n"
        response += "• Motivation and accountability\n"
        response += "• Look for NASM, ACSM, ACE, NSCA certifications\n\n"

        response += "**Exercise Physiologist**:\n"
        response += "• Degree in exercise science\n"
        response += "• Works with chronic disease patients\n"
        response += "• Often in clinical rehab settings\n\n"

        response += "**Physical Therapist**:\n"
        response += "• Licensed healthcare professional\n"
        response += "• Specializes in rehab and injury prevention\n"
        response += "• Works with movement dysfunctions\n\n"

        response += "🎯 **When to Work with a Fitness Pro**:\n"
        response += "• New to exercise or post-injury\n"
        response += "• Sports-specific training\n"
        response += "• Plateaued progress\n"
        response += "• Motivation or accountability needs\n"
        response += "• Want proper form guidance\n\n"

        response += "🔍 **How to Find One**:\n"
        response += "• Local gyms, studios, recreation centers\n"
        response += "• Directories on NASM.org, ACEfitness.org, ACSM.org, NSCA.com\n"
        response += "• Online platforms like Thumbtack, ClassPass\n\n"

        response += "💰 **Cost Guide**:\n"
        response += "• Personal training: $30–100+ per session\n"
        response += "• Group classes: $15–30\n"
        response += "• Bundles reduce per-session rates\n"
        response += "• Community centers = budget-friendly\n"
        response += "• Some health plans cover it\n\n"

        response += "❓ **Questions to Ask Trainers**:\n"
        response += "• Certifications?\n"
        response += "• Experience with your goals?\n"
        response += "• Training style?\n"
        response += "• Progress tracking?\n"
        response += "• Rates and cancellation policy?\n"
        response += "• Insurance coverage?\n\n"

        response += "✅ **Tips for Success**:\n"
        response += "• Get a consultation\n"
        response += "• Match personality/style\n"
        response += "• Ensure credentials and insurance\n\n"

        response += "A great trainer can help you progress safely and effectively. 💪"
        return response

    async def _handle_general_escalation(self, message: str, context: UserSessionContext) -> str:
        response = f"🤝 **Professional Support Options**\n\n"
        response += f"Hi {context.name}, I understand you'd like to connect with human professionals. Here are your options:\n\n"

        response += "👥 **Types of Professional Support**:\n\n"

        response += "🧠 **Mental Health**:\n"
        response += "• Therapists, counselors, psychologists\n"
        response += "• Psychiatrists for medication\n"
        response += "• Crisis counselors (immediate help)\n\n"

        response += "🏥 **Medical**:\n"
        response += "• Primary care doctors\n"
        response += "• Specialists for conditions\n"
        response += "• Preventive care\n\n"

        response += "🥗 **Nutrition**:\n"
        response += "• RDNs and CNS professionals\n"
        response += "• Meal planning and medical nutrition therapy\n\n"

        response += "🏋️‍♀️ **Fitness**:\n"
        response += "• Certified personal trainers\n"
        response += "• Exercise physiologists\n"
        response += "• Physical therapists\n\n"

        response += "🎯 **Why It Helps**:\n"
        response += "• Personalized care\n"
        response += "• Expertise and credentials\n"
        response += "• Long-term support\n"
        response += "• Integrates with medical care\n\n"

        response += "🛠 **Getting Started**:\n"
        response += "1. Identify your goal\n"
        response += "2. Check insurance coverage\n"
        response += "3. Ask for referrals\n"
        response += "4. Check credentials\n"
        response += "5. Schedule consultations\n\n"

        response += "💡 **Remember**:\n"
        response += "• It's okay to try more than one provider\n"
        response += "• Seeking help is a sign of strength\n"
        response += "• Professionals and AI can work together\n\n"

        response += "Would you like more details about a specific kind of professional?"
        return response

    def get_capabilities(self) -> List[str]:
        return [
            "Crisis intervention and emergency resource provision",
            "Mental health professional referrals",
            "Medical professional guidance",
            "Nutrition professional connections",
            "Fitness professional recommendations",
            "Insurance and cost guidance",
            "Professional credential verification",
            "Appointment preparation assistance"
        ]
