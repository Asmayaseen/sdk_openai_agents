# 🏥 Health & Wellness Planner

A comprehensive multi-agent health and wellness planning system with AI-powered coaching, meal planning, workout recommendations, and progress tracking built with Python, OpenAI, and PostgreSQL.

## ✨ Features

### 🤖 Multi-Agent System
- **Wellness Agent**: General health and wellness coaching
- **Nutrition Agent**: Specialized meal planning and dietary advice
- **Fitness Agent**: Personalized workout plans and exercise guidance
- **Escalation Agent**: Human coach scheduling and support

### 🎯 Core Functionality
- **User Authentication & Profile Management**: Secure user accounts with comprehensive health profiles
- **Goal Setting & Progress Tracking**: SMART goal creation with visual progress monitoring
- **Meal Planning**: Personalized meal plans based on dietary preferences and restrictions
- **Workout Recommendations**: Fitness plans adapted to user's activity level and goals
- **Progress Monitoring**: Multi-metric tracking with data visualization
- **Report Generation**: Comprehensive PDF and HTML health reports
- **Database Persistence**: PostgreSQL backend for secure data storage
- **API Endpoints**: RESTful API for external integrations

### 🖥️ Multiple Interfaces
- **Streamlit Web App**: Interactive web interface for end users
- **Command Line Interface**: Terminal-based interaction for power users
- **FastAPI Backend**: RESTful API for integrations and mobile apps
- **Chainlit Support**: Conversational AI interface (extensible)

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** with asyncio for concurrent processing
- **OpenAI API** for intelligent agent responses (GPT-4o)
- **PostgreSQL** with psycopg2 for robust data persistence
- **SQLAlchemy** for database ORM and migrations
- **Pydantic** for data validation and serialization
- **FastAPI** for REST API endpoints

### Frontend
- **Streamlit** for main web interface
- **Plotly** for interactive health data visualization
- **ReportLab** for PDF report generation
- **Bootstrap** CSS framework for responsive design

### Core Libraries
- **OpenAI Agents** framework for multi-agent orchestration
- **AsyncPG** for high-performance database connectivity
- **Rich** for enhanced console output
- **Pandas** for data analysis and manipulation

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/health-wellness-planner.git
cd health-wellness-planner
