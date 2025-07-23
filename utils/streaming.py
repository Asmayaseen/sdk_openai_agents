"""
Real-time Streaming Handler for Health & Wellness Planner Agent
Provides typewriter effect and real-time response streaming
"""
import asyncio
import time
import sys
from typing import Any, Optional, Callable

class StreamingHandler:
    """
    Handles real-time streaming of agent responses with typewriter effect
    Provides engaging user experience with progress indicators
    """
    
    def __init__(self, typing_speed: float = 0.03, chunk_size: int = 1):
        """
        Initialize streaming handler
        
        Args:
            typing_speed: Delay between characters (seconds)
            chunk_size: Number of characters to display at once
        """
        self.typing_speed = typing_speed
        self.chunk_size = chunk_size
        self.is_streaming = False
    
    async def stream_response(
        self, 
        agent: Any, 
        user_input: str, 
        context: Any, 
        hooks: Optional[Any] = None
    ) -> None:
        """
        Stream agent response with typewriter effect
        
        Args:
            agent: The health wellness agent
            user_input: User's input message
            context: User session context
            hooks: Optional lifecycle hooks for monitoring
        """
        try:
            self.is_streaming = True
            start_time = time.time()
            
            # Show thinking indicator
            await self._show_thinking_indicator()
            
            # Get response from agent
            if hooks:
                hooks.on_user_input(user_input, context)
            
            response = await agent.process_message(user_input, context)
            
            # Clear thinking indicator
            self._clear_line()
            print("🤖 Health Coach: ", end="", flush=True)
            
            # Stream the response
            await self._stream_text(response)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            
            if hooks:
                hooks.on_response_generated(response, context, response_time)
            
            print()  # New line after response
            
        except Exception as e:
            self._clear_line()
            print(f"🤖 Health Coach: I apologize, but I encountered an error processing your request. Please try again.")
            if hooks:
                hooks.on_error(e, {"context": "streaming"}, context)
        finally:
            self.is_streaming = False
    
    async def _show_thinking_indicator(self) -> None:
        """Show animated thinking indicator"""
        thinking_frames = ["🤔 Thinking", "🤔 Thinking.", "🤔 Thinking..", "🤔 Thinking..."]
        
        for _ in range(2):  # Show animation for 2 cycles
            for frame in thinking_frames:
                if not self.is_streaming:
                    break
                print(f"\r{frame}", end="", flush=True)
                await asyncio.sleep(0.3)
    
    async def _stream_text(self, text: str) -> None:
        """
        Stream text with typewriter effect
        
        Args:
            text: Text to stream
        """
        if not text:
            return
        
        # Handle special formatting
        formatted_text = self._format_for_streaming(text)
        
        i = 0
        while i < len(formatted_text):
            if not self.is_streaming:
                break
            
            # Get next chunk
            chunk = formatted_text[i:i + self.chunk_size]
            print(chunk, end="", flush=True)
            
            # Adjust delay based on character type
            delay = self._get_character_delay(chunk)
            await asyncio.sleep(delay)
            
            i += self.chunk_size
    
    def _format_for_streaming(self, text: str) -> str:
        """
        Format text for better streaming experience
        
        Args:
            text: Original text
            
        Returns:
            Formatted text
        """
        # Replace multiple newlines with single newlines for better flow
        formatted = text.replace('\n\n\n', '\n\n')
        
        # Add slight pauses after sentences
        formatted = formatted.replace('. ', '.  ')
        formatted = formatted.replace('! ', '!  ')
        formatted = formatted.replace('? ', '?  ')
        
        return formatted
    
    def _get_character_delay(self, chunk: str) -> float:
        """
        Get appropriate delay based on character type
        
        Args:
            chunk: Character chunk
            
        Returns:
            Delay in seconds
        """
        if not chunk:
            return self.typing_speed
        
        char = chunk[-1]  # Last character in chunk
        
        # Longer pauses for punctuation
        if char in '.!?':
            return self.typing_speed * 3
        elif char in ',;:':
            return self.typing_speed * 2
        elif char == '\n':
            return self.typing_speed * 2
        elif char == ' ':
            return self.typing_speed * 0.5
        else:
            return self.typing_speed
    
    def _clear_line(self) -> None:
        """Clear current line"""
        print('\r' + ' ' * 80 + '\r', end='', flush=True)
    
    async def stream_tool_execution(
        self, 
        tool_name: str, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Stream tool execution progress
        
        Args:
            tool_name: Name of the tool being executed
            progress_callback: Optional callback for progress updates
        """
        try:
            self.is_streaming = True
            
            # Tool-specific progress messages
            progress_messages = self._get_tool_progress_messages(tool_name)
            
            for i, message in enumerate(progress_messages):
                if not self.is_streaming:
                    break
                
                print(f"\r🔄 {message}", end="", flush=True)
                
                if progress_callback:
                    progress_callback(message)
                
                # Simulate processing time
                await asyncio.sleep(0.8)
            
            # Clear progress line
            self._clear_line()
            
        except Exception as e:
            self._clear_line()
            print(f"⚠️ Tool execution interrupted: {str(e)}")
        finally:
            self.is_streaming = False
    
    def _get_tool_progress_messages(self, tool_name: str) -> list:
        """
        Get progress messages for specific tools
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of progress messages
        """
        progress_map = {
            'goal_analyzer': [
                "Analyzing your goals...",
                "Structuring your objectives...",
                "Creating action plan..."
            ],
            'meal_planner': [
                "Calculating nutritional needs...",
                "Selecting appropriate foods...",
                "Creating 7-day meal plan...",
                "Generating shopping list..."
            ],
            'workout_recommender': [
                "Assessing fitness level...",
                "Designing workout routine...",
                "Optimizing exercise selection...",
                "Creating schedule..."
            ],
            'progress_tracker': [
                "Analyzing progress data...",
                "Calculating trends...",
                "Generating insights..."
            ],
            'scheduler': [
                "Checking availability...",
                "Scheduling check-ins...",
                "Setting reminders..."
            ]
        }
        
        return progress_map.get(tool_name, [
            "Processing your request...",
            "Analyzing data...",
            "Generating response..."
        ])
    
    async def stream_handoff_transition(self, from_agent: str, to_agent: str, reason: str) -> None:
        """
        Stream agent handoff transition
        
        Args:
            from_agent: Source agent
            to_agent: Target agent
            reason: Reason for handoff
        """
        try:
            self.is_streaming = True
            
            transition_messages = [
                f"Connecting you to {to_agent.replace('_', ' ').title()}...",
                f"Transferring context and conversation history...",
                f"Specialized support is now available..."
            ]
            
            for message in transition_messages:
                if not self.is_streaming:
                    break
                
                print(f"\r🔄 {message}", end="", flush=True)
                await asyncio.sleep(1.0)
            
            self._clear_line()
            print(f"✅ Connected to {to_agent.replace('_', ' ').title()}")
            print(f"📋 Reason: {reason}")
            print()
            
        except Exception as e:
            self._clear_line()
            print(f"⚠️ Handoff interrupted: {str(e)}")
        finally:
            self.is_streaming = False
    
    def stop_streaming(self) -> None:
        """Stop current streaming operation"""
        self.is_streaming = False
    
    def set_typing_speed(self, speed: float) -> None:
        """
        Set typing speed
        
        Args:
            speed: Delay between characters in seconds
        """
        self.typing_speed = max(0.01, min(0.1, speed))  # Clamp between 0.01 and 0.1
    
    def set_chunk_size(self, size: int) -> None:
        """
        Set chunk size for streaming
        
        Args:
            size: Number of characters per chunk
        """
        self.chunk_size = max(1, min(5, size))  # Clamp between 1 and 5
    
    async def stream_with_progress_bar(self, text: str, total_steps: int = 100) -> None:
        """
        Stream text with progress bar
        
        Args:
            text: Text to stream
            total_steps: Total steps for progress bar
        """
        try:
            self.is_streaming = True
            text_length = len(text)
            
            for i, char in enumerate(text):
                if not self.is_streaming:
                    break
                
                # Calculate progress
                progress = int((i / text_length) * total_steps)
                progress_bar = "█" * (progress // 5) + "░" * ((total_steps - progress) // 5)
                
                # Display character with progress
                print(f"\r{char}", end="", flush=True)
                print(f" [{progress_bar}] {progress}%", end="", flush=True)
                
                await asyncio.sleep(self.typing_speed)
            
            print()  # New line after completion
            
        except Exception as e:
            self._clear_line()
            print(f"⚠️ Streaming with progress interrupted: {str(e)}")
        finally:
            self.is_streaming = False
