# cli.py
import os
import sys
import asyncio
from typing import Dict
from dotenv import load_dotenv


from context import UserSessionContext
from agents.base import BaseAgent
from agents.wellness_agent import WellnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.fitness_agent import FitnessAgent
from agents.injury_support_agent import InjurySupportAgent
from agents.mental_health_agent import MentalHealthAgent
from agents.human_coach_agent import HumanCoachAgent
from agents.progress_agent import ProgressAgent


# --- Environment Setup ---
load_dotenv()
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY not found in .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
except (ImportError, ValueError) as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


# ==============================================================================
# 🤖 THE ORCHESTRATOR - System ka Dimagh
# ==============================================================================
class CLIAgentOrchestrator:
    """Yeh orchestrator aapke sabhi specialized agents ko manage karta hai."""
    
    def __init__(self, context: UserSessionContext):
        self.context = context
        # --- Apne sabhi agents yahan register karein ---
        self.agents: Dict[str, BaseAgent] = {
            "wellness": WellnessAgent(),
            "nutrition": NutritionAgent(),
            "fitness": FitnessAgent(),
            "injury_support": InjurySupportAgent(),
            "mental_health": MentalHealthAgent(),
            "human_coach": HumanCoachAgent(),
            "progress": ProgressAgent(),
        }
        self.current_agent_name = self.context.current_agent

    async def determine_agent_and_process(self, user_input: str):
        """Sahi agent ka intekhab karta hai aur message process karta hai."""
        
        # NOTE: Behtareen tareeka yeh hai ke aapka 'WellnessAgent' handoff ka faisla le.
        # Hum yahan uske 'should_handoff' method ko istemal karenge.
        wellness_agent = self.agents['wellness']
        target_agent_name = await wellness_agent.should_handoff(user_input) or self.current_agent_name
        
        # Agar koi specific agent match nahi hota, to wellness agent hi rahega
        if not target_agent_name or target_agent_name not in self.agents:
            target_agent_name = "wellness"

        if self.current_agent_name != target_agent_name:
            self.context.log_handoff(self.current_agent_name, target_agent_name, f"User query matched '{target_agent_name}' keywords.")
            print(f"\n🔄 [Handoff]: Switching to {target_agent_name.replace('_', ' ').title()} Agent...")
            self.current_agent_name = target_agent_name
        
        current_agent = self.agents[self.current_agent_name]

        # Agent se Jawab Stream Karein
        print(f"🤖 [{current_agent.name}]: ", end="", flush=True)
        full_response = ""
        try:
            async for chunk in current_agent.process_message(user_input):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
        except Exception as e:
            print(f"\n❌ Agent Error in {current_agent.name}: {e}")
        
        # Context update karein
        self.context.add_message(role='user', content=user_input)
        self.context.add_message(role='assistant', content=full_response, agent_type=self.current_agent_name)


# ==============================================================================
# 🚀 Main Application Loop
# ==============================================================================
async def main():
    print("="*60, "\n🌿 Enterprise-Level CLI Wellness Agent 🌿\n", "="*60, sep="")
    
    name = input("👋 What's your name? ").strip() or "User"
    # ... Aap yahan poora profile input le sakte hain ...
    
    context = UserSessionContext(name=name, age=30, height=170, weight=70) # Pydantic model
    orchestrator = CLIAgentOrchestrator(context)
    
    # Wellness agent se personalized welcome message lein
    welcome_msg = orchestrator.agents['wellness'].get_welcome_message()
    print(f"\n{welcome_msg}")

    while True:
        try:
            user_input = input("🧑 You: ").strip()
            if user_input.lower() in ['quit', 'exit']: break
            if not user_input: continue
            
            await orchestrator.determine_agent_and_process(user_input)
        except (KeyboardInterrupt, EOFError):
            break
    print("\nGoodbye! Stay healthy!")

if __name__ == "__main__":
    asyncio.run(main())