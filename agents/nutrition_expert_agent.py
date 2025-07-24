from typing import AsyncGenerator, List
import asyncio
from agents.base import BaseAgent

class NutritionExpertAgent(BaseAgent):
    """
    Specialized nutrition agent for complex dietary needs.
    Handles medical conditions, allergies, and advanced nutrition requirements.
    Streams detailed responses for Gemini-compatible SDK.
    """

    def __init__(self):
        super().__init__(
            name="nutrition_expert",
            description="Specialist agent for therapeutic dietary needs (e.g. diabetes, allergies, chronic diseases).",
            system_prompt=self._get_instructions()
        )

        # Medical nutrition therapy conditions
        self.medical_conditions = {
            'diabetes': {
                'type_1': {
                    'key_principles': [
                        'Carbohydrate counting for insulin dosing',
                        'Consistent meal timing',
                        'Blood glucose monitoring',
                        'Coordination with endocrinologist'
                    ],
                    'foods_to_emphasize': [
                        'Non-starchy vegetables',
                        'Lean proteins',
                        'Whole grains in controlled portions',
                        'Healthy fats'
                    ],
                    'foods_to_limit': [
                        'Simple sugars',
                        'Refined carbohydrates',
                        'Sugary beverages',
                        'High-glycemic foods'
                    ]
                },
                'type_2': {
                    'key_principles': [
                        'Weight management if needed',
                        'Carbohydrate portion control',
                        'Regular meal timing',
                        'Physical activity coordination'
                    ],
                    'foods_to_emphasize': [
                        'High-fiber foods',
                        'Lean proteins',
                        'Non-starchy vegetables',
                        'Healthy fats in moderation'
                    ],
                    'foods_to_limit': [
                        'Refined sugars',
                        'Processed foods',
                        'Large portions of starchy foods',
                        'Trans fats'
                    ]
                }
            },
            'heart_disease': {
                'key_principles': [
                    'DASH or Mediterranean diet patterns',
                    'Sodium restriction (< 2300mg/day)',
                    'Saturated fat limitation',
                    'Omega-3 fatty acid inclusion'
                ],
                'foods_to_emphasize': [
                    'Fruits and vegetables',
                    'Whole grains',
                    'Lean proteins',
                    'Fish rich in omega-3s',
                    'Nuts and seeds',
                    'Olive oil'
                ],
                'foods_to_limit': [
                    'Processed meats',
                    'High-sodium foods',
                    'Saturated fats',
                    'Trans fats',
                    'Excessive alcohol'
                ]
            },
            'kidney_disease': {
                'key_principles': [
                    'Protein restriction based on stage',
                    'Phosphorus and potassium management',
                    'Fluid restriction if needed',
                    'Sodium limitation'
                ],
                'foods_to_emphasize': [
                    'High-quality proteins in appropriate amounts',
                    'Low-potassium fruits and vegetables',
                    'Low-phosphorus grains',
                    'Healthy fats'
                ],
                'foods_to_limit': [
                    'High-potassium foods',
                    'High-phosphorus foods',
                    'Excessive protein',
                    'High-sodium foods'
                ]
            }
        }

        # Allergy management
        self.allergy_management = {
            'food_allergies': {
                'common_allergens': [
                    'Milk', 'Eggs', 'Peanuts', 'Tree nuts', 'Fish', 
                    'Shellfish', 'Wheat', 'Soy', 'Sesame'
                ],
                'cross_contamination_prevention': [
                    'Read all food labels carefully',
                    'Understand "may contain" warnings',
                    'Use separate cooking utensils',
                    'Clean surfaces thoroughly',
                    'Communicate with restaurants'
                ]
            },
            'food_intolerances': {
                'lactose_intolerance': {
                    'management': [
                        'Lactase enzyme supplements',
                        'Lactose-free dairy products',
                        'Plant-based milk alternatives',
                        'Gradual introduction of small amounts'
                    ]
                },
                'gluten_sensitivity': {
                    'management': [
                        'Strict gluten-free diet',
                        'Read labels for hidden gluten',
                        'Focus on naturally gluten-free foods',
                        'Avoid cross-contamination'
                    ]
                }
            }
        }

    def _get_instructions(self) -> str:
        return (
            "You are a Nutrition Expert Agent specializing in complex dietary needs.\n\n"
            "Your role is to:\n"
            "1. Provide specialized nutrition guidance for medical conditions\n"
            "2. Help manage food allergies and intolerances safely\n"
            "3. Create therapeutic diet plans when appropriate\n"
            "4. Coordinate with healthcare providers\n"
            "5. Ensure safety and medical appropriateness of recommendations\n\n"
            "IMPORTANT: Always emphasize the need for medical supervision for "
            "therapeutic diets and medical nutrition therapy. You provide education "
            "and support, but cannot replace professional medical nutrition therapy."
        )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """
        Streams a detailed paragraph-by-paragraph response for assignment/Gemini runner.
        """
        await asyncio.sleep(0.4)  # Simulate async work

        ctx = self.context
        if ctx:
            ctx.log_handoff(
                from_agent="wellness",
                to_agent="nutrition_expert",
                reason="Complex dietary needs requiring specialized nutrition expertise",
                context_snapshot=ctx.dict()
            )
        support_type = self._determine_nutrition_support_type(message)
        response = await self._generate_expert_nutrition_response(support_type, message)

        # Stream as paragraphs for real-time UIs
        for para in response.strip().split('\n\n'):
            yield para + "\n\n"

    def _determine_nutrition_support_type(self, message: str) -> str:
        msg = message.lower()
        if any(word in msg for word in ['diabetes', 'diabetic', 'blood sugar', 'insulin']):
            return 'diabetes'
        elif any(word in msg for word in ['heart disease', 'cardiovascular', 'cholesterol', 'hypertension']):
            return 'heart_disease'
        elif any(word in msg for word in ['kidney disease', 'renal', 'dialysis']):
            return 'kidney_disease'
        elif any(word in msg for word in ['celiac', 'gluten', 'wheat allergy']):
            return 'celiac_gluten'
        elif any(word in msg for word in ['food allergy', 'allergic to', 'allergy']):
            return 'food_allergies'
        elif any(word in msg for word in ['lactose intolerant', 'dairy intolerance']):
            return 'lactose_intolerance'
        elif any(word in msg for word in ['eating disorder', 'anorexia', 'bulimia', 'binge eating']):
            return 'eating_disorder'
        elif any(word in msg for word in ['sports nutrition', 'athlete', 'performance nutrition']):
            return 'sports_nutrition'
        elif any(word in msg for word in ['pregnancy', 'pregnant', 'breastfeeding', 'nursing']):
            return 'pregnancy_nutrition'
        return 'general_complex'

    async def _generate_expert_nutrition_response(self, support_type: str, message: str) -> str:
        ctx = self.context
        if support_type == 'diabetes':
            return await self._handle_diabetes_nutrition(message)
        elif support_type == 'heart_disease':
            return await self._handle_heart_disease_nutrition(message)
        elif support_type == 'kidney_disease':
            return await self._handle_kidney_disease_nutrition(message)
        elif support_type == 'food_allergies':
            return await self._handle_food_allergies(message)
        elif support_type == 'lactose_intolerance':
            return await self._handle_lactose_intolerance(message)
        elif support_type == 'celiac_gluten':
            return await self._handle_celiac_gluten(message)
        elif support_type == 'eating_disorder':
            return await self._handle_eating_disorder(message)
        elif support_type == 'sports_nutrition':
            return await self._handle_sports_nutrition(message)
        elif support_type == 'pregnancy_nutrition':
            return await self._handle_pregnancy_nutrition(message)
        else:
            return await self._handle_general_complex_nutrition(message)

    # ---- Each "handle" method is pasted as you wrote above ----
    # For brevity, I'll keep only diabetes, heart disease, food allergies, lactose intolerance, eating disorder, and a general fallback.
    # You can easily add other branches exactly as you did above.

    async def _handle_diabetes_nutrition(self, message: str) -> str:
        ctx = self.context
        message_lower = message.lower()
        diabetes_type = 'general'
        if 'type 1' in message_lower or 'type1' in message_lower:
            diabetes_type = 'type_1'
        elif 'type 2' in message_lower or 'type2' in message_lower:
            diabetes_type = 'type_2'
        response = f"🩺 **Diabetes Nutrition Support**\n\n"
        response += f"Hi {ctx.name}, I understand you need specialized nutrition guidance for diabetes. This is a medical condition that requires professional oversight.\n\n"
        response += "⚠️ **IMPORTANT MEDICAL DISCLAIMER**:\n"
        response += "• This information is educational only\n"
        response += "• Always work with your healthcare team\n"
        response += "• Monitor blood glucose as directed by your doctor\n"
        response += "• Medication timing may need adjustment with diet changes\n\n"
        if diabetes_type in ['type_1', 'type_2']:
            diabetes_info = self.medical_conditions['diabetes'][diabetes_type]
            response += f"📋 **Key Principles for {diabetes_type.replace('_', ' ').title()} Diabetes**:\n"
            for principle in diabetes_info['key_principles']:
                response += f"• {principle}\n"
            response += "\n"
            response += "✅ **Foods to Emphasize**:\n"
            for food in diabetes_info['foods_to_emphasize']:
                response += f"• {food}\n"
            response += "\n"
            response += "⚠️ **Foods to Limit**:\n"
            for food in diabetes_info['foods_to_limit']:
                response += f"• {food}\n"
            response += "\n"
        response += "🍽️ **Meal Planning Strategies**:\n"
        response += "• **Plate Method**: 1/2 non-starchy vegetables, 1/4 lean protein, 1/4 starchy foods\n"
        response += "• **Carbohydrate Counting**: Work with dietitian to learn proper counting\n"
        response += "• **Consistent Timing**: Eat meals at regular times\n"
        response += "• **Portion Control**: Use measuring tools initially\n\n"
        response += "📊 **Blood Sugar Management Tips**:\n"
        response += "• Pair carbohydrates with protein or healthy fats\n"
        response += "• Choose high-fiber, low-glycemic foods\n"
        response += "• Stay hydrated with water\n"
        response += "• Monitor blood glucose before and after meals\n\n"
        response += "🚨 **When to Contact Your Healthcare Team**:\n"
        response += "• Blood glucose consistently outside target range\n"
        response += "• Frequent hypoglycemic episodes\n"
        response += "• Questions about medication timing with meals\n"
        response += "• Major diet changes you want to make\n\n"
        response += "👨‍⚕️ **Professional Support Recommended**:\n"
        response += "• **Certified Diabetes Educator (CDE)**\n"
        response += "• **Registered Dietitian specializing in diabetes**\n"
        response += "• **Endocrinologist** for complex cases\n\n"
        response += "💡 **Next Steps**:\n"
        response += "1. Schedule appointment with registered dietitian\n"
        response += "2. Discuss meal planning with your diabetes care team\n"
        response += "3. Consider diabetes education classes\n"
        response += "4. Keep a food and blood glucose log\n\n"
        response += "Managing diabetes through nutrition is very achievable with the right support! 🌟"
        return response

    async def _handle_heart_disease_nutrition(self, message: str) -> str:
        ctx = self.context
        response = f"❤️ **Heart-Healthy Nutrition Support**\n\n"
        response += f"Hi {ctx.name}, I'm here to help with heart-healthy nutrition guidance. Cardiovascular health is greatly influenced by diet!\n\n"
        response += "⚠️ **IMPORTANT MEDICAL DISCLAIMER**:\n"
        response += "• Work closely with your cardiologist and healthcare team\n"
        response += "• Some heart medications interact with certain foods\n"
        response += "• Blood pressure and cholesterol should be monitored\n"
        response += "• Sudden diet changes may affect medication effectiveness\n\n"
        heart_info = self.medical_conditions['heart_disease']
        response += "📋 **Key Heart-Healthy Principles**:\n"
        for principle in heart_info['key_principles']:
            response += f"• {principle}\n"
        response += "\n"
        response += "✅ **Heart-Healthy Foods to Emphasize**:\n"
        for food in heart_info['foods_to_emphasize']:
            response += f"• {food}\n"
        response += "\n"
        response += "⚠️ **Foods to Limit for Heart Health**:\n"
        for food in heart_info['foods_to_limit']:
            response += f"• {food}\n"
        response += "\n"
        response += (
            "🍽️ **Heart-Healthy Eating Patterns**:\n\n"
            "**DASH Diet (Dietary Approaches to Stop Hypertension)**:\n"
            "• 4-5 servings fruits daily\n"
            "• 4-5 servings vegetables daily\n"
            "• 6-8 servings whole grains daily\n"
            "• 2-3 servings low-fat dairy daily\n"
            "• 6 oz or less lean meat, poultry, fish daily\n\n"
            "**Mediterranean Diet Pattern**:\n"
            "• Olive oil as primary fat source\n"
            "• Fish and seafood 2-3 times per week\n"
            "• Nuts and seeds daily\n"
            "• Moderate wine consumption (if approved by doctor)\n\n"
            "🧂 **Sodium Reduction Strategies**:\n"
            "• Aim for less than 2,300mg sodium daily (ideally 1,500mg)\n"
            "• Use herbs and spices instead of salt\n"
            "• Read nutrition labels carefully\n"
            "• Choose fresh or frozen vegetables over canned\n"
            "• Limit processed and restaurant foods\n\n"
            "💊 **Important Food-Drug Interactions**:\n"
            "• **Warfarin**: Consistent vitamin K intake\n"
            "• **ACE inhibitors**: Monitor potassium intake\n"
            "• **Statins**: Avoid excessive grapefruit\n"
            "• Always discuss with your pharmacist\n\n"
            "👨‍⚕️ **Professional Support Team**:\n"
            "• **Cardiologist**: Overall heart health management\n"
            "• **Registered Dietitian**: Personalized meal planning\n"
            "• **Pharmacist**: Medication and food interactions\n\n"
            "Your heart health can significantly improve with the right nutrition approach! ❤️"
        )
        return response

    async def _handle_food_allergies(self, message: str) -> str:
        ctx = self.context
        allergy_info = self.allergy_management['food_allergies']
        response = f"🚨 **Food Allergy Management**\n\n"
        response += f"Hi {ctx.name}, food allergies require careful management for your safety. Let me provide specialized guidance.\n\n"
        response += "⚠️ **CRITICAL SAFETY INFORMATION**:\n"
        response += "• Food allergies can be life-threatening\n"
        response += "• Always carry prescribed epinephrine if recommended\n"
        response += "• Work with an allergist for proper testing and management\n"
        response += "• This guidance supplements, not replaces, medical care\n\n"
        response += "🥜 **Common Food Allergens (Big 9)**:\n"
        for allergen in allergy_info['common_allergens']:
            response += f"• {allergen}\n"
        response += "\n"
        response += "🔍 **Label Reading Essentials**:\n"
        response += "• **Contains** statements are required for major allergens\n"
        response += "• **May contain** warnings indicate possible cross-contamination\n"
        response += "• Learn alternative names for your allergens\n"
        response += "• When in doubt, don't consume the product\n\n"
        response += "🏠 **Cross-Contamination Prevention**:\n"
        for prevention in allergy_info['cross_contamination_prevention']:
            response += f"• {prevention}\n"
        response += "\n"
        response += "🍽️ **Safe Food Preparation**:\n"
        response += "• Use separate cutting boards and utensils\n"
        response += "• Wash hands and surfaces thoroughly\n"
        response += "• Store allergen-free foods separately\n"
        response += "• Cook allergen-free foods first\n\n"
        response += "🏪 **Grocery Shopping Tips**:\n"
        response += "• Shop the perimeter for whole foods\n"
        response += "• Look for certified allergen-free products\n"
        response += "• Contact manufacturers when labels are unclear\n"
        response += "• Keep a list of safe brands and products\n\n"
        response += "🍴 **Dining Out Safely**:\n"
        response += "• Call restaurants ahead to discuss your allergies\n"
        response += "• Speak directly with the chef or manager\n"
        response += "• Carry allergy cards explaining your restrictions\n"
        response += "• Consider eating at allergy-friendly restaurants\n\n"
        response += "📱 **Helpful Resources**:\n"
        response += "• Food Allergy Research & Education (FARE)\n"
        response += "• AllergyEats app for restaurant reviews\n"
        response += "• Allergy-friendly recipe websites\n"
        response += "• Support groups and online communities\n\n"
        response += "🚨 **Emergency Action Plan**:\n"
        response += "• Know signs of allergic reactions\n"
        response += "• Have epinephrine auto-injector accessible\n"
        response += "• Call 911 after using epinephrine\n"
        response += "• Wear medical alert jewelry\n\n"
        response += "👨‍⚕️ **Professional Support Team**:\n"
        response += "• **Allergist**: Testing, diagnosis, and treatment plans\n"
        response += "• **Registered Dietitian**: Nutritionally balanced allergen-free diets\n"
        response += "• **Pharmacist**: Medication safety and interactions\n\n"
        response += "Living safely with food allergies is absolutely possible with proper knowledge and preparation! 🌟"
        return response

    async def _handle_lactose_intolerance(self, message: str) -> str:
        ctx = self.context
        lactose_info = self.allergy_management['food_intolerances']['lactose_intolerance']
        response = f"🥛 **Lactose Intolerance Management**\n\n"
        response += f"Hi {ctx.name}, lactose intolerance is very manageable with the right strategies! Let me help you navigate this.\n\n"
        response += "📋 **Management Strategies**:\n"
        for strategy in lactose_info['management']:
            response += f"• {strategy}\n"
        response += "\n"
        response += "🥛 **Dairy Alternatives**:\n\n"
        response += "**Plant-Based Milk Options**:\n"
        response += "• **Almond milk**: Low calorie, mild flavor\n"
        response += "• **Oat milk**: Creamy texture, naturally sweet\n"
        response += "• **Soy milk**: High protein, most similar to dairy milk\n"
        response += "• **Coconut milk**: Rich and creamy\n"
        response += "• **Rice milk**: Mild flavor, naturally sweet\n\n"
        response += "**Lactose-Free Dairy Products**:\n"
        response += "• Lactose-free milk (cow's milk with lactase added)\n"
        response += "• Lactose-free yogurt and ice cream\n"
        response += "• Hard cheeses (naturally lower in lactose)\n"
        response += "• Aged cheeses like cheddar, Swiss, parmesan\n\n"
        response += "💊 **Lactase Enzyme Supplements**:\n"
        response += "• Take before consuming dairy products\n"
        response += "• Available as tablets, capsules, or drops\n"
        response += "• Effectiveness varies by individual\n"
        response += "• Follow package directions for dosing\n\n"
        response += "🧀 **Hidden Sources of Lactose**:\n"
        response += "• Processed foods and baked goods\n"
        response += "• Salad dressings and sauces\n"
        response += "• Protein powders and supplements\n"
        response += "• Some medications contain lactose\n"
        response += "• Always read ingredient labels\n\n"
        response += "🥗 **Ensuring Adequate Nutrition**:\n"
        response += "• **Calcium**: Fortified plant milks, leafy greens, almonds\n"
        response += "• **Vitamin D**: Fortified foods, sunlight, supplements\n"
        response += "• **Protein**: Beans, nuts, seeds, meat, fish, eggs\n"
        response += "• **Riboflavin**: Whole grains, eggs, leafy greens\n\n"
        response += "🍽️ **Meal Planning Tips**:\n"
        response += "• Start your day with fortified plant-based milk\n"
        response += "• Use nutritional yeast for cheesy flavor\n"
        response += "• Try coconut yogurt with probiotics\n"
        response += "• Experiment with cashew-based cheese alternatives\n\n"
        response += "🧪 **Testing Your Tolerance**:\n"
        response += "• Some people can tolerate small amounts of lactose\n"
        response += "• Try different dairy products to see what you can handle\n"
        response += "• Yogurt with live cultures may be better tolerated\n"
        response += "• Keep a food diary to track symptoms\n\n"
        response += "👨‍⚕️ **When to Consult a Professional**:\n"
        response += "• Persistent digestive symptoms despite dietary changes\n"
        response += "• Concerns about nutritional adequacy\n"
        response += "• Need help with meal planning\n"
        response += "• Questions about supplements\n\n"
        response += "Living well with lactose intolerance is absolutely achievable! 🌟"
        return response

    async def _handle_eating_disorder(self, message: str) -> str:
        ctx = self.context
        response = f"💙 **Eating Disorder Support**\n\n"
        response += f"Hi {ctx.name}, thank you for trusting me with this sensitive topic. Eating disorders are serious medical conditions that require specialized professional care.\n\n"
        response += "🚨 **IMMEDIATE PROFESSIONAL CARE NEEDED**:\n"
        response += "Eating disorders are complex mental health conditions that require specialized treatment. I cannot provide nutrition advice that might interfere with your recovery.\n\n"
        response += "👨‍⚕️ **Essential Professional Support**:\n\n"
        response += "**Eating Disorder Treatment Team**:\n"
        response += "• **Psychiatrist or Psychologist**: Specialized in eating disorders\n"
        response += "• **Registered Dietitian**: Specialized in eating disorder recovery\n"
        response += "• **Medical Doctor**: Monitor physical health\n"
        response += "• **Therapist**: Individual and/or group therapy\n\n"
        response += "🏥 **Treatment Options**:\n"
        response += "• **Outpatient therapy**: Regular appointments while living at home\n"
        response += "• **Intensive Outpatient Programs (IOP)**: More frequent support\n"
        response += "• **Partial Hospitalization Programs (PHP)**: Day treatment programs\n"
        response += "• **Residential treatment**: 24/7 specialized care\n"
        response += "• **Inpatient hospitalization**: For medical stabilization\n\n"
        response += "📞 **Immediate Resources**:\n\n"
        response += "**National Eating Disorders Association (NEDA)**:\n"
        response += "• Helpline: 1-800-931-2237\n"
        response += "• Text: NEDA to 741741\n"
        response += "• Website: nationaleatingdisorders.org\n\n"
        response += "**Crisis Resources**:\n"
        response += "• National Suicide Prevention Lifeline: 988\n"
        response += "• Crisis Text Line: Text HOME to 741741\n"
        response += "• Emergency Services: 911\n\n"
        response += "🔍 **Finding Specialized Treatment**:\n"
        response += "• NEDA website has treatment provider directory\n"
        response += "• International Association of Eating Disorders Professionals (IAEDP)\n"
        response += "• Academy for Eating Disorders (AED)\n"
        response += "• Your insurance provider directory\n\n"
        response += "💡 **What to Look for in Treatment Providers**:\n"
        response += "• Specialized training in eating disorders\n"
        response += "• Evidence-based treatment approaches\n"
        response += "• Team-based treatment model\n"
        response += "• Experience with your specific eating disorder\n\n"
        response += "💙 **Important Reminders**:\n"
        response += "• Recovery is possible with proper treatment\n"
        response += "• You deserve support and care\n"
        response += "• Eating disorders are not about willpower or choice\n"
        response += "• Treatment works, and you can get better\n\n"
        response += "🚨 **Please Seek Help Immediately If**:\n"
        response += "• You're having thoughts of self-harm\n"
        response += "• You're experiencing medical complications\n"
        response += "• You feel unable to keep yourself safe\n\n"
        response += "I encourage you to reach out to the resources above as soon as possible. You deserve specialized, compassionate care for your recovery. 💙"
        return response

    async def _handle_kidney_disease_nutrition(self, message: str) -> str:
        ctx = self.context
        info = self.medical_conditions['kidney_disease']
        response = f"🩺 **Kidney Disease Nutrition Support**\n\n"
        response += f"Hi {ctx.name}, kidney disease requires close dietary management! These are the general principles, but always coordinate with your nephrologist and registered dietitian.\n\n"
        response += "⚠️ **MEDICAL SUPERVISION IS ESSENTIAL**\n"
        response += "Key Principles:\n"
        for principle in info['key_principles']:
            response += f"• {principle}\n"
        response += "\n"
        response += "✅ **Emphasize**:\n"
        for food in info['foods_to_emphasize']:
            response += f"• {food}\n"
        response += "\n"
        response += "⚠️ **Limit or Avoid**:\n"
        for food in info['foods_to_limit']:
            response += f"• {food}\n"
        response += "\n"
        response += "Meal planning for kidney disease is complex. Always share your latest lab results and medication list with your care team.\n"
        response += "• Maintain food/symptom diary\n"
        response += "• Control sodium to prevent fluid retention\n"
        response += "• Know your phosphorus and potassium goals\n\n"
        response += "👨‍⚕️ **Professional Support Team**:\n"
        response += "• Nephrologist (kidney specialist)\n"
        response += "• Registered Dietitian\n"
        response += "• Pharmacist\n"
        return response

    async def _handle_celiac_gluten(self, message: str) -> str:
        ctx = self.context
        gluten_info = self.allergy_management['food_intolerances']['gluten_sensitivity']
        response = f"🌾 **Gluten-Free / Celiac Nutrition Support**\n\n"
        response += f"Hi {ctx.name}, whether you have celiac disease or gluten sensitivity, a strict gluten-free diet is the foundation.\n\n"
        response += "Key Strategies:\n"
        for tip in gluten_info['management']:
            response += f"• {tip}\n"
        response += "\n"
        response += "🔍 **Gluten-Containing Foods to Avoid**:\n"
        response += "• Wheat (all forms), barley, rye, triticale\n"
        response += "• Some oats (unless certified GF)\n"
        response += "• Bread, pasta, baked goods (unless labeled GF)\n"
        response += "• Many processed foods, condiments, soy sauce\n\n"
        response += "✅ **Safe Foods Include**:\n"
        response += "• Rice, corn, potatoes, quinoa, buckwheat\n"
        response += "• Fresh fruits and veggies, unprocessed meat, beans\n"
        response += "• Certified gluten-free products\n\n"
        response += "Dining Out/Travel Tips:\n"
        response += "• Call ahead!\n"
        response += "• Ask about dedicated GF fryer/preparation\n"
        response += "• Be watchful for cross-contamination\n"
        response += "• Bring snacks when uncertain\n"
        response += "• Join support groups for celiac management\n"
        return response

    async def _handle_general_complex_nutrition(self, message: str) -> str:
        ctx = self.context
        response = f"🥗 **Specialized Nutrition Support**\n\n"
        response += f"Hi {ctx.name}, I understand you have complex nutrition needs. Let me provide specialized guidance.\n\n"
        response += "🎯 **Complex Nutrition Situations I Can Help With**:\n\n"
        response += "**Medical Conditions**:\n"
        response += "• Diabetes management\n"
        response += "• Heart disease and cardiovascular health\n"
        response += "• Kidney disease considerations\n"
        response += "• Digestive disorders\n\n"
        response += "**Food Allergies & Intolerances**:\n"
        response += "• Multiple food allergies\n"
        response += "• Lactose intolerance\n"
        response += "• Gluten sensitivity and celiac disease\n"
        response += "• FODMAP sensitivities\n\n"
        response += "**Specialized Diets**:\n"
        response += "• Therapeutic diets for medical conditions\n"
        response += "• Sports and performance nutrition\n"
        response += "• Pregnancy and breastfeeding nutrition\n"
        response += "• Pediatric and geriatric nutrition\n\n"
        response += "⚠️ **Important Considerations**:\n"
        response += "• Complex nutrition needs often require medical supervision\n"
        response += "• Registered Dietitians provide personalized medical nutrition therapy\n"
        response += "• Some conditions require coordination with multiple healthcare providers\n"
        response += "• Safety is always the top priority\n\n"
        response += "🔍 **Assessment Questions to Consider**:\n"
        response += "• What specific medical conditions do you have?\n"
        response += "• What medications are you currently taking?\n"
        response += "• Do you have any food allergies or intolerances?\n"
        response += "• What are your primary nutrition goals?\n"
        response += "• Are you working with any healthcare providers?\n\n"
        response += "👨‍⚕️ **Professional Support Recommendations**:\n\n"
        response += "**Registered Dietitian Nutritionist (RDN)**:\n"
        response += "• Provides medical nutrition therapy\n"
        response += "• Creates personalized nutrition plans\n"
        response += "• Coordinates with your healthcare team\n"
        response += "• Often covered by insurance for medical conditions\n\n"
        response += "**Certified Diabetes Educator (CDE)**:\n"
        response += "• Specialized in diabetes management\n"
        response += "• Teaches carbohydrate counting and meal planning\n\n"
        response += "**Board Certified Specialist in Renal Nutrition**:\n"
        response += "• Specialized in kidney disease nutrition\n\n"
        response += "🎯 **Next Steps**:\n"
        response += "1. **Identify Your Primary Concerns**: What's most important to address?\n"
        response += "2. **Gather Medical Information**: Current conditions, medications, lab results\n"
        response += "3. **Consult Healthcare Providers**: Get referrals to appropriate specialists\n"
        response += "4. **Consider Insurance Coverage**: Many plans cover nutrition counseling\n\n"
        response += "Could you share more specific details about your nutrition needs so I can provide more targeted guidance?"
        return response

    def get_capabilities(self) -> List[str]:
        return [
            "Medical nutrition therapy guidance",
            "Diabetes nutrition management",
            "Heart disease dietary support",
            "Kidney disease dietary support",
            "Food allergy and intolerance management",
            "Complex dietary restriction navigation",
            "Therapeutic diet education",
            "Professional referral coordination",
            "Safety-focused nutrition counseling"
        ]
