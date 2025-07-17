from .base_agent import BaseAgent
from openai import Assistant
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, field_validator
from ..context import UserSessionContext
from datetime import datetime, timedelta

class NutritionInput(BaseModel):
    """Guardrail model for nutrition-related input validation"""
    condition: str
    severity: Optional[str] = "moderate"
    current_diet: Optional[str] = None

    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v: str) -> str:
        v = v.lower().strip()
        if len(v) < 3:
            raise ValueError("Condition description too short")
        if "emergency" in v or "severe" in v:
            raise ValueError("For medical emergencies, please consult a doctor immediately")
        return v

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v.lower() not in ["mild", "moderate", "severe"]:
            raise ValueError("Severity must be mild, moderate or severe")
        return v.lower()

class NutritionExpertAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NutritionExpertAgent",
            description="Provides expert dietary guidance for medical conditions",
            tools=[
                self.analyze_nutritional_needs,
                self.generate_meal_plan,
                self.track_nutrition_progress
            ]
        )
        self.nutrition_guidelines = {
            "diabetes": {
                "general": [
                    "Low glycemic index foods (non-starchy vegetables, whole grains)",
                    "Lean proteins (fish, poultry, legumes)",
                    "Healthy fats (avocados, nuts, olive oil)"
                ],
                "avoid": [
                    "Sugary beverages and juices",
                    "Refined carbohydrates (white bread, pastries)",
                    "Trans fats (fried foods, processed snacks)"
                ],
                "meal_timing": "3 main meals + 2-3 snacks at consistent times",
                "monitoring": "Regular blood glucose checks"
            },
            "allergies": {
                "general": [
                    "Strict allergen avoidance",
                    "Nutrient-dense alternatives",
                    "Homemade meals when possible"
                ],
                "emergency": [
                    "Carry epinephrine auto-injector",
                    "Wear medical alert identification",
                    "Know emergency action plan"
                ]
            },
            "hypertension": {
                "general": [
                    "Low-sodium foods (<1500mg/day)",
                    "Potassium-rich foods (bananas, spinach)",
                    "Magnesium sources (almonds, black beans)"
                ],
                "avoid": [
                    "Processed meats",
                    "Canned soups and sauces",
                    "Salty snacks"
                ]
            }
        }
        self.user_plans: Dict[str, Dict] = {}

    @Assistant.tool
    async def analyze_nutritional_needs(self, condition: str, severity: str = "moderate", context: Optional[UserSessionContext] = None) -> Dict[str, List[str]]:
        try:
            validated = NutritionInput(condition=condition, severity=severity)
            condition_key = validated.condition.lower()

            advice = {
                "recommendations": ["Consult a registered dietitian"],
                "avoid": ["All processed foods"],
                "monitoring": ["Regular medical checkups"]
            }

            if condition_key in self.nutrition_guidelines:
                cond_data = self.nutrition_guidelines[condition_key]
                advice["recommendations"] = cond_data.get("general", [])
                advice["avoid"] = cond_data.get("avoid", [])
                if "diabet" in condition_key:
                    advice["monitoring"] = [cond_data.get("monitoring", "Check sugar levels")]
                    if severity == "severe":
                        advice["recommendations"].append("May require insulin management")
                if "allerg" in condition_key and severity == "severe":
                    advice["emergency"] = cond_data.get("emergency", [])

            if context:
                context.update_progress(
                    update=f"Nutrition consultation for {condition_key} ({severity})",
                    metric="nutrition_consultation",
                    value=1
                )
                if not context.diet_preferences:
                    context.diet_preferences = f"Medical: {condition_key}"

            return advice
        except Exception as e:
            return {
                "error": str(e),
                "recommendations": ["Consult healthcare provider immediately"],
                "emergency": "emergency" in str(e).lower()
            }

    @Assistant.tool
    async def generate_meal_plan(self, condition: str, days: int = 7, context: Optional[UserSessionContext] = None) -> Dict[str, Any]:
        try:
            if not 1 <= days <= 14:
                raise ValueError("Meal plan duration must be 1-14 days")

            validated = NutritionInput(condition=condition)
            condition_key = validated.condition.lower()

            plan = {
                "condition": condition_key,
                "duration_days": days,
                "meals": [],
                "nutritional_focus": [],
                "created_at": datetime.now().isoformat()
            }

            if condition_key in self.nutrition_guidelines:
                plan["nutritional_focus"] = self.nutrition_guidelines[condition_key].get("general", [])
                for day in range(1, days + 1):
                    plan["meals"].append({
                        "day": day,
                        "date": (datetime.now() + timedelta(days=day - 1)).strftime('%Y-%m-%d'),
                        "breakfast": f"{condition_key}-friendly breakfast",
                        "lunch": f"{condition_key}-appropriate lunch",
                        "dinner": f"{condition_key}-specific dinner",
                        "snacks": ["Healthy snack option"]
                    })

            plan_id = f"{condition_key}_{datetime.now().strftime('%Y%m%d')}"
            self.user_plans[plan_id] = plan

            if context:
                context.meal_plan = [f"{d['day']}: {d['breakfast']}" for d in plan["meals"]]
                context.update_progress(
                    update=f"Generated {days}-day meal plan for {condition_key}",
                    metric="meal_plan_generated",
                    value=days
                )

            return plan

        except Exception as e:
            return {
                "error": str(e),
                "recommendation": "Consult dietitian for personalized meal plan"
            }

    @Assistant.tool
    async def track_nutrition_progress(self, condition: str, adherence_level: int, notes: str, context: Optional[UserSessionContext] = None) -> Dict[str, str]:
        try:
            if not 1 <= adherence_level <= 10:
                raise ValueError("Adherence level must be 1-10")
            if not notes.strip():
                raise ValueError("Progress notes required")

            validated = NutritionInput(condition=condition)
            condition_key = validated.condition.lower()

            feedback = {
                "condition": condition_key,
                "date": datetime.now().isoformat(),
                "adherence_score": adherence_level,
                "notes": notes,
                "recommendations": []
            }

            if adherence_level >= 8:
                feedback["recommendations"] = ["Continue current plan"]
            elif adherence_level >= 5:
                feedback["recommendations"] = ["Simplify meal preparation", "Make 1-2 small improvements"]
            else:
                feedback["recommendations"] = ["Consult dietitian", "Break goals into simpler steps"]

            if context:
                context.update_progress(
                    update=f"Nutrition progress update for {condition_key}",
                    metric="nutrition_adherence",
                    value=adherence_level
                )
                context.progress_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "category": "nutrition",
                    "details": f"Adherence: {adherence_level}/10 - {notes[:100]}..."
                })

            return feedback

        except Exception as e:
            return {
                "error": str(e),
                "recommendation": "Schedule follow-up with healthcare provider"
            }

    def get_nutrition_plan(self, plan_id: str) -> Optional[Dict]:
        """Retrieve a stored nutrition plan by ID"""
        plan = self.user_plans.get(plan_id)
        if not plan:
            return {"error": "No plan found for the given ID"}
        return plan

    def list_available_conditions(self) -> List[str]:
        """List all supported medical nutrition conditions"""
        return list(self.nutrition_guidelines.keys())
