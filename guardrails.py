"""
Input/Output Guardrails for Health & Wellness Planner Agent
Validates user input and agent output for safety and appropriateness
"""
import re
import logging
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ValidationError

from context import GoalStructure, MealPlanStructure, WorkoutPlanStructure

logger = logging.getLogger(__name__)

class HealthWellnessGuardrails:
    def __init__(self):
        self.dangerous_keywords = self._load_dangerous_keywords()
        self.medical_emergency_keywords = self._load_medical_emergency_keywords()
        self.inappropriate_content_patterns = self._load_inappropriate_patterns()
        self.max_input_length = 2000
        self.max_output_length = 5000

    def validate_input(self, user_input: str) -> Dict[str, Any]:
        logger.debug(f"Validating user input: {user_input}")
        try:
            if len(user_input.strip()) == 0:
                return {'is_valid': False, 'error': 'Please provide a message.', 'category': 'empty_input'}

            if len(user_input) > self.max_input_length:
                return {'is_valid': False, 'error': f'Message too long. Keep under {self.max_input_length} characters.', 'category': 'length_exceeded'}

            if (emergency := self._check_medical_emergency(user_input))['is_emergency']:
                return {'is_valid': False, 'error': emergency['message'], 'category': 'medical_emergency'}

            if (danger := self._check_dangerous_content(user_input))['is_safe'] is False:
                return {'is_valid': False, 'error': danger['message'], 'category': 'dangerous_content'}

            if (inappropriate := self._check_inappropriate_content(user_input))['is_appropriate'] is False:
                return {'is_valid': False, 'error': inappropriate['message'], 'category': 'inappropriate_content'}

            return {'is_valid': True, 'cleaned_input': user_input.strip(), 'category': 'valid'}

        except Exception as e:
            logger.exception("Exception during input validation")
            return {'is_valid': False, 'error': 'Unable to process your message.', 'category': 'processing_error'}

    def validate_output(self, agent_output: Any, tool_name: str = None) -> Dict[str, Any]:
        logger.debug(f"Validating output from tool '{tool_name}': {agent_output}")
        try:
            response_text = str(agent_output.get('response') if isinstance(agent_output, dict) else agent_output)

            if len(response_text) > self.max_output_length:
                response_text = response_text[:self.max_output_length] + "... [Response truncated for safety]"

            if (check := self._check_dangerous_medical_advice(response_text))['is_safe'] is False:
                return {'is_valid': False, 'error': check['message'], 'category': 'dangerous_medical_advice'}

            processed_response = self._add_safety_disclaimers(response_text, tool_name)

            if (tool_check := self._validate_tool_output(agent_output, tool_name))['is_valid'] is False:
                return tool_check

            return {'is_valid': True, 'data': processed_response, 'category': 'valid_output'}

        except Exception as e:
            logger.exception("Exception during output validation")
            return {'is_valid': False, 'error': 'Unable to process response.', 'category': 'output_processing_error'}

    def _check_medical_emergency(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        for keyword in self.medical_emergency_keywords:
            if keyword in text_lower:
                return {'is_emergency': True, 'message': '🚨 Possible medical emergency. Call emergency services (911/112).', 'keyword': keyword}
        return {'is_emergency': False}

    def _check_dangerous_content(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        for keyword in self.dangerous_keywords:
            if keyword in text_lower:
                return {'is_safe': False, 'message': 'Dangerous health practice detected. Consult a professional.', 'keyword': keyword}
        return {'is_safe': True}

    def _check_inappropriate_content(self, text: str) -> Dict[str, Any]:
        for pattern in self.inappropriate_content_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'is_appropriate': False, 'message': 'Please keep the conversation appropriate.', 'pattern': pattern}
        return {'is_appropriate': True}

    def _check_dangerous_medical_advice(self, text: str) -> Dict[str, Any]:
        patterns = [r'stop taking.*medication', r'ignore.*doctor', r'cure.*cancer', r'lose.*pounds.*week']
        for pattern in patterns:
            if re.search(pattern, text.lower()):
                return {'is_safe': False, 'message': '⚠️ This may be dangerous advice. Consult a licensed doctor.', 'pattern': pattern}
        return {'is_safe': True}

    def _add_safety_disclaimers(self, response: str, tool_name: str = None) -> str:
        disclaimers = {
            'meal_planner': '\n\n⚠️ **Disclaimer**: Meal plan is for general guidance. Consult a dietitian.',
            'workout_recommender': '\n\n⚠️ **Disclaimer**: Workout plan is for fitness guidance. Consult a doctor.',
            'goal_analyzer': '\n\n⚠️ **Disclaimer**: Goals should be realistic. Get professional advice.',
            'progress_tracker': '\n\n⚠️ **Disclaimer**: Progress tracking is informational only.',
            'scheduler': '\n\n⚠️ **Disclaimer**: Use this schedule as a general guide.'
        }
        return response + (disclaimers.get(tool_name) or '\n\n⚠️ **Disclaimer**: Always consult a qualified medical professional.')

    def _validate_tool_output(self, output: Any, tool_name: str = None) -> Dict[str, Any]:
        validators = {
            'meal_planner': self._validate_meal_plan_output,
            'workout_recommender': self._validate_workout_output,
            'goal_analyzer': self._validate_goal_output,
            'progress_tracker': self._validate_progress_output,
            'scheduler': self._validate_scheduler_output
        }
        try:
            if tool_name in validators:
                return validators[tool_name](output)
            return {'is_valid': True}
        except Exception as e:
            logger.exception("Tool output validation failed")
            return {'is_valid': False, 'error': str(e), 'category': 'tool_validation_error'}

    def _validate_meal_plan_output(self, output: Any) -> Dict[str, Any]:
        calories = output.get('nutrition_targets', {}).get('calories', 0)
        if calories < 800 or calories > 4000:
            return {'is_valid': False, 'error': 'Unrealistic calorie targets.', 'category': 'unrealistic_calories'}
        return {'is_valid': True}

    def _validate_workout_output(self, output: Any) -> Dict[str, Any]:
        response = output.get('response', '').lower()
        match = re.search(r'(\d+)\s*hours?', response)
        if match and int(match.group(1)) > 3:
            return {'is_valid': False, 'error': 'Workout duration too long.', 'category': 'excessive_workout'}
        return {'is_valid': True}

    def _validate_goal_output(self, output: Any) -> Dict[str, Any]:
        goal = output.get('goal', {})
        loss = goal.get('weight_loss_per_week')
        if loss and loss > 1.0:
            return {'is_valid': False, 'error': 'Unrealistic weight loss goal.', 'category': 'unrealistic_goal'}
        return {'is_valid': True}

    def _validate_progress_output(self, output: Any) -> Dict[str, Any]:
        return {'is_valid': True}

    def _validate_scheduler_output(self, output: Any) -> Dict[str, Any]:
        return {'is_valid': True}

    def _load_dangerous_keywords(self) -> List[str]:
        return [
            'extreme fasting', 'starvation diet', 'illegal steroids', 'diet pills',
            'purging', 'laxative abuse', 'overtraining', 'push through injury',
            'unsafe weight loss', 'dangerous detox'
        ]

    def _load_medical_emergency_keywords(self) -> List[str]:
        return [
            'chest pain', 'heart attack', 'stroke', "can't breathe", 'severe pain',
            'unconscious', 'bleeding heavily', 'overdose', 'anaphylaxis',
            'suicidal thoughts', 'want to die', 'emergency', 'ambulance'
        ]

    def _load_inappropriate_patterns(self) -> List[str]:
        return [
            r'\b(sex|porn|adult)\b', r'\b(drugs|cocaine|heroin)\b',
            r'\b(violence|kill|murder)\b', r'\b(hate|racism)\b'
        ]

    def get_safety_guidelines(self) -> Dict[str, List[str]]:
        return {
            'general': [
                'Consult healthcare professionals', 'Stay hydrated', 'Listen to your body'
            ],
            'exercise': [
                'Warm up and cool down', 'Use proper form', 'Rest between sessions'
            ],
            'nutrition': [
                'Eat balanced meals', 'Avoid extreme diets', 'Consult a dietitian'
            ],
            'goal_setting': [
                'Set realistic goals', 'Track progress wisely', 'Celebrate small wins'
            ]
        }
