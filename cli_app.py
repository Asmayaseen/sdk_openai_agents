#!/usr/bin/env python3
"""
CLI Health & Wellness Coach
Multi-agent health assistance with command-line interface
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from agents.wellness_agent import WellnessAgent
from agents.nutrition_expert_agent import NutritionAgent  
from agents.fitness_agent import FitnessAgent
from context import UserSessionContext
from database import init_db

# Load environment variables
load_dotenv()


class HealthCoachCLI:
    """Command-line interface for the health coaching system."""
    
    def __init__(self):
        self.wellness_agent = WellnessAgent()
        self.nutrition_agent = NutritionAgent()
        self.fitness_agent = FitnessAgent()
        self.current_user_id = None
        self.context = None
        
    async def initialize(self):
        """Initialize the CLI system."""
        print("🏥 Health & Wellness Coach - CLI Version")
        print("=" * 50)
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key to use the AI coaches")
            return False
            
        # Initialize database
        print("📊 Initializing database...")
        if init_db():
            print("✅ Database ready")
        else:
            print("⚠️  Database initialization failed, continuing without persistence")
            
        return True
        
    def display_menu(self):
        """Display the main CLI menu."""
        print("\n🎯 Available Coaches:")
        print("1. 🌟 Wellness Coach - General health guidance")
        print("2. 🥗 Nutrition Coach - Diet and meal planning") 
        print("3. 💪 Fitness Coach - Workout recommendations")
        print("4. 📈 View Progress")
        print("5. ⚙️  Settings")
        print("6. 🚪 Exit")
        print("-" * 30)
        
    async def chat_with_agent(self, agent, agent_name: str):
        """Start a chat session with a specific agent."""
        print(f"\n💬 Chatting with {agent_name}")
        print("Type 'back' to return to main menu, 'quit' to exit")
        print("-" * 40)
        while True:
            try:
                user_input = input(f"\nYou: ").strip()
                
                if user_input.lower() in ['back', 'menu']:
                    break
                elif user_input.lower() in ['quit', 'exit']:
                    return False
                elif not user_input:
                    continue
                    
                print(f"\n{agent_name}: ", end="")
                
                # Stream the response
                response_chunks = []
                async for chunk in agent.process_message(user_input, self.context):
                    if chunk:
                        print(chunk, end="", flush=True)
                        response_chunks.append(chunk)
                        
                full_response = "".join(response_chunks)
                print()  # New line after response
                
                # Save conversation to database if context available
                if self.context and hasattr(self.context, 'user_id'):
                    from database import save_conversation
                    save_conversation(
                        self.context.user_id,
                        user_input,
                        full_response,
                        agent_name.lower().replace(" ", "_")
                    )
                    
            except KeyboardInterrupt:
                print("\n\n👋 Chat session ended")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
        return True
        
    def get_user_info(self):
        """Collect basic user information for context."""
        print("\n📋 Let's set up your profile:")
        
        name = input("Name (optional): ").strip() or "User"
        
        try:
            age = int(input("Age (optional, press enter to skip): ") or 0)
        except ValueError:
            age = 0
            
        goals = input("Health goals (optional): ").strip()
        
        # Create a simple user context
        user_id = f"cli_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_user_id = user_id
        self.context = UserSessionContext(user_id=user_id)
        self.context.personal_info = {
            "name": name,
            "age": age,
            "goals": goals
        }
        
        print(f"✅ Profile created for {name}")
        
    async def view_progress(self):
        """Display user progress if available."""
        if not self.context:
            print("❌ No user context available. Please chat with a coach first.")
            return
            
        print("\n📈 Progress Overview")
        print("-" * 30)
        
        # Try to fetch from database
        try:
            from database import get_user_progress, get_user_goals
            
            goals = get_user_goals(self.current_user_id)
            progress = get_user_progress(self.current_user_id, days=7)
            
            if goals:
                print("🎯 Current Goals:")
                for goal in goals[:3]:  # Show top 3 goals
                    print(f"  • {goal['title']}: {goal['status']}")
            else:
                print("🎯 No goals set yet")
                
            if progress:
                print(f"\n📊 Recent Progress ({len(progress)} entries):")
                for entry in progress[:5]:  # Show last 5 entries
                    print(f"  • {entry['category']}: {entry['value']} {entry['unit']} ({entry['date']})")
            else:
                print("📊 No progress recorded yet")
                
        except Exception as e:
            print(f"⚠️  Could not load progress: {e}")
            print("💡 Chat with coaches to start tracking your progress")
            
    def settings(self):
        """Display and manage CLI settings."""
        print("\n⚙️  Settings")
        print("-" * 20)
        print(f"🆔 User ID: {self.current_user_id or 'Not set'}")
        print(f"🔑 API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
        print(f"🗄️  Database: {'✅ Connected' if os.getenv('DATABASE_URL') else '⚠️  Using fallback'}")
        
        print("\nOptions:")
        print("1. Reset user profile")
        print("2. Test API connection")
        print("3. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self.get_user_info()
        elif choice == "2":
            self.test_api_connection()
        # Option 3 or any other input goes back to main menu
            
    def test_api_connection(self):
        """Test the OpenAI API connection."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            print("✅ API connection successful!")
            
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            
    async def run(self):
        """Main CLI loop."""
        if not await self.initialize():
            return
            
        self.get_user_info()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Select option (1-6): ").strip()
                
                if choice == "1":
                    if not await self.chat_with_agent(self.wellness_agent, "Wellness Coach"):
                        break
                elif choice == "2":
                    if not await self.chat_with_agent(self.nutrition_agent, "Nutrition Coach"):
                        break
                elif choice == "3":
                    if not await self.chat_with_agent(self.fitness_agent, "Fitness Coach"):
                        break
                elif choice == "4":
                    await self.view_progress()
                elif choice == "5":
                    self.settings()
                elif choice == "6":
                    print("👋 Thank you for using Health & Wellness Coach!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                

async def main():
    """Entry point for the CLI application."""
    cli = HealthCoachCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)