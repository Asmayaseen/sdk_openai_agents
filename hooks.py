"""
Lifecycle Hooks for Health & Wellness Planner Agent
Provides comprehensive logging, analytics, performance monitoring, and user insights
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class HookEvent:
    """Represents a single hook event"""
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[int] = None

@dataclass
class SessionMetrics:
    """Session performance metrics"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_interactions: int = 0
    tool_usage_count: Dict[str, int] = None
    handoff_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    user_satisfaction_score: Optional[float] = None
    
    def __post_init__(self):
        if self.tool_usage_count is None:
            self.tool_usage_count = {}

@dataclass
class InteractionLog:
    """Individual interaction log entry"""
    timestamp: datetime
    user_input: str
    agent_response: str
    tool_used: Optional[str]
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None

class HealthWellnessHooks:
    """
    Comprehensive lifecycle hooks for the Health & Wellness Planner Agent
    Provides logging, analytics, performance monitoring, and user insights
    """
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Session tracking
        self.current_session: Optional[SessionMetrics] = None
        self.interaction_logs: List[InteractionLog] = []
        
        # Performance tracking
        self.response_times: List[float] = []
        self.tool_performance: Dict[str, List[float]] = {}
        
        # Analytics
        self.user_patterns: Dict[str, Any] = {}
        self.popular_tools: Dict[str, int] = {}
        self.common_errors: Dict[str, int] = {}
        
        # Initialize logging
        self._setup_logging()
    
    def on_session_start(self, user_context: Any) -> None:
        """Called when a new user session starts"""
        session_id = f"session_{user_context.uid}_{int(time.time())}"
        
        self.current_session = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self._log_event("session_start", {
            "session_id": session_id,
            "user_id": user_context.uid,
            "user_name": user_context.name,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"🔍 [DEBUG] Session started: {session_id}")
    
    def on_session_end(self, user_context: Any) -> None:
        """Called when a user session ends"""
        if not self.current_session:
            return
        
        self.current_session.end_time = datetime.now()
        
        # Calculate session metrics
        session_duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
        
        if self.response_times:
            self.current_session.average_response_time = sum(self.response_times) / len(self.response_times)
        
        # Log session summary
        session_summary = {
            "session_id": self.current_session.session_id,
            "duration_seconds": session_duration,
            "total_interactions": self.current_session.total_interactions,
            "tool_usage": self.current_session.tool_usage_count,
            "handoff_count": self.current_session.handoff_count,
            "error_count": self.current_session.error_count,
            "average_response_time_ms": self.current_session.average_response_time,
            "user_satisfaction": self.current_session.user_satisfaction_score
        }
        
        self._log_event("session_end", session_summary)
        self._save_session_analytics(session_summary)
        
        print(f"🔍 [DEBUG] Session ended: {self.current_session.session_id}")
        print(f"📊 Session Summary: {session_duration:.1f}s, {self.current_session.total_interactions} interactions")
    
    def on_user_input(self, user_input: str, user_context: Any) -> None:
        """Called when user provides input"""
        self._log_event("user_input", {
            "user_id": user_context.uid,
            "input_length": len(user_input),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        # Analyze user patterns
        self._analyze_user_patterns(user_input, user_context)
        
        print(f"🔍 [DEBUG] User input received: {len(user_input)} characters")
    
    def on_tool_start(self, tool_name: str, user_context: Any) -> Dict[str, Any]:
        """Called when a tool starts execution"""
        start_time = time.time()
        
        self._log_event("tool_start", {
            "tool_name": tool_name,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        # Track tool usage
        if self.current_session:
            if tool_name not in self.current_session.tool_usage_count:
                self.current_session.tool_usage_count[tool_name] = 0
            self.current_session.tool_usage_count[tool_name] += 1
        
        # Track popular tools
        if tool_name not in self.popular_tools:
            self.popular_tools[tool_name] = 0
        self.popular_tools[tool_name] += 1
        
        print(f"🔍 [DEBUG] Tool started: {tool_name}")
        
        return {"start_time": start_time}
    
    def on_tool_end(self, tool_name: str, result: Any, context: Dict[str, Any], user_context: Any) -> None:
        """Called when a tool completes execution"""
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Track tool performance
        if tool_name not in self.tool_performance:
            self.tool_performance[tool_name] = []
        self.tool_performance[tool_name].append(execution_time)
        
        success = isinstance(result, dict) and result.get('success', True)
        
        self._log_event("tool_end", {
            "tool_name": tool_name,
            "execution_time_ms": execution_time,
            "success": success,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        print(f"🔍 [DEBUG] Tool completed: {tool_name} ({execution_time:.1f}ms)")
    
    def on_tool_error(self, tool_name: str, error: Exception, user_context: Any) -> None:
        """Called when a tool encounters an error"""
        error_message = str(error)
        
        # Track errors
        if self.current_session:
            self.current_session.error_count += 1
        
        if error_message not in self.common_errors:
            self.common_errors[error_message] = 0
        self.common_errors[error_message] += 1
        
        self._log_event("tool_error", {
            "tool_name": tool_name,
            "error_message": error_message,
            "error_type": type(error).__name__,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        print(f"🔍 [DEBUG] Tool error: {tool_name} - {error_message}")
    
    def on_handoff(self, from_agent: str, to_agent: str, reason: str, user_context: Any) -> None:
        """Called when agent handoff occurs"""
        if self.current_session:
            self.current_session.handoff_count += 1
        
        self._log_event("agent_handoff", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        print(f"🔍 [DEBUG] Agent handoff: {from_agent} → {to_agent} ({reason})")
    
    def on_response_generated(self, response: str, user_context: Any, response_time_ms: float) -> None:
        """Called when agent generates a response"""
        if self.current_session:
            self.current_session.total_interactions += 1
        
        self.response_times.append(response_time_ms)
        
        self._log_event("response_generated", {
            "response_length": len(response),
            "response_time_ms": response_time_ms,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        print(f"🔍 [DEBUG] Response generated: {len(response)} characters ({response_time_ms:.1f}ms)")
    
    def on_error(self, error: Exception, context: Dict[str, Any], user_context: Any) -> None:
        """Called when a general error occurs"""
        error_message = str(error)
        
        if self.current_session:
            self.current_session.error_count += 1
        
        self._log_event("general_error", {
            "error_message": error_message,
            "error_type": type(error).__name__,
            "context": context,
            "user_id": user_context.uid,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None
        })
        
        print(f"🔍 [DEBUG] General error: {error_message}")
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get current session analytics"""
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "duration_minutes": (datetime.now() - self.current_session.start_time).total_seconds() / 60,
            "interactions": self.current_session.total_interactions,
            "tools_used": self.current_session.tool_usage_count,
            "handoffs": self.current_session.handoff_count,
            "errors": self.current_session.error_count,
            "avg_response_time": self.current_session.average_response_time
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics"""
        return {
            "popular_tools": dict(sorted(self.popular_tools.items(), key=lambda x: x[1], reverse=True)),
            "tool_performance": {
                tool: {
                    "avg_time_ms": sum(times) / len(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "usage_count": len(times)
                }
                for tool, times in self.tool_performance.items()
            },
            "common_errors": dict(sorted(self.common_errors.items(), key=lambda x: x[1], reverse=True)[:5]),
            "overall_avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0
        }
    
    def get_user_insights(self) -> Dict[str, Any]:
        """Get user behavior insights"""
        return {
            "user_patterns": self.user_patterns,
            "interaction_trends": self._analyze_interaction_trends(),
            "tool_preferences": self._analyze_tool_preferences(),
            "session_patterns": self._analyze_session_patterns()
        }
    
    def _setup_logging(self) -> None:
        """Setup logging infrastructure"""
        # Create log files
        self.event_log_file = self.log_directory / "events.jsonl"
        self.analytics_log_file = self.log_directory / "analytics.json"
        self.performance_log_file = self.log_directory / "performance.json"
        
        print(f"🔍 [DEBUG] Logging initialized: {self.log_directory}")
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the event log file"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            with open(self.event_log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"🔍 [DEBUG] Logging error: {e}")
    
    def _save_session_analytics(self, session_data: Dict[str, Any]) -> None:
        """Save session analytics to file"""
        try:
            # Load existing analytics
            analytics_data = []
            if self.analytics_log_file.exists():
                with open(self.analytics_log_file, "r") as f:
                    analytics_data = json.load(f)
            
            # Add new session data
            analytics_data.append(session_data)
            
            # Save updated analytics
            with open(self.analytics_log_file, "w") as f:
                json.dump(analytics_data, f, indent=2)
                
        except Exception as e:
            print(f"🔍 [DEBUG] Analytics save error: {e}")
    
    def _analyze_user_patterns(self, user_input: str, user_context: Any) -> None:
        """Analyze user input patterns"""
        user_id = str(user_context.uid)
        
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                "total_inputs": 0,
                "avg_input_length": 0,
                "common_keywords": {},
                "interaction_times": []
            }
        
        patterns = self.user_patterns[user_id]
        patterns["total_inputs"] += 1
        patterns["interaction_times"].append(datetime.now().isoformat())
        
        # Update average input length
        current_avg = patterns["avg_input_length"]
        patterns["avg_input_length"] = (current_avg * (patterns["total_inputs"] - 1) + len(user_input)) / patterns["total_inputs"]
        
        # Track keywords
        keywords = user_input.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:  # Only track meaningful words
                if keyword not in patterns["common_keywords"]:
                    patterns["common_keywords"][keyword] = 0
                patterns["common_keywords"][keyword] += 1
    
    def _analyze_interaction_trends(self) -> Dict[str, Any]:
        """Analyze interaction trends"""
        return {
            "total_interactions": len(self.interaction_logs),
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "peak_usage_hours": self._get_peak_usage_hours(),
            "interaction_success_rate": self._calculate_success_rate()
        }
    
    def _analyze_tool_preferences(self) -> Dict[str, Any]:
        """Analyze tool usage preferences"""
        total_usage = sum(self.popular_tools.values())
        
        return {
            "most_popular": max(self.popular_tools.items(), key=lambda x: x[1]) if self.popular_tools else None,
            "usage_distribution": {
                tool: (count / total_usage) * 100
                for tool, count in self.popular_tools.items()
            } if total_usage > 0 else {},
            "tool_efficiency": {
                tool: sum(times) / len(times)
                for tool, times in self.tool_performance.items()
            }
        }
    
    def _analyze_session_patterns(self) -> Dict[str, Any]:
        """Analyze session patterns"""
        return {
            "current_session_duration": (datetime.now() - self.current_session.start_time).total_seconds() / 60 if self.current_session else 0,
            "interactions_per_session": self.current_session.total_interactions if self.current_session else 0,
            "handoff_rate": self.current_session.handoff_count / max(1, self.current_session.total_interactions) if self.current_session else 0,
            "error_rate": self.current_session.error_count / max(1, self.current_session.total_interactions) if self.current_session else 0
        }
    
    def _get_peak_usage_hours(self) -> List[int]:
        """Get peak usage hours"""
        # Simplified implementation - would analyze actual usage patterns
        return [9, 10, 11, 14, 15, 16, 20, 21]  # Common peak hours
    
    def _calculate_success_rate(self) -> float:
        """Calculate interaction success rate"""
        if not self.interaction_logs:
            return 100.0
        
        successful = sum(1 for log in self.interaction_logs if log.success)
        return (successful / len(self.interaction_logs)) * 100
    
    def export_analytics(self, format: str = "json") -> str:
        """Export analytics data"""
        analytics = {
            "session_analytics": self.get_session_analytics(),
            "performance_metrics": self.get_performance_metrics(),
            "user_insights": self.get_user_insights(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        if format == "json":
            return json.dumps(analytics, indent=2)
        else:
            return str(analytics)
