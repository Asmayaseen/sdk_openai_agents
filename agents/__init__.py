"""
Specialized agents for handoffs
"""
from .escalation_agent import EscalationAgent
from .nutrition_expert_agent import NutritionExpertAgent
from .injury_support_agent import InjurySupportAgent

__all__ = [
    'EscalationAgent',
    'NutritionExpertAgent', 
    'InjurySupportAgent'
]
