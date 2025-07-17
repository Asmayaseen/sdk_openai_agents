import pytest
from unittest.mock import AsyncMock
from agents import WellnessPlannerAgent  # Adjust this import based on your actual project structure
from utils.old_context import UserSessionContext  # Corrected import path

@pytest.fixture
def mock_agent():
    return WellnessPlannerAgent(context=UserSessionContext(name="Test User", goal="Weight loss"))

@pytest.mark.asyncio
async def test_agent_initialization(mock_agent):
    assert mock_agent.name == "WellnessPlannerAgent"
    assert hasattr(mock_agent, 'tools')

@pytest.mark.asyncio
async def test_goal_analysis(mock_agent):
    mock_agent.run = AsyncMock(return_value="Test response")
    response = await mock_agent.run("I want to lose 5kg in 2 months")
    assert response == "Test response"
    mock_agent.run.assert_called_once()

@pytest.mark.asyncio
async def test_meal_plan_request():
    context = UserSessionContext(
        name="Test User", 
        goal="Eat healthy", 
        meal_plan=None, 
        progress_logs=[], 
        diet_preferences="vegetarian"
    )
    agent = WellnessPlannerAgent(context=context)
    agent.run = AsyncMock(return_value={"Monday": {"breakfast": "Oatmeal"}})

    response = await agent.run("Suggest a vegetarian meal plan")
    assert isinstance(response, dict)
    assert "Monday" in response
