# Health & Wellness AI Coach

## Overview

This is a comprehensive AI-powered health and wellness coaching application built with Streamlit and OpenAI's GPT-4o model. The system features multiple specialized AI agents that work together to provide personalized fitness, nutrition, and wellness guidance through natural language conversations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular, agent-based architecture where specialized AI agents handle different aspects of health and wellness coaching. The system is built around a central orchestrator that routes conversations to appropriate agents based on user needs and context.

### Core Components:
- **Agent Orchestrator**: Central system that manages conversation flow between specialized agents
- **Specialized Agents**: Domain-specific AI agents for wellness, nutrition, fitness, and progress tracking
- **Tools**: Reusable components for meal planning, workout recommendations, and progress tracking
- **Context Management**: Persistent user session state management
- **Database Layer**: SQLite/PostgreSQL support for data persistence
- **UI Layer**: Streamlit-based interactive web interface

## Key Components

### Agent System
The application uses four specialized AI agents:

1. **WellnessAgent**: Primary coach for general health guidance and motivation
   - Handles general wellness questions and provides holistic health advice
   - Determines when to hand off to specialist agents
   - Acts as the entry point for most conversations

2. **NutritionAgent**: Certified nutritionist for meal planning and dietary guidance
   - Creates personalized meal plans based on dietary preferences and restrictions
   - Provides nutritional analysis and food recommendations
   - Handles calorie calculations and macro tracking

3. **FitnessAgent**: Personal trainer for workout planning and exercise guidance
   - Generates customized workout plans based on fitness level and goals
   - Provides exercise form guidance and injury prevention strategies
   - Adapts exercises for different equipment availability

4. **ProgressAgent**: Analytics specialist for progress tracking and goal monitoring
   - Analyzes user progress data and identifies trends
   - Provides motivational feedback on achievements
   - Suggests goal adjustments when needed

### Tools
Three main tools support the agent functionality:

1. **MealPlannerTool**: Generates structured meal plans with nutritional information
2. **WorkoutRecommenderTool**: Creates exercise routines with injury modifications
3. **ProgressTrackerTool**: Validates and stores user progress metrics

### Context Management
The `UserSessionContext` class maintains comprehensive user state including:
- Personal information (name, age, goals)
- Health metrics and progress tracking
- Dietary preferences and restrictions
- Conversation history
- Agent handoff logs

## Data Flow

1. **User Input**: User messages are received through the Streamlit interface
2. **Agent Selection**: The orchestrator determines the appropriate agent based on message content
3. **Context Injection**: User session context is provided to the selected agent
4. **AI Processing**: The agent processes the message using OpenAI's GPT-4o model with specialized prompts
5. **Tool Execution**: Agents may call tools for structured operations (meal planning, workout generation, etc.)
6. **Response Generation**: Streaming responses are generated and displayed in real-time
7. **State Updates**: User context and conversation history are updated
8. **Handoff Logic**: Agents may hand off conversations to specialists when needed

## External Dependencies

### Core Technologies:
- **Streamlit**: Web application framework for the user interface
- **OpenAI API**: GPT-4o model for natural language processing and generation
- **SQLAlchemy**: Database ORM with SQLite/PostgreSQL support
- **Pydantic**: Data validation and serialization

### Optional Dependencies:
- **WeasyPrint**: HTML to PDF conversion for report generation (fallback to FPDF)
- **Plotly**: Interactive charts for progress visualization
- **PostgreSQL**: Production database (SQLite for development)

### Environment Variables:
- `OPENAI_API_KEY`: Required for AI functionality
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `DEBUG`: Enable debug logging

## Deployment Strategy

The application is designed to run on Replit with the following deployment considerations:

### Development Setup:
- SQLite database for local development
- File-based configuration management
- Streamlit development server

### Production Considerations:
- PostgreSQL database for scalability
- Environment variable configuration
- Session state management for multi-user support
- PDF report generation with proper file handling

### Scaling Strategy:
- The agent-based architecture allows for easy addition of new specialized agents
- Database schema supports multi-user scenarios
- Stateless design enables horizontal scaling
- Tool system allows for integration with external APIs and services

### Security Features:
- Input validation through Pydantic models
- SQL injection protection through ORM
- Content filtering through agent prompts
- Medical disclaimer and professional consultation recommendations

The system prioritizes user safety by always recommending professional medical consultation for serious health concerns and maintaining clear boundaries around medical advice.