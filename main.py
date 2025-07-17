#!/usr/bin/env python3

import asyncio
from planner import WellnessPlanner
from context import UserSessionContext
from datetime import datetime
import argparse

# Optional: PostgreSQL session logging
try:
    from database.session import SessionLocal
    from database.models import SessionLog
    db_enabled = True
except ImportError:
    db_enabled = False

def parse_args():
    parser = argparse.ArgumentParser(description="🧘‍♀️ Health & Wellness Planner CLI")
    parser.add_argument("--user_id", type=str, default="anonymous", help="Unique user ID")
    return parser.parse_args()

async def main():
    """Entry point with example conversation flow"""
    args = parse_args()

    print("\n=== 🧘‍♀️ Health & Wellness Planner ===")
    print("Type your message (type 'exit' or 'quit' to stop)\n")

    planner = WellnessPlanner()
    context: UserSessionContext = None
    start_time = datetime.utcnow()

    try:
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break

            context = await planner.run_conversation(
                messages=[user_input],
                context=context,
                streaming=True
            )

    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user.")

    finally:
        if context:
            print("\n=== 🧾 Session Summary ===")
            duration = context.get_duration()
            print(f"🕒 Duration: {duration:.2f} seconds")
            print(f"🧠 Final Agent: {context.current_agent.value}")
            print(f"💬 Total Messages: {len(context.conversation_history)}")

            if context.handoff_log:
                print("🔄 Handoffs:")
                for handoff in context.handoff_log:
                    print(f"  ➜ {handoff['from']} → {handoff['to']} (reason: {handoff['reason']})")
            else:
                print("✅ No agent handoffs detected.")

            # ✅ Save to PostgreSQL if enabled
            if db_enabled:
                try:
                    db = SessionLocal()
                    session_log = SessionLog(
                        uid=args.user_id,
                        start_time=start_time,
                        duration=int(duration),
                        conversation=context.conversation_history,
                        final_agent=context.current_agent.value,
                        handoffs=context.handoff_log,
                    )
                    db.add(session_log)
                    db.commit()
                    print("📦 Session saved to database.")
                except Exception as e:
                    print(f"❌ Failed to save session to DB: {e}")
                finally:
                    db.close()

        print("\n👋 Thank you for using the Health & Wellness Planner!")

if __name__ == "__main__":
    asyncio.run(main())
