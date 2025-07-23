"""
Check-in Scheduler Tool for Health & Wellness Planner Agent
Schedules progress check-ins and reminders for user goals
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from context import UserSessionContext

class CheckinSchedulerTool:
    """
    Schedules regular check-ins and reminders for health and wellness goals
    Creates personalized reminder schedules based on user preferences and goals
    """
    
    def __init__(self):
        self.name = "CheckinSchedulerTool"
        self.description = "Schedules progress check-ins and reminders for health goals"
        
        # Scheduling templates
        self.schedule_templates = self._load_schedule_templates()
        self.reminder_types = self._load_reminder_types()
    
    async def run(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """
        Create a check-in schedule for the user
        
        Args:
            user_input: User's scheduling request
            context: User session context with goals and preferences
            
        Returns:
            Personalized check-in schedule with reminders
        """
        try:
            # Analyze scheduling requirements
            requirements = self._analyze_schedule_requirements(user_input, context)
            
            # Create check-in schedule
            schedule = self._create_checkin_schedule(requirements, context)
            
            # Add reminder settings
            schedule['reminders'] = self._create_reminder_settings(requirements, context)
            
            # Format response
            response = self._format_schedule_response(schedule, requirements)
            
            return {
                'response': response,
                'schedule': schedule,
                'requirements': requirements,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"I'd love to help you set up check-ins and reminders! Could you tell me how often you'd like to track your progress? For example: 'Weekly check-ins' or 'Daily reminders for workouts'.",
                'error': str(e),
                'success': False
            }
    
    def _analyze_schedule_requirements(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Analyze user input to determine scheduling requirements"""
        user_input_lower = user_input.lower()
        
        requirements = {
            'checkin_frequency': self._extract_checkin_frequency(user_input_lower),
            'reminder_types': self._extract_reminder_types(user_input_lower),
            'preferred_times': self._extract_preferred_times(user_input_lower),
            'goal_type': context.goal_type.value if context.goal_type else 'general_fitness',
            'duration_weeks': self._extract_duration(user_input_lower, context),
            'notification_preferences': context.notification_preferences,
            'timezone': context.timezone
        }
        
        return requirements
    
    def _extract_checkin_frequency(self, user_input: str) -> str:
        """Extract check-in frequency from user input"""
        frequency_keywords = {
            'daily': ['daily', 'every day', 'each day'],
            'weekly': ['weekly', 'every week', 'once a week'],
            'biweekly': ['biweekly', 'every two weeks', 'twice a month'],
            'monthly': ['monthly', 'every month', 'once a month']
        }
        
        for frequency, keywords in frequency_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                return frequency
        
        return 'weekly'  # Default
    
    def _extract_reminder_types(self, user_input: str) -> List[str]:
        """Extract types of reminders requested"""
        reminder_keywords = {
            'workout': ['workout', 'exercise', 'training', 'gym'],
            'meal': ['meal', 'eating', 'nutrition', 'diet'],
            'water': ['water', 'hydration', 'drink'],
            'progress': ['progress', 'check-in', 'tracking', 'measurement'],
            'motivation': ['motivation', 'encouragement', 'inspiration']
        }
        
        requested_reminders = []
        
        for reminder_type, keywords in reminder_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                requested_reminders.append(reminder_type)
        
        # Default reminders if none specified
        if not requested_reminders:
            requested_reminders = ['progress', 'workout']
        
        return requested_reminders
    
    def _extract_preferred_times(self, user_input: str) -> List[str]:
        """Extract preferred reminder times"""
        time_keywords = {
            'morning': ['morning', 'am', '8am', '9am', 'early'],
            'afternoon': ['afternoon', 'pm', '2pm', '3pm', 'lunch'],
            'evening': ['evening', '6pm', '7pm', '8pm', 'after work'],
            'night': ['night', '9pm', '10pm', 'before bed']
        }
        
        preferred_times = []
        
        for time_period, keywords in time_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                preferred_times.append(time_period)
        
        # Default to morning if no preference specified
        if not preferred_times:
            preferred_times = ['morning']
        
        return preferred_times
    
    def _extract_duration(self, user_input: str, context: UserSessionContext) -> int:
        """Extract schedule duration in weeks"""
        import re
        
        # Look for duration patterns
        duration_patterns = [
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?',
            r'for\s+(\d+)\s*weeks?',
            r'for\s+(\d+)\s*months?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, user_input)
            if match:
                duration = int(match.group(1))
                if 'month' in pattern:
                    return duration * 4  # Convert months to weeks
                return duration
        
        # Use goal timeframe if available
        if context.goal and context.goal.get('timeframe'):
            goal_timeframe = context.goal['timeframe']
            goal_unit = context.goal.get('timeframe_unit', 'weeks')
            
            if goal_unit == 'months':
                return goal_timeframe * 4
            elif goal_unit == 'days':
                return goal_timeframe // 7
            else:
                return goal_timeframe
        
        return 12  # Default 12 weeks
    
    def _create_checkin_schedule(self, requirements: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Create a comprehensive check-in schedule"""
        schedule = {
            'created_at': datetime.now().isoformat(),
            'frequency': requirements['checkin_frequency'],
            'duration_weeks': requirements['duration_weeks'],
            'goal_type': requirements['goal_type'],
            'checkin_dates': [],
            'milestone_dates': [],
            'reminder_schedule': []
        }
        
        # Generate check-in dates
        schedule['checkin_dates'] = self._generate_checkin_dates(
            requirements['checkin_frequency'],
            requirements['duration_weeks']
        )
        
        # Generate milestone dates
        schedule['milestone_dates'] = self._generate_milestone_dates(
            requirements['duration_weeks'],
            context
        )
        
        # Create reminder schedule
        schedule['reminder_schedule'] = self._create_reminder_schedule(
            requirements,
            schedule['checkin_dates']
        )
        
        return schedule
    
    def _generate_checkin_dates(self, frequency: str, duration_weeks: int) -> List[Dict[str, Any]]:
        """Generate check-in dates based on frequency"""
        checkin_dates = []
        start_date = datetime.now()
        
        # Determine interval based on frequency
        if frequency == 'daily':
            interval_days = 1
        elif frequency == 'weekly':
            interval_days = 7
        elif frequency == 'biweekly':
            interval_days = 14
        elif frequency == 'monthly':
            interval_days = 30
        else:
            interval_days = 7  # Default to weekly
        
        # Generate dates
        current_date = start_date
        checkin_number = 1
        
        while current_date <= start_date + timedelta(weeks=duration_weeks):
            checkin_dates.append({
                'checkin_number': checkin_number,
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': current_date.strftime('%A'),
                'week_number': ((current_date - start_date).days // 7) + 1,
                'focus_areas': self._get_checkin_focus_areas(checkin_number, frequency)
            })
            
            current_date += timedelta(days=interval_days)
            checkin_number += 1
        
        return checkin_dates
    
    def _generate_milestone_dates(self, duration_weeks: int, context: UserSessionContext) -> List[Dict[str, Any]]:
        """Generate milestone dates for major progress points"""
        milestones = []
        start_date = datetime.now()
        
        # Create milestones at 25%, 50%, 75%, and 100% of duration
        milestone_percentages = [0.25, 0.5, 0.75, 1.0]
        
        for percentage in milestone_percentages:
            milestone_date = start_date + timedelta(weeks=int(duration_weeks * percentage))
            
            milestones.append({
                'percentage': int(percentage * 100),
                'date': milestone_date.strftime('%Y-%m-%d'),
                'week_number': int(duration_weeks * percentage),
                'title': self._get_milestone_title(percentage),
                'description': self._get_milestone_description(percentage, context),
                'celebration_ideas': self._get_celebration_ideas(percentage)
            })
        
        return milestones
    
    def _create_reminder_schedule(self, requirements: Dict[str, Any], checkin_dates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create detailed reminder schedule"""
        reminders = []
        
        for reminder_type in requirements['reminder_types']:
            for time_preference in requirements['preferred_times']:
                reminder = {
                    'type': reminder_type,
                    'time': time_preference,
                    'frequency': self._get_reminder_frequency(reminder_type),
                    'message_templates': self._get_reminder_messages(reminder_type),
                    'enabled': True
                }
                reminders.append(reminder)
        
        return reminders
    
    def _create_reminder_settings(self, requirements: Dict[str, Any], context: UserSessionContext) -> Dict[str, Any]:
        """Create reminder settings configuration"""
        return {
            'enabled': True,
            'timezone': requirements['timezone'],
            'notification_preferences': requirements['notification_preferences'],
            'reminder_types': requirements['reminder_types'],
            'preferred_times': requirements['preferred_times'],
            'frequency': requirements['checkin_frequency']
        }
    
    def _get_checkin_focus_areas(self, checkin_number: int, frequency: str) -> List[str]:
        """Get focus areas for each check-in"""
        base_areas = ['progress_review', 'goal_adjustment']
        
        # Add specific focus areas based on check-in number and frequency
        if checkin_number == 1:
            base_areas.extend(['baseline_establishment', 'expectation_setting'])
        elif checkin_number % 4 == 0:  # Every 4th check-in
            base_areas.extend(['comprehensive_review', 'plan_optimization'])
        else:
            base_areas.extend(['motivation_boost', 'obstacle_discussion'])
        
        return base_areas
    
    def _get_milestone_title(self, percentage: float) -> str:
        """Get title for milestone based on percentage"""
        titles = {
            0.25: "Quarter Way There! 🎯",
            0.5: "Halfway Milestone! 🏃‍♀️",
            0.75: "Three-Quarters Complete! 💪",
            1.0: "Goal Achievement! 🎉"
        }
        return titles.get(percentage, "Progress Milestone")
    
    def _get_milestone_description(self, percentage: float, context: UserSessionContext) -> str:
        """Get description for milestone"""
        descriptions = {
            0.25: "Time to assess your initial progress and make any needed adjustments to your plan.",
            0.5: "You're halfway to your goal! Let's celebrate your progress and refine your strategy.",
            0.75: "You're in the home stretch! Time to push through and maintain momentum.",
            1.0: "Congratulations on reaching your goal! Time to celebrate and set new challenges."
        }
        return descriptions.get(percentage, "Progress checkpoint")
    
    def _get_celebration_ideas(self, percentage: float) -> List[str]:
        """Get celebration ideas for milestones"""
        celebrations = {
            0.25: [
                "Treat yourself to a healthy meal at your favorite restaurant",
                "Buy a new piece of workout gear",
                "Share your progress with friends and family"
            ],
            0.5: [
                "Plan a fun active outing (hiking, dancing, sports)",
                "Get a massage or spa treatment",
                "Update your progress photos and measurements"
            ],
            0.75: [
                "Buy new workout clothes or equipment",
                "Plan a weekend getaway focused on wellness",
                "Treat yourself to a fitness class you've wanted to try"
            ],
            1.0: [
                "Celebrate with a special dinner or event",
                "Share your success story to inspire others",
                "Set an exciting new fitness challenge",
                "Reward yourself with something you've been wanting"
            ]
        }
        return celebrations.get(percentage, ["Celebrate your progress!"])
    
    def _get_reminder_frequency(self, reminder_type: str) -> str:
        """Get frequency for different reminder types"""
        frequencies = {
            'workout': 'daily',
            'meal': 'daily',
            'water': 'daily',
            'progress': 'weekly',
            'motivation': 'weekly'
        }
        return frequencies.get(reminder_type, 'weekly')
    
    def _get_reminder_messages(self, reminder_type: str) -> List[str]:
        """Get message templates for different reminder types"""
        messages = {
            'workout': [
                "Time to get moving! Your workout is scheduled for today. 💪",
                "Your body is counting on you! Let's crush today's workout. 🏋️‍♀️",
                "Every workout brings you closer to your goal. You've got this! 🎯"
            ],
            'meal': [
                "Fuel your body right! Time for a nutritious meal. 🥗",
                "Your meal plan is your roadmap to success. Stay on track! 🍎",
                "Healthy eating = healthy living. Make good choices today! 🥑"
            ],
            'water': [
                "Hydration check! Time to drink some water. 💧",
                "Your body needs water to perform at its best. Drink up! 🚰",
                "Stay hydrated, stay healthy! Have a glass of water now. 💦"
            ],
            'progress': [
                "Time for your weekly check-in! How are you feeling about your progress? 📊",
                "Progress review time! Let's see how far you've come. 📈",
                "Weekly reflection: What went well? What can we improve? 🤔"
            ],
            'motivation': [
                "You're doing amazing! Keep up the great work. 🌟",
                "Remember why you started. You're stronger than you think! 💪",
                "Every small step counts. You're making progress! 👏"
            ]
        }
        return messages.get(reminder_type, ["Keep up the great work!"])
    
    def _format_schedule_response(self, schedule: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Format the schedule response"""
        response = f"📅 **Your Personalized Check-in Schedule**\n\n"
        
        # Schedule overview
        response += f"**Schedule Overview:**\n"
        response += f"• Frequency: {schedule['frequency'].title()} check-ins\n"
        response += f"• Duration: {schedule['duration_weeks']} weeks\n"
        response += f"• Goal Type: {schedule['goal_type'].replace('_', ' ').title()}\n"
        response += f"• Total Check-ins: {len(schedule['checkin_dates'])}\n\n"
        
        # Upcoming check-ins
        response += f"📋 **Upcoming Check-ins:**\n"
        for checkin in schedule['checkin_dates'][:4]:  # Show first 4 check-ins
            response += f"**Week {checkin['week_number']}** - {checkin['date']} ({checkin['day_of_week']})\n"
            focus_areas = ', '.join([area.replace('_', ' ').title() for area in checkin['focus_areas']])
            response += f"   Focus: {focus_areas}\n\n"
        
        if len(schedule['checkin_dates']) > 4:
            response += f"   ... and {len(schedule['checkin_dates']) - 4} more check-ins\n\n"
        
        # Milestone dates
        response += f"🎯 **Major Milestones:**\n"
        for milestone in schedule['milestone_dates']:
            response += f"**{milestone['title']}** - Week {milestone['week_number']} ({milestone['date']})\n"
            response += f"   {milestone['description']}\n\n"
        
        # Reminder settings
        response += f"🔔 **Reminder Settings:**\n"
        for reminder in schedule['reminder_schedule']:
            response += f"• **{reminder['type'].replace('_', ' ').title()}** reminders: {reminder['frequency'].title()}\n"
            response += f"   Preferred time: {reminder['time'].title()}\n"
        response += "\n"
        
        # Sample reminder messages
        response += f"💬 **Sample Reminder Messages:**\n"
        for reminder in schedule['reminder_schedule'][:2]:  # Show first 2 types
            response += f"**{reminder['type'].replace('_', ' ').title()}:** \"{reminder['message_templates'][0]}\"\n"
        response += "\n"
        
        # Tips for success
        response += f"💡 **Tips for Successful Check-ins:**\n"
        response += f"• Be honest about your progress and challenges\n"
        response += f"• Celebrate small wins along the way\n"
        response += f"• Use setbacks as learning opportunities\n"
        response += f"• Adjust your plan based on what's working\n"
        response += f"• Stay consistent with your check-ins\n\n"
        
        # Next steps
        response += f"🚀 **Next Steps:**\n"
        response += f"• I'll send you reminders based on your preferences\n"
        response += f"• We can adjust the schedule anytime based on your needs\n"
        response += f"• I can help you prepare for each check-in with specific questions\n\n"
        
        response += f"Your first check-in is scheduled for {schedule['checkin_dates'][0]['date']}. Are you ready to start your journey?"
        
        return response
    
    def _load_schedule_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load schedule templates for different goals"""
        return {
            'weight_loss': {
                'recommended_frequency': 'weekly',
                'key_metrics': ['weight', 'measurements', 'energy_levels'],
                'focus_areas': ['nutrition_adherence', 'exercise_consistency', 'motivation']
            },
            'muscle_building': {
                'recommended_frequency': 'biweekly',
                'key_metrics': ['strength_gains', 'measurements', 'workout_performance'],
                'focus_areas': ['progressive_overload', 'nutrition_timing', 'recovery']
            },
            'endurance': {
                'recommended_frequency': 'weekly',
                'key_metrics': ['distance', 'time', 'heart_rate', 'perceived_exertion'],
                'focus_areas': ['training_consistency', 'recovery', 'nutrition']
            }
        }
    
    def _load_reminder_types(self) -> Dict[str, Dict[str, Any]]:
        """Load reminder type configurations"""
        return {
            'workout': {
                'default_frequency': 'daily',
                'best_times': ['morning', 'evening'],
                'message_tone': 'motivational'
            },
            'meal': {
                'default_frequency': 'daily',
                'best_times': ['morning', 'afternoon', 'evening'],
                'message_tone': 'supportive'
            },
            'progress': {
                'default_frequency': 'weekly',
                'best_times': ['morning'],
                'message_tone': 'reflective'
            }
        }
