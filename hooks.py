from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from .context import UserSessionContext
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base hook classes
class BaseHooks(ABC):
    """Abstract base class for all hook implementations"""
    
    @abstractmethod
    async def on_agent_start(self, agent_name: str, input: str, context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_agent_end(self, agent_name: str, output: str, context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_tool_start(self, tool_name: str, input: Dict[str, Any], context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_tool_end(self, tool_name: str, output: Dict[str, Any], context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_handoff(self, from_agent: str, to_agent: str, context: Optional[UserSessionContext] = None):
        pass

class AgentSpecificHooks(ABC):
    """Abstract base class for agent-specific hooks"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    @abstractmethod
    async def on_start(self, input: str, context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_end(self, output: str, context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_tool_start(self, tool_name: str, input: Dict[str, Any], context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_tool_end(self, tool_name: str, output: Dict[str, Any], context: Optional[UserSessionContext] = None):
        pass
    
    @abstractmethod
    async def on_handoff(self, to_agent: str, context: Optional[UserSessionContext] = None):
        pass

# Concrete implementations
class LoggingHooks(BaseHooks):
    """Global lifecycle hooks for logging and tracking system-wide events"""
    
    async def on_agent_start(self, agent_name: str, input: str, context: Optional[UserSessionContext] = None):
        """Log when any agent starts processing"""
        log_msg = f"Agent '{agent_name}' started with input: '{input[:50]}...'"  # Truncate long inputs
        logger.info(log_msg)
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "agent_start",
                "agent": agent_name,
                "details": log_msg
            })
    
    async def on_agent_end(self, agent_name: str, output: str, context: Optional[UserSessionContext] = None):
        """Log when any agent completes processing"""
        log_msg = f"Agent '{agent_name}' completed with output length: {len(output)}"
        logger.info(log_msg)
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "agent_end",
                "agent": agent_name,
                "details": log_msg
            })
    
    async def on_tool_start(self, tool_name: str, input: Dict[str, Any], context: Optional[UserSessionContext] = None):
        """Log when any tool starts execution"""
        logger.info(f"Tool '{tool_name}' invoked with input: {str(input)[:100]}...")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "tool_start",
                "tool": tool_name,
                "input": str(input)[:200]  # Truncate large inputs
            })
    
    async def on_tool_end(self, tool_name: str, output: Dict[str, Any], context: Optional[UserSessionContext] = None):
        """Log when any tool completes execution"""
        logger.info(f"Tool '{tool_name}' completed with output length: {len(str(output))}")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "tool_end",
                "tool": tool_name,
                "output_size": len(str(output))
            })
    
    async def on_handoff(self, from_agent: str, to_agent: str, context: Optional[UserSessionContext] = None):
        """Log and track agent handoffs"""
        handoff_msg = f"Handoff from '{from_agent}' to '{to_agent}'"
        logger.info(handoff_msg)
        if context:
            context.handoff_logs.append({
                "timestamp": datetime.now().isoformat(),
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context_snapshot": {
                    "goal": context.goal,
                    "diet_preferences": context.diet_preferences,
                    "injury_notes": context.injury_notes
                }
            })
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "handoff",
                "details": handoff_msg
            })

class HealthAgentHooks(AgentSpecificHooks):
    """Agent-specific hooks for the Health & Wellness Planner"""
    
    def __init__(self, agent_name: str):
        super().__init__(agent_name)
    
    async def on_start(self, input: str, context: Optional[UserSessionContext] = None):
        """Agent-specific startup logic"""
        logger.info(f"{self.agent_name} starting with input: {input[:50]}...")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"{self.agent_name}_start",
                "input": input[:200]
            })
    
    async def on_end(self, output: str, context: Optional[UserSessionContext] = None):
        """Agent-specific cleanup logic"""
        logger.info(f"{self.agent_name} completed with output length: {len(output)}")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"{self.agent_name}_end",
                "output_size": len(output)
            })
    
    async def on_tool_start(self, tool_name: str, input: Dict[str, Any], context: Optional[UserSessionContext] = None):
        """Agent-specific tool start logic"""
        logger.info(f"{self.agent_name} using tool '{tool_name}'")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"{self.agent_name}_tool_start",
                "tool": tool_name
            })
    
    async def on_tool_end(self, tool_name: str, output: Dict[str, Any], context: Optional[UserSessionContext] = None):
        """Agent-specific tool end logic"""
        logger.info(f"{self.agent_name} completed tool '{tool_name}'")
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"{self.agent_name}_tool_end",
                "tool": tool_name,
                "output_valid": bool(output)  # Simple validation check
            })
    
    async def on_handoff(self, to_agent: str, context: Optional[UserSessionContext] = None):
        """Agent-specific handoff preparation"""
        handoff_msg = f"{self.agent_name} handing off to '{to_agent}'"
        logger.info(handoff_msg)
        if context:
            context.progress_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"{self.agent_name}_handoff",
                "to_agent": to_agent,
                "context_snapshot": {
                    "goal": context.goal,
                    "diet_preferences": context.diet_preferences
                }
            })