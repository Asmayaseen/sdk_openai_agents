import streamlit as st
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List

def set_theme(theme: str):
    """Set the application theme."""
    if theme == 'dark':
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #FFFFFF;
                color: #262730;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

def load_custom_css():
    """Load custom CSS for the application."""
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #00C851;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background-color: #F0F2F6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border-left: 4px solid #00C851;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            max-width: 80%;
        }
        
        .user-message {
            background-color: #E3F2FD;
            margin-left: auto;
            text-align: right;
        }
        
        .assistant-message {
            background-color: #F1F8E9;
            margin-right: auto;
        }
        
        .sidebar .sidebar-content {
            background-color: #F8F9FA;
        }
        
        .goal-card {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            background-color: #E0E0E0;
            border-radius: 0.5rem;
            height: 1rem;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            background-color: #00C851;
            border-radius: 0.5rem;
            height: 100%;
            transition: width 0.3s ease;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def format_date(date_obj):
    """Format date for display."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d %H:%M")
    return str(date_obj)

def calculate_bmi(weight: float, height: float) -> Dict[str, Any]:
    """Calculate BMI and return result with category."""
    try:
        # Convert height from cm to meters
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
            color = "#FFA726"
        elif bmi < 25:
            category = "Normal weight"
            color = "#66BB6A"
        elif bmi < 30:
            category = "Overweight"
            color = "#FFA726"
        else:
            category = "Obese"
            color = "#EF5350"
        
        return {
            'bmi': round(bmi, 1),
            'category': category,
            'color': color,
            'healthy_range': '18.5 - 24.9'
        }
    except Exception as e:
        return {
            'error': f"BMI calculation failed: {str(e)}"
        }

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user input data."""
    errors = []
    
    # Validate age
    if 'age' in data:
        if not isinstance(data['age'], int) or data['age'] < 16 or data['age'] > 100:
            errors.append("Age must be between 16 and 100")
    
    # Validate weight
    if 'weight' in data:
        if not isinstance(data['weight'], (int, float)) or data['weight'] < 30 or data['weight'] > 300:
            errors.append("Weight must be between 30 and 300 kg")
    
    # Validate height
    if 'height' in data:
        if not isinstance(data['height'], (int, float)) or data['height'] < 100 or data['height'] > 250:
            errors.append("Height must be between 100 and 250 cm")
    
    # Validate email
    if 'email' in data:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append("Invalid email format")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def generate_user_id():
    """Generate unique user ID."""
    import uuid
    return str(uuid.uuid4())

def format_workout_duration(minutes: int) -> str:
    """Format workout duration for display."""
    if minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"

def calculate_calories_burned(activity: str, duration_minutes: int, weight_kg: float) -> int:
    """Calculate estimated calories burned."""
    # MET values for different activities
    met_values = {
        'walking': 3.5,
        'jogging': 7.0,
        'running': 9.0,
        'cycling': 6.0,
        'swimming': 8.0,
        'weightlifting': 6.0,
        'yoga': 3.0,
        'pilates': 4.0,
        'dancing': 5.0,
        'hiking': 6.0
    }
    
    # Get MET value or use default
    met = met_values.get(activity.lower(), 5.0)
    
    # Calculate calories: MET × weight (kg) × duration (hours)
    calories = met * weight_kg * (duration_minutes / 60)
    
    return int(calories)

def format_nutrition_info(nutrition_data: Dict[str, Any]) -> str:
    """Format nutrition information for display."""
    if not nutrition_data:
        return "No nutrition data available"
    
    formatted = []
    
    if 'calories' in nutrition_data:
        formatted.append(f"🔥 Calories: {nutrition_data['calories']}")
    
    if 'protein' in nutrition_data:
        formatted.append(f"🥩 Protein: {nutrition_data['protein']}g")
    
    if 'carbs' in nutrition_data:
        formatted.append(f"🍞 Carbs: {nutrition_data['carbs']}g")
    
    if 'fat' in nutrition_data:
        formatted.append(f"🥑 Fat: {nutrition_data['fat']}g")
    
    if 'fiber' in nutrition_data:
        formatted.append(f"🌾 Fiber: {nutrition_data['fiber']}g")
    
    return " | ".join(formatted)

def create_progress_chart_data(progress_data: List[Dict[str, Any]]) -> Dict[str, List]:
    """Create data structure for progress charts."""
    dates = []
    weights = []
    energy_levels = []
    
    for entry in progress_data:
        if 'date' in entry:
            dates.append(entry['date'])
        if 'weight' in entry:
            weights.append(entry['weight'])
        if 'energy_level' in entry:
            energy_levels.append(entry['energy_level'])
    
    return {
        'dates': dates,
        'weights': weights,
        'energy_levels': energy_levels
    }

def get_motivational_message(progress_score: int) -> str:
    """Get motivational message based on progress score."""
    if progress_score >= 80:
        return "🎉 Outstanding progress! You're crushing your goals!"
    elif progress_score >= 60:
        return "💪 Great work! You're making solid progress!"
    elif progress_score >= 40:
        return "👍 Good effort! Keep pushing forward!"
    else:
        return "🌟 Every step counts! You've got this!"

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    import html
    return html.escape(text.strip())

def log_user_activity(user_id: str, activity: str, details: Dict[str, Any] = None):
    """Log user activity (placeholder for actual logging)."""
    # In a real application, this would log to a file or database
    timestamp = datetime.now().isoformat()
    log_entry = {
        'user_id': user_id,
        'activity': activity,
        'timestamp': timestamp,
        'details': details or {}
    }
    # This is a placeholder - in production, implement proper logging
    pass