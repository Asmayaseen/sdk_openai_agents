📘 README.md — Health & Wellness Planner Agent
🧠 Project: Health & Wellness Planner Agent
AI-powered agent system to provide users with personalized 7-day meal plans, goal tracking, injury support, and wellness recommendations using OpenAI Agents SDK, Chainlit, and Streamlit.

📁 Folder Structure
arduino
Copy
Edit
health_wellness_agent/
├── main.py
├── agent.py
├── context.py
├── hooks.py
├── config.py
├── chainlit_app.py
├── utils/
│   ├── streaming.py
│   └── report.py
├── tools/
│   ├── goal_analyzer.py
│   ├── meal_planner.py
│   ├── workout_recommender.py
│   ├── schedular.py
│   └── tracker.py
├── .env
├── pyproject.toml
└── README.md
⚙️ Core Features
✅ Personalized Meal Plan (7-day, dietary preference-based)

✅ Beginner-level Workout Plan

✅ Smart Goal Analysis

✅ Health Progress Tracker

✅ Injury Support Agent

✅ Chainlit-based live chat interface

✅ PDF plan report export

🚀 How to Run the Project
📌 Python 3.12+ required

1. Create Virtual Environment
bash
Copy
Edit
uv venv
2. Activate Environment
bash
Copy
Edit
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
3. Add All Dependencies
bash
Copy
Edit
uv add chainlit fpdf nest-asyncio openai openai-agents pandas pydantic python-dotenv rich streamlit
💬 Run as Chat App with Chainlit
bash
Copy
Edit
chainlit run chainlit_app.py
🖥️ Run from CLI (Console)
bash
Copy
Edit
python main.py
📄 .env File
Create a .env file in the root:

env
Copy
Edit
OPENAI_API_KEY=your_openai_api_key_here
📦 Dependencies (Defined in pyproject.toml)
chainlit>=2.6.0

fpdf>=1.7.2

nest-asyncio>=1.6.0

openai>=1.93.0

openai-agents>=0.1.0

pandas>=2.3.0

pydantic>=2.11.7

python-dotenv>=1.1.1

rich>=13.7.1

streamlit>=1.46.1

📊 PDF Wellness Report
After generating your plan, a personalized .pdf report is created using the FPDF library in /utils/report.py.

💡 Possible Future Additions
Admin Dashboard (for coaches/trainers)

Daily Email Reminders

Supabase/SQLite integration for saving sessions

👩‍💻 Created by
Asma Yaseen — Governor Sindh GenAI Hackathon Participant
🗓️ July 2025