"""
Goal Analyzer Tool for Health & Wellness Planner Agent
Parses natural language goals into structured, actionable objectives
"""
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from context import UserSessionContext, GoalType

class GoalAnalyzerTool:
    """
    Analyzes and structures user health and wellness goals from natural language input
    Converts vague goals into specific, measurable, achievable, relevant, and time-bound (SMART) objectives
    """
    
    def __init__(self):
        self.name = "GoalAnalyzerTool"
        self.description = "Analyzes and structures user health and wellness goals into actionable plans"
        
        # Goal patterns and keywords
        self.goal_patterns = self._load_goal_patterns()
        self.time_patterns = self._load_time_patterns()
        self.measurement_patterns = self._load_measurement_patterns()
        
    async def run(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """
        Analyze user input and extract structured goal information
        
        Args:
            user_input: User's goal description in natural language
            context: User session context
            
        Returns:
            Structured goal information with SMART criteria
        """
        try:
            # Parse the goal from user input
            parsed_goal = self._parse_goal(user_input, context)
            
            # Validate and enhance the goal
            enhanced_goal = self._enhance_goal(parsed_goal, context)
            
            # Create action plan
            action_plan = self._create_action_plan(enhanced_goal, context)
            
            # Update context
            context.goal = enhanced_goal
            context.goal_type = GoalType(enhanced_goal['goal_type'])
            
            # Generate response
            response = self._format_goal_response(enhanced_goal, action_plan)
            
            return {
                'response': response,
                'goal': enhanced_goal,
                'action_plan': action_plan,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"I'd love to help you set a clear goal! Could you tell me more specifically what you'd like to achieve? For example: 'I want to lose 5kg in 2 months' or 'I want to run a 5K race'.",
                'error': str(e),
                'success': False
            }
    
    def _parse_goal(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Parse goal information from user input"""
        user_input_lower = user_input.lower()
        
        # Initialize goal structure
        goal = {
            'original_input': user_input,
            'goal_type': 'general_fitness',
            'description': '',
            'target_value': None,
            'target_unit': None,
            'timeframe': None,
            'timeframe_unit': None,
            'specific_activities': [],
            'motivation': '',
            'difficulty_level': 'moderate'
        }
        
        # Determine goal type
        goal['goal_type'] = self._identify_goal_type(user_input_lower)
        
        # Extract target values and measurements
        target_info = self._extract_target_measurements(user_input_lower)
        goal.update(target_info)
        
        # Extract timeframe
        timeframe_info = self._extract_timeframe(user_input_lower)
        goal.update(timeframe_info)
        
        # Extract specific activities
        goal['specific_activities'] = self._extract_activities(user_input_lower)
        
        # Generate description
        goal['description'] = self._generate_goal_description(goal, user_input)
        
        # Assess difficulty
        goal['difficulty_level'] = self._assess_difficulty(goal, context)
        
        return goal
    
    def _identify_goal_type(self, user_input: str) -> str:
        """Identify the type of goal from user input"""
        goal_type_keywords = {
            'weight_loss': ['lose weight', 'lose', 'shed', 'drop', 'slim down', 'get thinner', 'weight loss'],
            'weight_gain': ['gain weight', 'gain', 'bulk up', 'put on weight', 'get bigger', 'weight gain'],
            'muscle_building': ['build muscle', 'muscle', 'strength', 'bulk', 'tone', 'get stronger', 'muscle building'],
            'endurance': ['endurance', 'cardio', 'run', 'marathon', 'stamina', 'fitness', 'aerobic'],
            'strength': ['strength', 'lift', 'powerlifting', 'strong', 'bench press', 'squat', 'deadlift'],
            'flexibility': ['flexibility', 'flexible', 'stretch', 'yoga', 'mobility', 'range of motion'],
            'stress_management': ['stress', 'anxiety', 'mental health', 'relaxation', 'meditation', 'mindfulness'],
            'nutrition_improvement': ['eat better', 'nutrition', 'healthy eating', 'diet', 'meal plan', 'food']
        }
        
        for goal_type, keywords in goal_type_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                return goal_type
        
        return 'general_fitness'
    
    def _extract_target_measurements(self, user_input: str) -> Dict[str, Any]:
        """Extract target measurements from user input"""
        measurements = {
            'target_value': None,
            'target_unit': None,
            'current_value': None,
            'current_unit': None
        }
        
        # Weight patterns
        weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|kilograms?|lbs?|pounds?)',
            r'lose\s+(\d+(?:\.\d+)?)\s*(kg|kilograms?|lbs?|pounds?)',
            r'gain\s+(\d+(?:\.\d+)?)\s*(kg|kilograms?|lbs?|pounds?)'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, user_input)
            if match:
                measurements['target_value'] = float(match.group(1))
                measurements['target_unit'] = self._normalize_unit(match.group(2))
                break
        
        # Distance patterns
        distance_patterns = [
            r'(\d+(?:\.\d+)?)\s*(km|kilometers?|miles?|m|meters?)',
            r'run\s+(\d+(?:\.\d+)?)\s*(km|kilometers?|miles?|m|meters?)'
        ]
        
        for pattern in distance_patterns:
            match = re.search(pattern, user_input)
            if match:
                measurements['target_value'] = float(match.group(1))
                measurements['target_unit'] = self._normalize_unit(match.group(2))
                break
        
        # Repetition patterns (push-ups, sit-ups, etc.)
        rep_patterns = [
            r'(\d+)\s*(push-?ups?|sit-?ups?|squats?|reps?|repetitions?)',
            r'do\s+(\d+)\s*(push-?ups?|sit-?ups?|squats?)'
        ]
        
        for pattern in rep_patterns:
            match = re.search(pattern, user_input)
            if match:
                measurements['target_value'] = int(match.group(1))
                measurements['target_unit'] = 'repetitions'
                break
        
        return measurements
    
    def _extract_timeframe(self, user_input: str) -> Dict[str, Any]:
        """Extract timeframe information from user input"""
        timeframe_info = {
            'timeframe': None,
            'timeframe_unit': None,
            'target_date': None
        }
        
        # Time patterns
        time_patterns = [
            r'in\s+(\d+)\s*(days?|weeks?|months?|years?)',
            r'within\s+(\d+)\s*(days?|weeks?|months?|years?)',
            r'over\s+(\d+)\s*(days?|weeks?|months?|years?)',
            r'(\d+)\s*(days?|weeks?|months?|years?)',
            r'by\s+(\w+)',  # by summer, by christmas, etc.
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, user_input)
            if match:
                if len(match.groups()) == 2:
                    timeframe_info['timeframe'] = int(match.group(1))
                    timeframe_info['timeframe_unit'] = self._normalize_time_unit(match.group(2))
                    
                    # Calculate target date
                    timeframe_info['target_date'] = self._calculate_target_date(
                        timeframe_info['timeframe'], 
                        timeframe_info['timeframe_unit']
                    )
                break
        
        # Default timeframe if none specified
        if not timeframe_info['timeframe']:
            timeframe_info['timeframe'] = 12
            timeframe_info['timeframe_unit'] = 'weeks'
            timeframe_info['target_date'] = self._calculate_target_date(12, 'weeks')
        
        return timeframe_info
    
    def _extract_activities(self, user_input: str) -> List[str]:
        """Extract specific activities mentioned in the goal"""
        activities = []
        
        activity_keywords = {
            'running': ['run', 'running', 'jog', 'jogging'],
            'walking': ['walk', 'walking'],
            'swimming': ['swim', 'swimming'],
            'cycling': ['bike', 'cycling', 'bicycle'],
            'weightlifting': ['lift', 'weights', 'gym', 'strength training'],
            'yoga': ['yoga'],
            'pilates': ['pilates'],
            'dancing': ['dance', 'dancing'],
            'hiking': ['hike', 'hiking'],
            'sports': ['tennis', 'basketball', 'football', 'soccer', 'volleyball']
        }
        
        for activity, keywords in activity_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                activities.append(activity)
        
        return activities
    
    def _enhance_goal(self, goal: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Enhance goal with SMART criteria and realistic expectations"""
        enhanced_goal = goal.copy()
        
        # Make goal more specific
        enhanced_goal = self._make_specific(enhanced_goal, context)
        
        # Ensure measurability
        enhanced_goal = self._make_measurable(enhanced_goal)
        
        # Check achievability
        enhanced_goal = self._make_achievable(enhanced_goal, context)
        
        # Ensure relevance
        enhanced_goal = self._make_relevant(enhanced_goal, context)
        
        # Set time-bound criteria
        enhanced_goal = self._make_time_bound(enhanced_goal)
        
        return enhanced_goal
    
    def _make_specific(self, goal: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Make goal more specific based on context"""
        if not goal['description']:
            goal_type = goal['goal_type']
            
            if goal_type == 'weight_loss' and goal['target_value']:
                goal['description'] = f"Lose {goal['target_value']}{goal['target_unit']} through healthy diet and exercise"
            elif goal_type == 'muscle_building':
                goal['description'] = "Build lean muscle mass through strength training and proper nutrition"
            elif goal_type == 'endurance':
                goal['description'] = "Improve cardiovascular endurance and stamina"
            elif goal_type == 'strength':
                goal['description'] = "Increase overall strength and power"
            else:
                goal['description'] = "Improve overall health and fitness"
        
        return goal
    
    def _make_measurable(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure goal has measurable criteria"""
        if not goal['target_value']:
            goal_type = goal['goal_type']
            
            # Set default measurable targets
            if goal_type == 'weight_loss':
                goal['target_value'] = 5
                goal['target_unit'] = 'kg'
            elif goal_type == 'weight_gain':
                goal['target_value'] = 3
                goal['target_unit'] = 'kg'
            elif goal_type == 'endurance':
                goal['target_value'] = 5
                goal['target_unit'] = 'km'
            elif goal_type == 'strength':
                goal['target_value'] = 20
                goal['target_unit'] = 'percent_increase'
        
        return goal
    
    def _make_achievable(self, goal: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Ensure goal is achievable and realistic"""
        goal_type = goal['goal_type']
        timeframe = goal.get('timeframe', 12)
        timeframe_unit = goal.get('timeframe_unit', 'weeks')
        
        # Convert timeframe to weeks for consistency
        timeframe_weeks = self._convert_to_weeks(timeframe, timeframe_unit)
        
        if goal_type == 'weight_loss' and goal['target_value']:
            # Safe weight loss is 0.5-1kg per week
            max_safe_loss = timeframe_weeks * 1.0  # 1kg per week max
            if goal['target_value'] > max_safe_loss:
                goal['target_value'] = max_safe_loss
                goal['adjusted'] = True
                goal['adjustment_reason'] = 'Adjusted for safe weight loss rate'
        
        elif goal_type == 'weight_gain' and goal['target_value']:
            # Safe weight gain is 0.25-0.5kg per week
            max_safe_gain = timeframe_weeks * 0.5
            if goal['target_value'] > max_safe_gain:
                goal['target_value'] = max_safe_gain
                goal['adjusted'] = True
                goal['adjustment_reason'] = 'Adjusted for safe weight gain rate'
        
        return goal
    
    def _make_relevant(self, goal: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Ensure goal is relevant to user's situation"""
        # Add relevance based on user's current state
        if context.age:
            if context.age > 50:
                goal['considerations'] = goal.get('considerations', [])
                goal['considerations'].append('Age-appropriate modifications recommended')
        
        if context.medical_conditions:
            goal['considerations'] = goal.get('considerations', [])
            goal['considerations'].append('Medical conditions require professional guidance')
        
        return goal
    
    def _make_time_bound(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure goal has clear time boundaries"""
        if not goal.get('target_date'):
            timeframe = goal.get('timeframe', 12)
            timeframe_unit = goal.get('timeframe_unit', 'weeks')
            goal['target_date'] = self._calculate_target_date(timeframe, timeframe_unit)
        
        # Add milestone dates
        goal['milestones'] = self._create_milestones(goal)
        
        return goal
    
    def _create_action_plan(self, goal: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Create detailed action plan for achieving the goal"""
        action_plan = {
            'weekly_targets': [],
            'recommended_activities': [],
            'nutrition_guidelines': [],
            'progress_tracking': [],
            'potential_obstacles': [],
            'success_strategies': []
        }
        
        goal_type = goal['goal_type']
        
        # Create weekly targets
        action_plan['weekly_targets'] = self._create_weekly_targets(goal)
        
        # Recommend activities
        action_plan['recommended_activities'] = self._recommend_activities(goal_type, context)
        
        # Nutrition guidelines
        action_plan['nutrition_guidelines'] = self._create_nutrition_guidelines(goal_type)
        
        # Progress tracking methods
        action_plan['progress_tracking'] = self._create_progress_tracking(goal_type)
        
        # Identify potential obstacles
        action_plan['potential_obstacles'] = self._identify_obstacles(goal, context)
        
        # Success strategies
        action_plan['success_strategies'] = self._create_success_strategies(goal_type)
        
        return action_plan
    
    def _create_weekly_targets(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create weekly targets leading to the main goal"""
        targets = []
        timeframe_weeks = self._convert_to_weeks(
            goal.get('timeframe', 12), 
            goal.get('timeframe_unit', 'weeks')
        )
        
        if goal['target_value'] and timeframe_weeks:
            weekly_increment = goal['target_value'] / timeframe_weeks
            
            for week in range(1, min(int(timeframe_weeks) + 1, 13)):  # Max 12 weeks shown
                target_value = weekly_increment * week
                targets.append({
                    'week': week,
                    'target': round(target_value, 1),
                    'unit': goal['target_unit']
                })
        
        return targets
    
    def _recommend_activities(self, goal_type: str, context: UserSessionContext) -> List[str]:
        """Recommend specific activities based on goal type"""
        activity_recommendations = {
            'weight_loss': [
                'Cardio exercises (30-45 minutes, 4-5 times per week)',
                'Strength training (2-3 times per week)',
                'Daily walks (10,000 steps)',
                'High-intensity interval training (HIIT)'
            ],
            'weight_gain': [
                'Strength training (3-4 times per week)',
                'Compound exercises (squats, deadlifts, bench press)',
                'Progressive overload training',
                'Adequate rest between workouts'
            ],
            'muscle_building': [
                'Resistance training (4-5 times per week)',
                'Progressive overload',
                'Compound movements',
                'Adequate protein intake'
            ],
            'endurance': [
                'Gradual running program',
                'Cross-training activities',
                'Interval training',
                'Long, steady-state cardio'
            ],
            'strength': [
                'Powerlifting movements',
                'Progressive overload',
                'Compound exercises',
                'Proper rest and recovery'
            ]
        }
        
        return activity_recommendations.get(goal_type, [
            'Regular physical activity',
            'Balanced exercise routine',
            'Consistency in training'
        ])
    
    def _create_nutrition_guidelines(self, goal_type: str) -> List[str]:
        """Create nutrition guidelines based on goal type"""
        nutrition_guidelines = {
            'weight_loss': [
                'Create a moderate caloric deficit (300-500 calories)',
                'Focus on whole, unprocessed foods',
                'Increase protein intake for satiety',
                'Stay hydrated with plenty of water'
            ],
            'weight_gain': [
                'Create a moderate caloric surplus (300-500 calories)',
                'Focus on nutrient-dense foods',
                'Increase healthy fats and complex carbs',
                'Eat frequent, balanced meals'
            ],
            'muscle_building': [
                'Consume adequate protein (1.6-2.2g per kg body weight)',
                'Time protein intake around workouts',
                'Include complex carbohydrates for energy',
                'Stay well-hydrated'
            ]
        }
        
        return nutrition_guidelines.get(goal_type, [
            'Maintain a balanced, nutritious diet',
            'Stay hydrated',
            'Eat regular, balanced meals'
        ])
    
    def _create_progress_tracking(self, goal_type: str) -> List[str]:
        """Create progress tracking methods"""
        tracking_methods = {
            'weight_loss': [
                'Weekly weigh-ins (same time, same conditions)',
                'Body measurements (waist, hips, arms)',
                'Progress photos',
                'Fitness performance metrics'
            ],
            'weight_gain': [
                'Weekly weigh-ins',
                'Muscle measurements',
                'Strength progression tracking',
                'Progress photos'
            ],
            'muscle_building': [
                'Strength progression logs',
                'Body measurements',
                'Progress photos',
                'Body composition analysis'
            ],
            'endurance': [
                'Running times and distances',
                'Heart rate monitoring',
                'Recovery time tracking',
                'Perceived exertion levels'
            ]
        }
        
        return tracking_methods.get(goal_type, [
            'Regular progress check-ins',
            'Performance metrics tracking',
            'Subjective wellness assessment'
        ])
    
    def _identify_obstacles(self, goal: Dict[str, Any], context: UserSessionContext) -> List[str]:
        """Identify potential obstacles to goal achievement"""
        obstacles = [
            'Lack of time for exercise',
            'Motivation fluctuations',
            'Social situations and food temptations',
            'Plateaus in progress'
        ]
        
        # Add context-specific obstacles
        if context.medical_conditions:
            obstacles.append('Managing health conditions during exercise')
        
        if goal['difficulty_level'] == 'challenging':
            obstacles.append('Ambitious timeline requiring high commitment')
        
        return obstacles
    
    def _create_success_strategies(self, goal_type: str) -> List[str]:
        """Create strategies for success"""
        return [
            'Start with small, manageable changes',
            'Track progress regularly',
            'Find an accountability partner or support group',
            'Celebrate small victories along the way',
            'Prepare for setbacks and have a recovery plan',
            'Focus on building sustainable habits',
            'Seek professional guidance when needed'
        ]
    
    def _format_goal_response(self, goal: Dict[str, Any], action_plan: Dict[str, Any]) -> str:
        """Format the goal analysis response"""
        response = f"🎯 **Goal Analysis Complete!**\n\n"
        
        # Goal summary
        response += f"**Your Goal:** {goal['description']}\n"
        if goal['target_value']:
            response += f"**Target:** {goal['target_value']} {goal['target_unit']}\n"
        if goal['target_date']:
            response += f"**Target Date:** {goal['target_date']}\n"
        response += f"**Goal Type:** {goal['goal_type'].replace('_', ' ').title()}\n"
        response += f"**Difficulty Level:** {goal['difficulty_level'].title()}\n\n"
        
        # Adjustments if any
        if goal.get('adjusted'):
            response += f"⚠️ **Goal Adjusted:** {goal['adjustment_reason']}\n\n"
        
        # Weekly targets preview
        if action_plan['weekly_targets']:
            response += f"📈 **Weekly Targets (First 4 weeks):**\n"
            for target in action_plan['weekly_targets'][:4]:
                response += f"• Week {target['week']}: {target['target']} {target['unit']}\n"
            response += "\n"
        
        # Key recommendations
        response += f"🏃 **Recommended Activities:**\n"
        for activity in action_plan['recommended_activities'][:3]:
            response += f"• {activity}\n"
        response += "\n"
        
        response += f"🥗 **Nutrition Guidelines:**\n"
        for guideline in action_plan['nutrition_guidelines'][:3]:
            response += f"• {guideline}\n"
        response += "\n"
        
        response += f"📊 **Progress Tracking:**\n"
        for method in action_plan['progress_tracking'][:3]:
            response += f"• {method}\n"
        response += "\n"
        
        # Success strategies
        response += f"💡 **Success Strategies:**\n"
        for strategy in action_plan['success_strategies'][:3]:
            response += f"• {strategy}\n"
        response += "\n"
        
        # Next steps
        response += f"🚀 **Next Steps:**\n"
        response += f"• I can create a personalized meal plan for your goal\n"
        response += f"• I can design a workout routine tailored to your needs\n"
        response += f"• We can set up progress tracking and check-in reminders\n\n"
        
        response += f"What would you like to work on next?"
        
        return response
    
    # Helper methods
    def _normalize_unit(self, unit: str) -> str:
        """Normalize measurement units"""
        unit_map = {
            'kg': 'kg', 'kilograms': 'kg', 'kilogram': 'kg',
            'lbs': 'lbs', 'pounds': 'lbs', 'pound': 'lbs', 'lb': 'lbs',
            'km': 'km', 'kilometers': 'km', 'kilometer': 'km',
            'miles': 'miles', 'mile': 'miles',
            'm': 'meters', 'meters': 'meters', 'meter': 'meters'
        }
        return unit_map.get(unit.lower(), unit)
    
    def _normalize_time_unit(self, unit: str) -> str:
        """Normalize time units"""
        unit_map = {
            'day': 'days', 'days': 'days',
            'week': 'weeks', 'weeks': 'weeks',
            'month': 'months', 'months': 'months',
            'year': 'years', 'years': 'years'
        }
        return unit_map.get(unit.lower(), unit)
    
    def _calculate_target_date(self, timeframe: int, unit: str) -> str:
        """Calculate target date based on timeframe"""
        now = datetime.now()
        
        if unit == 'days':
            target_date = now + timedelta(days=timeframe)
        elif unit == 'weeks':
            target_date = now + timedelta(weeks=timeframe)
        elif unit == 'months':
            target_date = now + timedelta(days=timeframe * 30)
        elif unit == 'years':
            target_date = now + timedelta(days=timeframe * 365)
        else:
            target_date = now + timedelta(weeks=12)  # Default
        
        return target_date.strftime('%Y-%m-%d')
    
    def _convert_to_weeks(self, timeframe: int, unit: str) -> float:
        """Convert timeframe to weeks"""
        if unit == 'days':
            return timeframe / 7
        elif unit == 'weeks':
            return timeframe
        elif unit == 'months':
            return timeframe * 4.33  # Average weeks per month
        elif unit == 'years':
            return timeframe * 52
        else:
            return 12  # Default
    
    def _assess_difficulty(self, goal: Dict[str, Any], context: UserSessionContext) -> str:
        """Assess goal difficulty level"""
        difficulty_score = 0
        
        # Time pressure
        timeframe_weeks = self._convert_to_weeks(
            goal.get('timeframe', 12), 
            goal.get('timeframe_unit', 'weeks')
        )
        
        if timeframe_weeks < 8:
            difficulty_score += 2
        elif timeframe_weeks < 16:
            difficulty_score += 1
        
        # Target ambition
        if goal['goal_type'] == 'weight_loss' and goal.get('target_value', 0) > 10:
            difficulty_score += 2
        elif goal['goal_type'] == 'weight_gain' and goal.get('target_value', 0) > 5:
            difficulty_score += 2
        
        # User experience level
        if context.activity_level.value == 'sedentary':
            difficulty_score += 1
        
        if difficulty_score >= 4:
            return 'challenging'
        elif difficulty_score >= 2:
            return 'moderate'
        else:
            return 'beginner'
    
    def _load_goal_patterns(self) -> Dict[str, List[str]]:
        """Load goal identification patterns"""
        return {
            'weight_loss': [
                r'lose\s+\d+.*(?:kg|pounds?|lbs?)',
                r'want to lose weight',
                r'shed.*(?:kg|pounds?|lbs?)',
                r'get thinner'
            ],
            'muscle_building': [
                r'build muscle',
                r'get stronger',
                r'bulk up',
                r'gain muscle'
            ]
        }
    
    def _load_time_patterns(self) -> List[str]:
        """Load time extraction patterns"""
        return [
            r'in\s+(\d+)\s*(days?|weeks?|months?)',
            r'within\s+(\d+)\s*(days?|weeks?|months?)',
            r'by\s+(\w+)'
        ]
    
    def _load_measurement_patterns(self) -> List[str]:
        """Load measurement extraction patterns"""
        return [
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilograms?|lbs?|pounds?)',
            r'(\d+(?:\.\d+)?)\s*(?:km|kilometers?|miles?)'
        ]
    
    def _create_milestones(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create milestone dates for goal achievement"""
        milestones = []
        
        if goal.get('target_date'):
            target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
            start_date = datetime.now()
            
            # Create quarterly milestones
            total_days = (target_date - start_date).days
            
            for i in [0.25, 0.5, 0.75, 1.0]:
                milestone_date = start_date + timedelta(days=int(total_days * i))
                milestone_value = goal.get('target_value', 0) * i if goal.get('target_value') else None
                
                milestones.append({
                    'date': milestone_date.strftime('%Y-%m-%d'),
                    'percentage': int(i * 100),
                    'target_value': round(milestone_value, 1) if milestone_value else None,
                    'description': f"{int(i * 100)}% of goal achieved"
                })
        
        return milestones
