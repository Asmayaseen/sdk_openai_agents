#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

def get_pg_connection():
    """Load environment and return PostgreSQL connection"""
    try:
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set in .env file.")
            return None
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def create_tables():
    """Create necessary tables in PostgreSQL"""
    conn = get_pg_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            # ------------------ USERS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    age INTEGER,
                    gender VARCHAR(10),
                    height FLOAT,
                    weight FLOAT,
                    activity_level VARCHAR(50),
                    fitness_goal VARCHAR(100),
                    medical_conditions TEXT,
                    dietary_restrictions TEXT,
                    emergency_contact VARCHAR(200),
                    preferred_language VARCHAR(20) DEFAULT 'English',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );
            """)

            # ------------------ GOALS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    target_value FLOAT,
                    current_value FLOAT DEFAULT 0,
                    target_date DATE,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # ------------------ CONVERSATIONS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    agent_type VARCHAR(50) DEFAULT 'health_coach',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # ------------------ PROGRESS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    category VARCHAR(50) NOT NULL,
                    value FLOAT,
                    unit VARCHAR(20),
                    notes TEXT,
                    data JSONB,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # ------------------ MEAL PLANS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    plan_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # ------------------ WORKOUTS ------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    workout_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # ------------------ INDEXES ------------------
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_time 
                ON conversations(user_id, timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_goals_user_created 
                ON goals(user_id, created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_progress_user_date 
                ON progress(user_id, date DESC)
            """)

            conn.commit()
            print("✅ PostgreSQL tables created successfully!")

    except Exception as e:
        print(f"❌ Error during table creation: {e}")
    finally:
        conn.close()
        print("🔒 Database connection closed.")

if __name__ == "__main__":
    create_tables()
    input("\nPress Enter to exit...")
