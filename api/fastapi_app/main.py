# fastapi_app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.wellness_agent import WellnessAgent
from context import UserSessionContext


app = FastAPI(title="Health & Wellness Planner API")

agent = WellnessAgent()

class GeneratePlanRequest(BaseModel):
    user_id: str
    goal_description: str

@app.post("/generate-plan")
async def generate_plan(req: GeneratePlanRequest):
    try:
        context = UserSessionContext(user_id=req.user_id)
        result = await agent.generate_wellness_plan(
            user_input=req.goal_description,
            context=context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
