import streamlit as st
import psycopg2
import os
import json
from datetime import datetime, timedelta

# -------------------- DATABASE CONNECTION --------------------

def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            st.error("⚠️ DATABASE_URL not set in environment variables.")
            return None
        return psycopg2.connect(database_url)
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        return None

# -------------------- DATABASE INIT --------------------

def init_db():
    """Creates required PostgreSQL tables if not exist."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        with conn.cursor() as cursor:
            # USERS
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
                )
            """)

            # GOALS
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
                )
            """)

            # CONVERSATIONS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    agent_type VARCHAR(50) DEFAULT 'health_coach',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # PROGRESS
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
                )
            """)

            # MEAL PLANS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    plan_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # WORKOUTS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    workout_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # INDEXES
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_time ON conversations(user_id, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_goals_user_created ON goals(user_id, created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_progress_user_date ON progress(user_id, date DESC)")

        conn.commit()
        st.success("✅ Database initialized successfully.")
        return True

    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        return False

    finally:
        if 'conn' in locals() and conn:
            conn.close()

# -------------------- UTILITY FUNCTIONS --------------------

def safe_close(conn):
    if 'conn' in locals() and conn:
        conn.close()

# -------------------- CONVERSATIONS --------------------

def save_conversation(user_id, message, response, agent_type="health_coach"):
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO conversations (user_id, message, response, agent_type, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, message, response, agent_type, datetime.now()))
            conn.commit()
        return True

    except Exception as e:
        st.error(f"❌ Error saving conversation: {e}")
        return False
    finally:
        safe_close(conn)

def get_conversation_history(user_id, limit=50):
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT message, response, agent_type, timestamp 
                FROM conversations 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (user_id, limit))
            rows = cursor.fetchall()

        return [
            {
                'message': row[0],
                'response': row[1],
                'agent_type': row[2],
                'timestamp': row[3]
            }
            for row in rows
        ]

    except Exception as e:
        st.error(f"❌ Error fetching conversation history: {e}")
        return []
    finally:
        safe_close(conn)

# -------------------- GOALS --------------------

def save_goal(user_id, goal_data):
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO goals (user_id, title, description, category, target_value, target_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                goal_data.get('title', ''),
                goal_data.get('description', ''),
                goal_data.get('category', ''),
                goal_data.get('target_value', 0),
                goal_data.get('target_date'),
                'active'
            ))
            conn.commit()
        return True

    except Exception as e:
        st.error(f"❌ Error saving goal: {e}")
        return False
    finally:
        safe_close(conn)

def get_user_goals(user_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, category, target_value, current_value, target_date, status, created_at
                FROM goals 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()

        return [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'target_value': row[4],
                'current_value': row[5],
                'target_date': row[6],
                'status': row[7],
                'created_at': row[8]
            }
            for row in rows
        ]

    except Exception as e:
        st.error(f"❌ Error fetching goals: {e}")
        return []
    finally:
        safe_close(conn)

# -------------------- PROGRESS --------------------

def save_progress(user_id, progress_data):
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO progress (user_id, category, value, unit, notes, data, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                progress_data.get('category', ''),
                progress_data.get('value', 0),
                progress_data.get('unit', ''),
                progress_data.get('notes', ''),
                json.dumps(progress_data.get('data', {})),
                progress_data.get('date', datetime.now().date())
            ))
            conn.commit()
        return True

    except Exception as e:
        st.error(f"❌ Error saving progress: {e}")
        return False
    finally:
        safe_close(conn)

def get_user_progress(user_id, days=30):
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        start_date = datetime.now() - timedelta(days=days)

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, category, value, unit, notes, data, date, created_at
                FROM progress 
                WHERE user_id = %s AND date >= %s
                ORDER BY date DESC
            """, (user_id, start_date.date()))
            rows = cursor.fetchall()

        return [
            {
                'id': row[0],
                'category': row[1],
                'value': row[2],
                'unit': row[3],
                'notes': row[4],
                'data': json.loads(row[5]) if row[5] else {},
                'date': row[6],
                'created_at': row[7]
            }
            for row in rows
        ]

    except Exception as e:
        st.error(f"❌ Error fetching progress: {e}")
        return []
    finally:
        safe_close(conn)
