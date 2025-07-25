import sys
import traceback

try:
    import asyncio
    import logging
    import os
    import uuid
    from datetime import datetime
    from typing import Dict, List, Optional, Any
    import streamlit as st
    from pathlib import Path

    # Local imports
    from context import UserSessionContext, GoalType, DietaryPreference, MedicalCondition
    from agents.wellness_agent import WellnessAgent
    from agents.fitness_agent import FitnessAgent
    from agents.progress_agent import ProgressAgent
    from agents.nutrition_agent import NutritionAgent
    from agents.mental_health_agent import MentalHealthAgent
    from agents.injury_support_agent import InjurySupportAgent
    from agents.human_coach_agent import HumanCoachAgent


    from tools.progress_tracker import ProgressTrackerTool
    from tools.workout_recommender import WorkoutRecommenderTool
    from tools.meal_planner import MealPlannerTool
    from tools.goal_analyzer import GoalAnalyzerTool
    from tools.scheduler import CheckinSchedulerTool

    from utils.database import db_manager
    from utils.report_generator import generate_pdf_report
    from utils.ui_helpers import (
        load_custom_css, set_theme, display_chat_message, show_typing_indicator,
        display_metric_card, display_goal_card, create_progress_chart, create_bmi_gauge,
        display_meal_plan_summary, display_workout_plan_summary, get_motivational_message
    )
    from config import config

    # Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Page configuration
    st.set_page_config(
        page_title="🌿 AI Health & Wellness Coach",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    class WellnessAgentOrchestrator:
        """Orchestrates multiple specialized agents for health and wellness coaching."""

        def __init__(self):
            self.agents = {
                "wellness": WellnessAgent(),
                "nutrition": NutritionAgent(),
                "fitness": FitnessAgent(),
                "progress": ProgressAgent(),
                "mental_health": MentalHealthAgent(),
                "injury_support": InjurySupportAgent(),
                "human_coach": HumanCoachAgent(),
            
            }
            self.tools = {
                "progress_tracker": ProgressTrackerTool(),
                "workout_recommender": WorkoutRecommenderTool(),
                "meal_planner": MealPlannerTool(),
                "goal_analyzer": GoalAnalyzerTool(),
                "scheduler": CheckinSchedulerTool()
            }
            self.current_agent = "wellness"

        def set_context(self, context: UserSessionContext):
            """Set context for all agents."""
            for agent in self.agents.values():
                agent.set_context(context)

        async def process_message(self, message: str, context: UserSessionContext) -> str:
            """Process message through appropriate agent with potential handoffs."""
            # Determine if we need to switch agents
            current_agent_obj = self.agents[self.current_agent]

            # Check if current agent should hand off
            handoff_target = await current_agent_obj.should_handoff(message)
            if handoff_target and handoff_target in self.agents:
                # Log handoff
                context.log_handoff(
                    from_agent=self.current_agent,
                    to_agent=handoff_target,
                    reason=f"User message requires {handoff_target} specialization"
                )
                self.current_agent = handoff_target
                current_agent_obj = self.agents[self.current_agent]

            # Process message with current agent
            response_chunks = []
            async for chunk in current_agent_obj.process_message(message):
                response_chunks.append(chunk)
                yield chunk

            # Store conversation in context
            full_response = "".join(response_chunks)
            context.add_message("user", message)
            context.add_message("assistant", full_response, self.current_agent)

            # Save to database
            db_manager.save_conversation_message(context.user_id, "user", message)
            db_manager.save_conversation_message(context.user_id, "assistant", full_response, self.current_agent)

        async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
            """Execute a specific tool."""
            if tool_name not in self.tools:
                return {"error": f"Tool {tool_name} not found"}
            tool = self.tools[tool_name]
            return await tool.execute(**kwargs)

    # -------------------------------
    # Streamlit Session State Setup
    # -------------------------------
    def init_session_state():
        """Initialize Streamlit session state."""
        if 'context' not in st.session_state:
            # Try to load existing user or create new one
            user_id = st.query_params.get("user_id", str(uuid.uuid4()))

            context = db_manager.load_user_context(user_id)
            if not context:
                # Create new user context
                context = UserSessionContext(
                    user_id=user_id,
                    name="New User",
                    goal_type=GoalType.GENERAL_FITNESS,
                    dietary_preference=DietaryPreference.NO_PREFERENCE
                )

            st.session_state.context = context
            st.session_state.orchestrator = WellnessAgentOrchestrator()
            st.session_state.orchestrator.set_context(context)
            st.session_state.chat_history = []
            st.session_state.is_typing = False

    def save_context():
        """Save current context to database."""
        if 'context' in st.session_state:
            db_manager.save_user_context(st.session_state.context)

    # -------------------------------
    # Message Handling
    # -------------------------------
    async def handle_user_message(message: str):
        """Handle user message with streaming response."""
        context = st.session_state.context
        orchestrator = st.session_state.orchestrator

        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })

        # Show typing indicator
        st.session_state.is_typing = True

        # Process message and stream response
        response_chunks = []
        response_placeholder = st.empty()

        try:
            async for chunk in orchestrator.process_message(message, context):
                response_chunks.append(chunk)
                # Update the response in real-time
                response_placeholder.markdown("".join(response_chunks))

            # Add complete response to chat history
            full_response = "".join(response_chunks)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_response,
                "agent": orchestrator.current_agent,
                "timestamp": datetime.now()
            })

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg,
                "agent": "system",
                "timestamp": datetime.now()
            })
            logger.error(f"Error processing message: {e}")

        finally:
            st.session_state.is_typing = False
            save_context()

    # -------------------------------
    # Sidebar UI
    # -------------------------------
    def render_sidebar():
        """Render the sidebar with user info and controls."""
        with st.sidebar:
            st.title("🌿 Wellness Dashboard")

            context = st.session_state.context

            # User profile section
            st.subheader("👤 Profile")

            # Editable user information
            with st.expander("Edit Profile", expanded=False):
                new_name = st.text_input("Name", value=context.name)
                new_age = st.number_input("Age", min_value=16, max_value=100, value=(context.age or 25))
                new_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=(context.weight or 70.0), step=0.1)
                new_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=(context.height or 170.0), step=0.1)

                new_goal_type = st.selectbox(
                    "Goal Type",
                    options=[g.value for g in GoalType],
                    index=list(GoalType).index(context.goal_type) if context.goal_type else 0,
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                new_dietary_pref = st.selectbox(
                    "Dietary Preference",
                    options=[d.value for d in DietaryPreference],
                    index=list(DietaryPreference).index(context.dietary_preference),
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                new_activity_level = st.selectbox(
                    "Activity Level",
                    options=["sedentary", "light", "moderate", "active", "very_active"],
                    index=["sedentary", "light", "moderate", "active", "very_active"].index(context.activity_level),
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                if st.button("Update Profile"):
                    # Update context
                    context.name = new_name
                    context.age = new_age
                    context.weight = new_weight
                    context.height = new_height
                    context.goal_type = GoalType(new_goal_type)
                    context.dietary_preference = DietaryPreference(new_dietary_pref)
                    context.activity_level = new_activity_level

                    save_context()
                    st.success("Profile updated!")
                    st.rerun()

            # Display current goal
            if context.goal_type:
                display_goal_card(context)

            # Quick stats
            st.subheader("📊 Quick Stats")
            bmi = context.calculate_bmi()
            if bmi:
                display_metric_card("BMI", f"{bmi}", "Body Mass Index")
                # BMI Gauge
                if st.checkbox("Show BMI Chart"):
                    fig = create_bmi_gauge(bmi)
                    st.plotly_chart(fig, use_container_width=True)

            progress_count = len(context.progress_history)
            display_metric_card("Progress Entries", str(progress_count), "Total logged")

            # Quick actions
            st.subheader("⚡ Quick Actions")
            if st.button("📊 Generate Report"):
                with st.spinner("Generating report..."):
                    try:
                        report_path = generate_pdf_report(context)
                        if report_path and os.path.exists(report_path):
                            with open(report_path, "rb") as pdf_file:
                                pdf_data = pdf_file.read()
                            st.download_button(
                                label="📄 Download Report",
                                data=pdf_data,
                                file_name=f"wellness_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                            st.success("Report generated successfully!")
                        else:
                            st.error("Failed to generate report")
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")

            if st.button("🍎 Quick Meal Plan"):
                st.session_state.pending_message = "Please create a 7-day meal plan based on my dietary preferences"
                st.rerun()

            if st.button("💪 Quick Workout"):
                st.session_state.pending_message = "Please create a workout plan based on my fitness level and goals"
                st.rerun()

            if st.button("📈 Log Progress"):
                st.session_state.show_progress_form = True

            # Theme toggle
            current_theme = getattr(context, "theme", "light")
            if st.button(f"🎨 Switch to {'Dark' if current_theme == 'light' else 'Light'} Theme"):
                context.theme = 'dark' if current_theme == 'light' else 'light'
                save_context()
                st.rerun()

            # Agent status
            st.subheader("🤖 Current Agent")
            current_agent = st.session_state.orchestrator.current_agent
            agent_emoji = {
                "wellness": "🌿", "nutrition": "🍎", "fitness": "💪", "progress": "📊",
                "mental_health": "🧠", "injury_support": "🩹", "human_coach": "👨‍🏫", "escalation": "🔼"
            }
            st.info(f"{agent_emoji.get(current_agent, '🤖')} {current_agent.replace('_',' ').title()} Agent")

    # -------------------------------
    # Progress Form
    # -------------------------------
    def render_progress_form():
        """Render progress logging form."""
        if st.session_state.get('show_progress_form', False):
            with st.expander("📈 Log Progress", expanded=True):
                metric = st.selectbox(
                    "Metric",
                    options=["weight", "body_fat", "muscle_mass", "steps", "calories_burned", "sleep_hours", "water_intake"],
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                value = st.number_input("Value", min_value=0.0, step=0.1)

                unit_options = {
                    "weight": ["kg", "lbs"],
                    "body_fat": ["%"],
                    "muscle_mass": ["kg", "lbs"],
                    "steps": [""],
                    "calories_burned": ["kcal"],
                    "sleep_hours": ["hours"],
                    "water_intake": ["L", "oz"]
                }

                unit = st.selectbox("Unit", options=unit_options.get(metric, [""]))
                notes = st.text_area("Notes (optional)")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Log Progress"):
                        # Add progress to context
                        st.session_state.context.add_progress_update(metric, value, unit, notes)

                        # Save to database
                        db_manager.save_progress_entry(
                            st.session_state.context.user_id,
                            metric, value, unit, notes
                        )

                        save_context()
                        st.success(f"Logged {metric}: {value}{unit}")
                        st.session_state.show_progress_form = False
                        st.rerun()

                with col2:
                    if st.button("Cancel"):
                        st.session_state.show_progress_form = False
                        st.rerun()

    # -------------------------------
    # Main Chat Interface
    # -------------------------------
    def render_main_content():
        """Render the main chat interface."""
        context = st.session_state.context

        # Apply theme
        set_theme(getattr(context, "theme", "light"))
        load_custom_css()

        # Main header
        st.markdown('<h1 class="main-header">🌿 AI Health & Wellness Coach</h1>', unsafe_allow_html=True)

        # Welcome message for new users
        if not st.session_state.chat_history:
            welcome_agent = st.session_state.orchestrator.agents["wellness"]
            welcome_msg = welcome_agent.get_welcome_message()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": welcome_msg,
                "agent": "wellness",
                "timestamp": datetime.now()
            })

        # Chat container
        chat_container = st.container()

        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                display_chat_message(
                    role=message["role"],
                    content=message["content"],
                    agent_type=message.get("agent")
                )

            # Show typing indicator if AI is responding
            if st.session_state.get('is_typing', False):
                show_typing_indicator()

        # Progress form
        render_progress_form()

        # Chat input (floating style)
        st.markdown('<div class="floating-input">', unsafe_allow_html=True)

        # Handle pending messages (from quick action buttons)
        if st.session_state.get('pending_message'):
            user_input = st.session_state.pending_message
            st.session_state.pending_message = None

            # Process the message
            asyncio.run(handle_user_message(user_input))
            st.rerun()

        # Chat input
        user_input = st.chat_input("Ask me about nutrition, fitness, or wellness...")

        if user_input:
            # Process the message
            asyncio.run(handle_user_message(user_input))
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Analytics Tab
    # -------------------------------
    def render_analytics_tab():
        """Render analytics and progress visualizations."""
        context = st.session_state.context

        st.header("📊 Analytics & Progress")

        # Motivational message
        progress_count = len(context.progress_history)
        goal_type = context.goal_type.value.replace('_', ' ') if context.goal_type else "general wellness"
        motivational_msg = get_motivational_message(progress_count, goal_type)
        st.success(motivational_msg)

        # Progress charts
        if context.progress_history:
            # Get unique metrics
            metrics = list(set(entry.metric for entry in context.progress_history))

            if metrics:
                selected_metric = st.selectbox("Select metric to visualize:", metrics)

                fig = create_progress_chart(context, selected_metric)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No data available for {selected_metric}")
        else:
            st.info("No progress data available yet. Start logging your progress to see charts!")

        # Recent progress table
        if context.progress_history:
            st.subheader("Recent Progress Entries")

            # Convert to display format
            recent_entries = context.progress_history[-10:]  # Last 10 entries

            for entry in reversed(recent_entries):
                date_str = entry.date.strftime("%Y-%m-%d %H:%M") if hasattr(entry.date, 'strftime') else str(entry.date)
                col1, col2, col3, col4 = st.columns([2, 2, 1, 3])

                with col1:
                    st.text(date_str)
                with col2:
                    st.text(entry.metric.title())
                with col3:
                    st.text(f"{entry.value}{entry.unit}")
                with col4:
                    st.text(entry.notes or "")

    # -------------------------------
    # Plans Tab
    # -------------------------------
    def render_plans_tab():
        """Render meal and workout plans."""
        context = st.session_state.context

        st.header("📋 My Plans")

        # Meal Plan Section
        st.subheader("🍎 Meal Plan")
        if getattr(context, "meal_plan", None):
            display_meal_plan_summary(context.meal_plan)
        else:
            st.info("No meal plan created yet. Ask the nutrition agent to create one!")
            if st.button("Create Meal Plan"):
                st.session_state.pending_message = "Please create a personalized meal plan for me"
                st.rerun()

        # Workout Plan Section
        st.subheader("💪 Workout Plan")
        if getattr(context, "workout_plan", None):
            display_workout_plan_summary(context.workout_plan)
        else:
            st.info("No workout plan created yet. Ask the fitness agent to create one!")
            if st.button("Create Workout Plan"):
                st.session_state.pending_message = "Please create a personalized workout plan for me"
                st.rerun()

    # -------------------------------
    # App Entry
    # -------------------------------
    def main():
        """Main application entry point."""
        # Initialize session state
        init_session_state()

        # Render sidebar
        render_sidebar()

        # Main content tabs
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "📋 Plans"])

        with tab1:
            render_main_content()

        with tab2:
            render_analytics_tab()

        with tab3:
            render_plans_tab()

        # Auto-save context periodically
        if st.session_state.get('last_save'):
            time_since_save = datetime.now() - st.session_state.last_save
            if time_since_save.seconds > 30:  # Save every 30 seconds
                save_context()
                st.session_state.last_save = datetime.now()
        else:
            st.session_state.last_save = datetime.now()

    if __name__ == "__main__":
        main()

except Exception:
    traceback.print_exc(file=sys.stderr)