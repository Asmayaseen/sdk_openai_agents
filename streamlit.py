#!/usr/bin/env python3
import asyncio
import csv
import sqlite3
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from jinja2 import Template
from pathlib import Path
import os
import nest_asyncio

# Apply nest_asyncio for Jupyter compatibility
nest_asyncio.apply()

# ------------ Context Model ------------
class UserSessionContext(BaseModel):
    name: str
    uid: str
    goal: Optional[str] = None
    diet_preferences: Optional[str] = None
    lifestyle: Optional[str] = None
    meal_plan: List[str] = []
    workouts: List[str] = []
    injury_notes: Optional[str] = None
    progress_logs: List[Dict[str, str]] = []
    theme: str = "light"

# ------------ Constants ------------
DB_PATH = 'wellness.db'
DEFAULT_USER = {
    "name": "Asma Yaseen",
    "uid": "00436743",
    "goal": "Lose 5kg in 2 months",
    "diet_preferences": "Vegetarian",
    "lifestyle": "Busy office worker",
    "theme": "light"
}

# ------------ Database Functions ------------
@st.cache_resource
def init_database() -> sqlite3.Connection:
    """Initialize and cache SQLite database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            name TEXT,
            goal TEXT,
            diet_preferences TEXT,
            lifestyle TEXT,
            theme TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            date TEXT,
            notes TEXT,
            metrics TEXT,
            FOREIGN KEY(uid) REFERENCES users(uid)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            plan TEXT,
            date TEXT,
            FOREIGN KEY(uid) REFERENCES users(uid)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            workout TEXT,
            date TEXT,
            FOREIGN KEY(uid) REFERENCES users(uid)
        )
    ''')
    
    conn.commit()
    return conn

# ------------ Report Generation ------------
def generate_pdf_report(context: UserSessionContext) -> bytes:
    """Generate PDF report from user context"""
    try:
        from weasyprint import HTML
        import tempfile
        
        # Create report directory if it doesn't exist
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        # HTML template
        template = Template('''
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    h1 { color: #2e86c1; }
                    h2 { color: #28b463; }
                    .header { background-color: #f2f3f4; padding: 20px; }
                    .section { margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Wellness Report for {{name}}</h1>
                    <p>Generated on {{date}}</p>
                </div>
                
                <div class="section">
                    <h2>Personal Details</h2>
                    <p><strong>Goal:</strong> {{goal}}</p>
                    <p><strong>Diet Preferences:</strong> {{diet_preferences}}</p>
                    <p><strong>Lifestyle:</strong> {{lifestyle}}</p>
                </div>
                
                <div class="section">
                    <h2>Meal Plan</h2>
                    <ul>
                        {% for meal in meal_plan %}
                        <li>{{ meal }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Workout Plan</h2>
                    <ul>
                        {% for workout in workouts %}
                        <li>{{ workout }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </body>
        </html>
        ''')
        
        # Render HTML
        html = template.render(
            name=context.name,
            date=datetime.now().strftime('%Y-%m-%d'),
            goal=context.goal,
            diet_preferences=context.diet_preferences,
            lifestyle=context.lifestyle,
            meal_plan=context.meal_plan,
            workouts=context.workouts
        )
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            HTML(string=html).write_pdf(f.name)
            with open(f.name, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            os.unlink(f.name)
            
        return pdf_bytes
        
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        raise

# ------------ Agent Implementation ------------
class WellnessPlannerAgent:
    def __init__(self, context: UserSessionContext):
        self.context = context

    async def run(self, prompt: str) -> str:
        """Simulate agent response"""
        await asyncio.sleep(1)  # Simulate processing time
        
        if "meal plan" in prompt.lower():
            meal_plan = """7-Day Vegetarian Meal Plan:
            1. Monday: Chickpea curry with brown rice
            2. Tuesday: Lentil soup with whole wheat bread
            3. Wednesday: Vegetable stir-fry with tofu
            4. Thursday: Spinach and cheese omelette
            5. Friday: Mushroom risotto
            6. Saturday: Stuffed bell peppers
            7. Sunday: Vegetable lasagna"""
            
            # Save to database
            conn = init_database()
            conn.execute(
                "INSERT INTO meal_plans (uid, plan, date) VALUES (?, ?, ?)",
                (self.context.uid, meal_plan, datetime.now().strftime('%Y-%m-%d'))
            )
            conn.commit()
            
            self.context.meal_plan = [meal_plan]
            return meal_plan
            
        elif "workout" in prompt.lower():
            workout_plan = """Weekly Workout Plan:
            - Monday: Yoga (30 mins)
            - Wednesday: Strength training (45 mins)
            - Friday: Cardio (30 mins)
            - Sunday: Walking (60 mins)"""
            
            # Save to database
            conn = init_database()
            conn.execute(
                "INSERT INTO workouts (uid, workout, date) VALUES (?, ?, ?)",
                (self.context.uid, workout_plan, datetime.now().strftime('%Y-%m-%d'))
            )
            conn.commit()
            
            self.context.workouts = [workout_plan]
            return workout_plan
            
        return f"I'll help with your goal: {self.context.goal}. For '{prompt}', I recommend..."

# ------------ Streamlit App Components ------------
def init_session_state() -> None:
    """Initialize Streamlit session state"""
    if 'context' not in st.session_state:
        # Try to load user from database
        conn = init_database()
        user = conn.execute(
            "SELECT * FROM users WHERE uid = ?", 
            (DEFAULT_USER["uid"],)
        ).fetchone()
        
        if user:
            st.session_state.context = UserSessionContext(**user)
        else:
            # Create new user
            conn.execute(
                "INSERT INTO users (uid, name, goal, diet_preferences, lifestyle, theme) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    DEFAULT_USER["uid"],
                    DEFAULT_USER["name"],
                    DEFAULT_USER["goal"],
                    DEFAULT_USER["diet_preferences"],
                    DEFAULT_USER["lifestyle"],
                    DEFAULT_USER["theme"]
                )
            )
            conn.commit()
            st.session_state.context = UserSessionContext(**DEFAULT_USER)
        
        # Initialize empty chat history
        st.session_state.chat_history = []

def reset_session() -> None:
    """Reset the user session"""
    conn = init_database()
    conn.execute(
        "UPDATE users SET goal = ?, diet_preferences = ?, lifestyle = ? WHERE uid = ?",
        ("", "", "", st.session_state.context.uid)
    )
    conn.commit()
    
    st.session_state.context.goal = ""
    st.session_state.context.diet_preferences = ""
    st.session_state.context.lifestyle = ""
    st.session_state.context.meal_plan = []
    st.session_state.context.workouts = []
    st.session_state.chat_history = []
    st.rerun()

def export_data() -> None:
    """Export user data to CSV"""
    try:
        conn = init_database()
        filename = f"wellness_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write user data
            writer.writerow(["User Data"])
            writer.writerow(["Name", "Goal", "Diet Preferences", "Lifestyle"])
            user = conn.execute(
                "SELECT name, goal, diet_preferences, lifestyle FROM users WHERE uid = ?",
                (st.session_state.context.uid,)
            ).fetchone()
            writer.writerow([user["name"], user["goal"], user["diet_preferences"], user["lifestyle"]])
            
            # Write progress data
            writer.writerow([])
            writer.writerow(["Progress History"])
            writer.writerow(["Date", "Notes", "Metrics"])
            progress = conn.execute(
                "SELECT date, notes, metrics FROM progress WHERE uid = ? ORDER BY date DESC",
                (st.session_state.context.uid,)
            ).fetchall()
            for row in progress:
                writer.writerow([row["date"], row["notes"], row["metrics"]])
            
            # Write meal plans
            writer.writerow([])
            writer.writerow(["Meal Plans"])
            meals = conn.execute(
                "SELECT date, plan FROM meal_plans WHERE uid = ? ORDER BY date DESC",
                (st.session_state.context.uid,)
            ).fetchall()
            for row in meals:
                writer.writerow([row["date"], row["plan"]])
            
            # Write workouts
            writer.writerow([])
            writer.writerow(["Workout Plans"])
            workouts = conn.execute(
                "SELECT date, workout FROM workouts WHERE uid = ? ORDER BY date DESC",
                (st.session_state.context.uid,)
            ).fetchall()
            for row in workouts:
                writer.writerow([row["date"], row["workout"]])
        
        st.toast(f"📤 Data exported to {filename}", icon="✅")
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def toggle_theme() -> None:
    """Toggle between light and dark theme"""
    conn = init_database()
    new_theme = "dark" if st.session_state.context.theme == "light" else "light"
    st.session_state.context.theme = new_theme
    
    conn.execute(
        "UPDATE users SET theme = ? WHERE uid = ?",
        (new_theme, st.session_state.context.uid)
    )
    conn.commit()
    
    # Apply theme
    if new_theme == "dark":
        st.markdown("""
        <style>
            .stApp { background-color: #1E1E1E; color: white; }
            .sidebar .sidebar-content { background-color: #2E2E2E; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stApp { background-color: white; color: black; }
            .sidebar .sidebar-content { background-color: #f0f2f6; }
        </style>
        """, unsafe_allow_html=True)

async def render_chat() -> None:
    """Render the main chat interface"""
    st.title("💬 Wellness Assistant Chat")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about meal plans, workouts, or health advice..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Thinking..."):
                try:
                    agent = WellnessPlannerAgent(st.session_state.context)
                    response = await agent.run(prompt)
                    response_placeholder.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")

def save_progress(note: str, metrics: str) -> None:
    """Save progress entry to database"""
    try:
        conn = init_database()
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO progress (uid, date, notes, metrics) VALUES (?, ?, ?, ?)",
            (st.session_state.context.uid, today, note, metrics)
        )
        conn.commit()
        
        st.session_state.context.progress_logs.append({
            "date": today,
            "note": note,
            "metrics": metrics
        })
        st.toast("📝 Progress saved!", icon="✅")
    except Exception as e:
        st.error(f"Failed to save progress: {str(e)}")

def display_progress_history() -> None:
    """Display historical progress entries"""
    try:
        conn = init_database()
        progress = conn.execute(
            "SELECT date, notes, metrics FROM progress WHERE uid = ? ORDER BY date DESC",
            (st.session_state.context.uid,)
        ).fetchall()
        
        if not progress:
            st.info("No progress entries yet. Start tracking your journey!")
            return
            
        for row in progress:
            with st.expander(f"📅 {row['date']}"):
                if row['metrics']:
                    st.metric("Metrics", row['metrics'])
                st.write(row['notes'])
    except Exception as e:
        st.error(f"Error loading progress: {str(e)}")

def display_meal_plans() -> None:
    """Display saved meal plans"""
    try:
        conn = init_database()
        meals = conn.execute(
            "SELECT date, plan FROM meal_plans WHERE uid = ? ORDER BY date DESC",
            (st.session_state.context.uid,)
        ).fetchall()
        
        if not meals:
            st.info("No meal plans yet. Ask your assistant for one!")
            return
            
        for row in meals:
            with st.expander(f"🍽️ Meal Plan ({row['date']})"):
                st.write(row['plan'])
    except Exception as e:
        st.error(f"Error loading meal plans: {str(e)}")

def display_workouts() -> None:
    """Display saved workout plans"""
    try:
        conn = init_database()
        workouts = conn.execute(
            "SELECT date, workout FROM workouts WHERE uid = ? ORDER BY date DESC",
            (st.session_state.context.uid,)
        ).fetchall()
        
        if not workouts:
            st.info("No workout plans yet. Ask your assistant for one!")
            return
            
        for row in workouts:
            with st.expander(f"🏋️ Workout Plan ({row['date']})"):
                st.write(row['workout'])
    except Exception as e:
        st.error(f"Error loading workouts: {str(e)}")

def profile_settings() -> None:
    """Display and edit user profile"""
    st.header("👤 Profile Settings")
    
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.context.name)
        goal = st.text_area("Health Goal", value=st.session_state.context.goal)
        diet = st.text_input("Diet Preferences", value=st.session_state.context.diet_preferences)
        lifestyle = st.text_input("Lifestyle", value=st.session_state.context.lifestyle)
        
        if st.form_submit_button("💾 Save Profile"):
            try:
                conn = init_database()
                conn.execute(
                    "UPDATE users SET name = ?, goal = ?, diet_preferences = ?, lifestyle = ? WHERE uid = ?",
                    (name, goal, diet, lifestyle, st.session_state.context.uid)
                )
                conn.commit()
                
                st.session_state.context.name = name
                st.session_state.context.goal = goal
                st.session_state.context.diet_preferences = diet
                st.session_state.context.lifestyle = lifestyle
                
                st.toast("Profile updated!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {str(e)}")

# ------------ Main Application ------------
async def main_async() -> None:
    """Async main application entry point"""
    # Initialize app
    st.set_page_config(
        page_title="AI Wellness Planner",
        page_icon="🏋️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session
    init_session_state()
    
    # Apply theme
    if st.session_state.context.theme == "dark":
        st.markdown("""
        <style>
            .stApp { background-color: #1E1E1E; color: white; }
            .sidebar .sidebar-content { background-color: #2E2E2E; }
        </style>
        """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🧘 Wellness Dashboard")
        
        # Theme toggle
        theme_label = "🌙 Dark Mode" if st.session_state.context.theme == "light" else "☀️ Light Mode"
        if st.button(theme_label):
            toggle_theme()
            st.rerun()
        
        # Navigation
        page = st.radio(
            "Menu",
            ["💬 Chat", "📊 Dashboard", "🍽️ Meal Plans", "🏋️ Workouts", "📈 Progress", "👤 Profile"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Session controls
        st.header("Session Controls")
        if st.button("🔄 Reset Session"):
            reset_session()
        if st.button("💾 Export Data"):
            export_data()
    
    # Main content area
    if page == "💬 Chat":
        await render_chat()
        
    elif page == "📊 Dashboard":
        st.title("📊 Wellness Dashboard")
        st.write(f"Welcome back, {st.session_state.context.name}!")
        
        cols = st.columns(2)
        with cols[0]:
            st.metric("Current Goal", st.session_state.context.goal or "Not set")
        with cols[1]:
            st.metric("Diet Preference", st.session_state.context.diet_preferences or "Not set")
        
        st.divider()
        
        st.subheader("Recent Progress")
        display_progress_history()
        
        st.subheader("Quick Actions")
        if st.button("📝 Add Progress Entry"):
            with st.form("quick_progress"):
                note = st.text_area("Note")
                metrics = st.text_input("Metrics")
                if st.form_submit_button("Save"):
                    save_progress(note, metrics)
                    st.rerun()
    
    elif page == "🍽️ Meal Plans":
        st.title("🍽️ Meal Plans")
        display_meal_plans()
        
        if st.button("➕ Request New Meal Plan"):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "Create a new meal plan for me"
            })
            st.switch_page("💬 Chat")
    
    elif page == "🏋️ Workouts":
        st.title("🏋️ Workout Plans")
        display_workouts()
        
        if st.button("➕ Request New Workout Plan"):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "Create a new workout plan for me"
            })
            st.switch_page("💬 Chat")
    
    elif page == "📈 Progress":
        st.title("📈 Progress Tracker")
        
        with st.expander("➕ Add New Entry", expanded=True):
            with st.form("progress_form"):
                note = st.text_area("Today's notes")
                metrics = st.text_input("Metrics (e.g., Weight: 68kg)")
                if st.form_submit_button("💾 Save Entry"):
                    save_progress(note, metrics)
                    st.rerun()
        
        st.divider()
        st.subheader("History")
        display_progress_history()
    
    elif page == "👤 Profile":
        profile_settings()
    
    # Report generation (available when there's data)
    if (page in ["📊 Dashboard", "🍽️ Meal Plans", "🏋️ Workouts"] and 
        (st.session_state.context.meal_plan or st.session_state.context.workouts)):
        st.divider()
        if st.button("📄 Generate Wellness Report"):
            with st.spinner("Generating report..."):
                try:
                    pdf_bytes = generate_pdf_report(st.session_state.context)
                    st.download_button(
                        label="⬇️ Download Full Report",
                        data=pdf_bytes,
                        file_name=f"wellness_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Report generation failed: {str(e)}")

def main() -> None:
    """Wrapper for async main function"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()