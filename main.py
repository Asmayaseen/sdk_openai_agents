

import asyncio
import sys
import os
from datetime import datetime
import argparse

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai_agents import RunContextWrapper, Runner

from agent import HealthWellnessAgent
from context import UserSessionContext
from utils.streaming import StreamingHandler
from hooks import HealthWellnessHooks

# Import tools
from tools.goal_analyzer import GoalAnalyzerTool
from tools.meal_planner import MealPlannerTool
from tools.workout_recommender import WorkoutRecommenderTool
from tools.scheduler import CheckinSchedulerTool
from tools.progress_tracker import ProgressTrackerTool

# Import specialized agents for handoffs
from agents.escalation_agent import EscalationAgent
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="🏥 Health & Wellness Planner Agent")
    parser.add_argument("--mode", choices=["cli", "streamlit", "api"], default="cli",
                        help="Run mode: cli for command line, streamlit for web interface, api for REST API")
    parser.add_argument("--user_name", type=str, default="User",
                        help="User name for the session")
    parser.add_argument("--user_id", type=int, default=1001,
                        help="User ID for the session")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--streaming", action="store_true", default=True,
                        help="Enable real-time streaming")
    return parser.parse_args()


async def run_cli_mode(args):
    """Run the application in CLI mode with streaming"""
    print("\n" + "="*60)
    print("🏥 HEALTH & WELLNESS PLANNER AGENT")
    print("="*60)
    print("Powered by OpenAI API")
    print("Your AI-powered personal health companion with real-time streaming")
    print("\nType your message (type 'exit', 'quit', or 'bye' to stop)")
    print("Type 'help' for available commands")
    print("Type 'status' to see your session information")
    print("-"*60)

    # Initialize user context wrapped in RunContextWrapper
    user_context = RunContextWrapper(
    context=UserSessionContext(
        name=args.user_name,
        user_id=str(args.user_id)

    )
)


    # Initialize tools
    tools = [
        GoalAnalyzerTool(),
        MealPlannerTool(),
        WorkoutRecommenderTool(),
        CheckinSchedulerTool(),
        ProgressTrackerTool(),
    ]

    # Initialize specialized agents for handoffs
    handoffs = {
        "EscalationAgent": EscalationAgent(),
        "NutritionExpertAgent": NutritionExpertAgent(),
        "InjurySupportAgent": InjurySupportAgent()
    }

    # Initialize hooks if debug enabled
    hooks = HealthWellnessHooks() if args.debug else None

    # Initialize agent with tools, handoffs, and hooks
    agent = HealthWellnessAgent(tools=tools, handoffs=handoffs, hooks=hooks)
    streaming_handler = StreamingHandler()

    conversation_count = 0
    start_time = datetime.now()

    try:
        while True:
            try:
                user_input = input(f"\n{args.user_name}: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in {'exit', 'quit', 'bye'}:
                    print(f"\n👋 Thank you for using Health & Wellness Planner, {args.user_name}!")
                    break

                if user_input.lower() == 'help':
                    print_help()
                    continue

                if user_input.lower() == 'status':
                    print_status(user_context.context, conversation_count, start_time)
                    continue

                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("🏥 Health & Wellness Planner - Session Cleared")
                    continue

                # Process user input with streaming or normal response
                print(f"\n🤖 Health Coach: ", end="", flush=True)

                if args.streaming:
                    await streaming_handler.stream_response(
                        agent=agent,
                        user_input=user_input,
                        context=user_context,
                        hooks=hooks
                    )
                    print()  # Newline after streaming response
                else:
                    response = await agent.process_message(user_input, user_context)
                    print(response)

                conversation_count += 1

            except KeyboardInterrupt:
                print("\n\n⛔ Interrupted by user. Type 'exit' to quit properly.")
                continue
            except Exception as e:
                print(f"\n❌ Error processing request: {str(e)}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
                continue

    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye, {args.user_name}!")
    finally:
        # Print session summary
        print_session_summary(user_context.context, conversation_count, start_time)
def print_help():
    """Print available commands"""
    print("\n📋 Available Commands:")
    print("  help     - Show this help message")
    print("  status   - Show current session information")
    print("  clear    - Clear the screen")
    print("  exit     - Exit the application")
    print("\n💡 Example interactions:")
    print("  - 'I want to lose 5kg in 2 months'")
    print("  - 'I'm vegetarian and need a meal plan'")
    print("  - 'Create a workout routine for beginners'")
    print("  - 'I have knee pain, need modified exercises'")
    print("  - 'I want to speak with a human coach'")
    print("  - 'I'm diabetic and need special diet advice'")

def print_status(context: UserSessionContext, conversation_count: int, start_time: datetime):
    """Print current session status"""
    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n📊 Session Status:")
    print(f"  User: {context.name} (ID: {context.uid})")
    print(f"  Duration: {duration:.0f} seconds")
    print(f"  Conversations: {conversation_count}")
    print(f"  Goal: {context.goal if context.goal else 'Not set'}")
    print(f"  Diet Preferences: {context.diet_preferences if context.diet_preferences else 'Not specified'}")
    print(f"  Handoffs: {len(context.handoff_logs)}")
    print(f"  Progress Logs: {len(context.progress_logs)}")


def print_session_summary(context: UserSessionContext, conversation_count: int, start_time: datetime):
    """Print session summary"""
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n{'='*60}")
    print("🧾 SESSION SUMMARY")
    print("="*60)
    print(f"🕒 Total Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")
    print(f"💬 Total Conversations: {conversation_count}")
    print(f"🎯 Final Goal: {context.goal if context.goal else 'Not set'}")
    print(f"🥗 Diet Preferences: {context.diet_preferences if context.diet_preferences else 'Not specified'}")

    if context.handoff_logs:
        print(f"\n🔄 Agent Handoffs ({len(context.handoff_logs)}):")
        for i, handoff in enumerate(context.handoff_logs[-3:], 1):
            print(f"  {i}. {handoff}")

    if context.progress_logs:
        print(f"\n📈 Progress Updates ({len(context.progress_logs)}):")
        for update in context.progress_logs[-3:]:
            print(f"  • {update.get('description', 'Progress update')}")

    print(f"\n🏥 Thank you for using Health & Wellness Planner!")
    print("="*60)


def run_streamlit_mode():
    """Run the application in Streamlit mode"""
    import subprocess
    import sys

    print("🚀 Starting Streamlit application...")
    print("📱 Access the application at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Streamlit server stopped.")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {str(e)}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

def run_api_mode(args):
    """Run the application in API mode"""
    print("🚀 Starting FastAPI server...")
    print(f"📡 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")

    try:
        import uvicorn
        from api.main import app

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=args.debug,
            log_level="debug" if args.debug else "info"
        )
    except ImportError:
        print("❌ Error: FastAPI and uvicorn are required for API mode")
        print("💡 Install with: pip install fastapi uvicorn")
    except KeyboardInterrupt:
        print("\n⏹️  API server stopped.")
    except Exception as e:
        print(f"❌ Error starting API server: {str(e)}")
def main():
    """Main entry point"""
    args = parse_args()
    print(f"🏥 Health & Wellness Planner starting in {args.mode} mode...")
    if args.mode == "cli":
        asyncio.run(run_cli_mode(args))
    elif args.mode == "streamlit":
        run_streamlit_mode()
    elif args.mode == "api":
        run_api_mode(args)
    else:
        print(f"❌ Unknown mode: {args.mode}")
        sys.exit(1)
if __name__ == "__main__":
    main()
