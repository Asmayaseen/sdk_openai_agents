import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd


from context import UserSessionContext

def set_theme(theme: str):
    """Set the application theme."""
    if theme == 'dark':
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
                color: #FAFAFA;
            }
            .chat-message {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .user-message {
                background: linear-gradient(135deg, #00C851 0%, #007E3A 100%);
                color: white;
            }
            .assistant-message {
                background: rgba(255, 255, 255, 0.08);
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
                background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                color: #262730;
            }
            .chat-message {
                background: white;
                border: 1px solid #E0E0E0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .user-message {
                background: linear-gradient(135deg, #00C851 0%, #00A344 100%);
                color: white;
                margin-left: 20%;
            }
            .assistant-message {
                background: white;
                color: #262730;
                margin-right: 20%;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

def load_custom_css():
    """Load custom CSS for modern chat interface."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main-header {
            font-family: 'Inter', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00C851 0%, #007E3A 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 15px;
            margin-bottom: 1rem;
        }
        
        .chat-message {
            padding: 1rem 1.5rem;
            margin: 0.8rem 0;
            border-radius: 20px;
            max-width: 75%;
            word-wrap: break-word;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .user-message {
            margin-left: auto;
            margin-right: 0;
            text-align: right;
            border-bottom-right-radius: 5px;
        }
        
        .assistant-message {
            margin-left: 0;
            margin-right: auto;
            border-bottom-left-radius: 5px;
            border: 1px solid rgba(0, 200, 81, 0.2);
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            padding: 1rem 1.5rem;
            margin: 0.8rem 0;
            margin-right: auto;
            max-width: 75%;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            border-bottom-left-radius: 5px;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #00C851;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border-left: 5px solid #00C851;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #00C851;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.5rem;
        }
        
        .progress-ring {
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }
        
        .goal-card {
            background: linear-gradient(135deg, #00C851 0%, #007E3A 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            text-align: center;
        }
        
        .floating-input {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 600px;
            z-index: 1000;
        }
        
        .agent-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(0, 200, 81, 0.1);
            color: #00C851;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #F8F9FA 0%, #E9ECEF 100%);
        }
        
        .stSelectbox > div > div {
            background-color: white;
            border-radius: 10px;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #00C851 0%, #007E3A 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 200, 81, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_chat_message(role: str, content: str, agent_type: Optional[str] = None):
    """Display a chat message with proper styling."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        agent_badge = f'<div class="agent-badge">{agent_type or "Assistant"}</div>' if agent_type else ""
        st.markdown(f"""
        <div class="chat-message assistant-message">
            {agent_badge}
            {content}
        </div>
        """, unsafe_allow_html=True)

def show_typing_indicator():
    """Display typing indicator animation."""
    st.markdown("""
    <div class="typing-indicator">
        <span style="margin-right: 0.5rem;">AI is thinking</span>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_metric_card(title: str, value: str, subtitle: str = "", color: str = "#00C851"):
    """Display a metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{value}</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">{title}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_goal_card(context: UserSessionContext):
    """Display user's current goal in a card."""
    if not context.goal_type:
        return
    
    goal_text = context.goal_type.value.replace('_', ' ').title()
    target_text = ""
    if context.goal_target:
        target_text = f"Target: {context.goal_target}{context.goal_unit.value if context.goal_unit else ''}"
    
    deadline_text = ""
    if context.goal_deadline:
        deadline_text = f"Deadline: {context.goal_deadline.strftime('%B %d, %Y')}"
    
    st.markdown(f"""
    <div class="goal-card">
        <h3 style="margin: 0 0 1rem 0;">🎯 Current Goal</h3>
        <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">{goal_text}</div>
        <div style="opacity: 0.9;">{target_text}</div>
        <div style="opacity: 0.8; font-size: 0.9rem;">{deadline_text}</div>
    </div>
    """, unsafe_allow_html=True)

def create_progress_chart(context: UserSessionContext, metric: str = "weight") -> Optional[go.Figure]:
    """Create a progress chart for a specific metric."""
    if not context.progress_history:
        return None
    
    # Filter progress entries for the specific metric
    metric_entries = [entry for entry in context.progress_history if entry.metric.lower() == metric.lower()]
    
    if not metric_entries:
        return None
    
    # Sort by date
    metric_entries.sort(key=lambda x: x.date)
    
    # Extract data
    dates = [entry.date for entry in metric_entries]
    values = [entry.value for entry in metric_entries]
    
    # Create the chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        line=dict(color='#00C851', width=3),
        marker=dict(size=8, color='#00C851'),
        name=metric.title()
    ))
    
    fig.update_layout(
        title=f"{metric.title()} Progress",
        xaxis_title="Date",
        yaxis_title=f"{metric.title()} ({metric_entries[0].unit if metric_entries[0].unit else ''})",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_bmi_gauge(bmi: float) -> go.Figure:
    """Create a BMI gauge chart."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI"},
        gauge = {
            'axis': {'range': [None, 40]},
            'bar': {'color': "#00C851"},
            'steps': [
                {'range': [0, 18.5], 'color': "#FFA726"},
                {'range': [18.5, 25], 'color': "#66BB6A"},
                {'range': [25, 30], 'color': "#FFA726"},
                {'range': [30, 40], 'color': "#EF5350"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 25
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def display_meal_plan_summary(meal_plan: Dict[str, Any]):
    """Display a summary of the meal plan."""
    if not meal_plan:
        st.info("No meal plan available. Ask your nutrition agent to create one!")
        return
    
    st.subheader("📋 Current Meal Plan")
    
    for day, plan in meal_plan.items():
        with st.expander(f"{day}", expanded=False):
            if isinstance(plan, dict):
                if 'breakfast' in plan:
                    st.write(f"🌅 **Breakfast:** {plan['breakfast'].get('name', 'N/A')}")
                if 'lunch' in plan:
                    st.write(f"☀️ **Lunch:** {plan['lunch'].get('name', 'N/A')}")
                if 'dinner' in plan:
                    st.write(f"🌙 **Dinner:** {plan['dinner'].get('name', 'N/A')}")
                if 'total_calories' in plan:
                    st.write(f"🔥 **Total Calories:** {plan['total_calories']}")

def display_workout_plan_summary(workout_plan: Dict[str, Any]):
    """Display a summary of the workout plan."""
    if not workout_plan:
        st.info("No workout plan available. Ask your fitness agent to create one!")
        return
    
    st.subheader("💪 Current Workout Plan")
    
    for day, plan in workout_plan.items():
        with st.expander(f"{day}", expanded=False):
            if isinstance(plan, dict):
                st.write(f"🎯 **Focus:** {plan.get('focus', 'N/A')}")
                st.write(f"⏱️ **Duration:** {plan.get('duration', 'N/A')}")
                st.write(f"📈 **Intensity:** {plan.get('intensity', 'N/A')}")
                
                exercises = plan.get('exercises', [])
                if exercises:
                    st.write("**Exercises:**")
                    for i, exercise in enumerate(exercises, 1):
                        if isinstance(exercise, dict):
                            st.write(f"{i}. {exercise.get('name', 'Unknown Exercise')}")

def format_date(date_obj) -> str:
    """Format date for display."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d %H:%M")
    return str(date_obj)

def calculate_bmi_category(bmi: float) -> tuple[str, str]:
    """Calculate BMI category and return category and color."""
    if bmi < 18.5:
        return "Underweight", "#FFA726"
    elif bmi < 25:
        return "Normal weight", "#66BB6A"
    elif bmi < 30:
        return "Overweight", "#FFA726"
    else:
        return "Obese", "#EF5350"

def get_motivational_message(progress_count: int, goal_type: str = "general wellness") -> str:
    """Get motivational message based on progress."""
    if progress_count >= 20:
        return f"🎉 Amazing! You've made {progress_count} progress updates on your {goal_type} journey!"
    elif progress_count >= 10:
        return f"💪 Great work! {progress_count} updates show real commitment to your {goal_type} goals!"
    elif progress_count >= 5:
        return f"👍 You're building momentum with {progress_count} progress updates!"
    else:
        return f"🌟 Every step counts! Keep tracking your {goal_type} progress!"

def display_agent_handoff_log(handoff_logs: List[Dict[str, Any]], limit: int = 5):
    """Display recent agent handoffs."""
    if not handoff_logs:
        return
    
    st.subheader("🔄 Recent Agent Handoffs")
    
    for log in handoff_logs[-limit:]:
        timestamp = log.get('timestamp', '')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = timestamp.strftime("%H:%M")
            except:
                time_str = timestamp[:5] if len(timestamp) > 5 else timestamp
        else:
            time_str = str(timestamp)[:5]
        
        st.caption(f"{time_str}: {log['from_agent']} → {log['to_agent']}")
