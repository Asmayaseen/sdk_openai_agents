import sqlite3
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from contextlib import contextmanager

from context import UserSessionContext

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the wellness application."""
    
    def __init__(self, db_path: str = "wellness.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database with required tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT,
                        age INTEGER,
                        weight REAL,
                        height REAL,
                        activity_level TEXT,
                        goal_type TEXT,
                        goal_target REAL,
                        goal_unit TEXT,
                        goal_deadline TEXT,
                        dietary_preference TEXT,
                        food_allergies TEXT,
                        medical_conditions TEXT,
                        injury_notes TEXT,
                        theme TEXT DEFAULT 'light',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Progress tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        notes TEXT,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Meal plans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meal_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        plan_name TEXT,
                        plan_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Workout plans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS workout_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        plan_name TEXT,
                        plan_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Conversation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        agent_type TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Agent handoffs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS handoffs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        from_agent TEXT NOT NULL,
                        to_agent TEXT NOT NULL,
                        reason TEXT,
                        context_snapshot TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_user_context(self, context: UserSessionContext) -> bool:
        """Save or update user context in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data
                food_allergies_json = json.dumps(context.food_allergies)
                medical_conditions_json = json.dumps([mc.value for mc in context.medical_conditions])
                
                # Check if user exists
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (context.user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing user
                    cursor.execute('''
                        UPDATE users SET
                            name = ?, age = ?, weight = ?, height = ?, activity_level = ?,
                            goal_type = ?, goal_target = ?, goal_unit = ?, goal_deadline = ?,
                            dietary_preference = ?, food_allergies = ?, medical_conditions = ?,
                            injury_notes = ?, theme = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (
                        context.name, context.age, context.weight, context.height,
                        context.activity_level, context.goal_type.value if context.goal_type else None,
                        context.goal_target, context.goal_unit.value if context.goal_unit else None,
                        context.goal_deadline.isoformat() if context.goal_deadline else None,
                        context.dietary_preference.value, food_allergies_json,
                        medical_conditions_json, context.injury_notes, context.theme,
                        context.user_id
                    ))
                else:
                    # Insert new user
                    cursor.execute('''
                        INSERT INTO users (
                            user_id, name, age, weight, height, activity_level,
                            goal_type, goal_target, goal_unit, goal_deadline,
                            dietary_preference, food_allergies, medical_conditions,
                            injury_notes, theme
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        context.user_id, context.name, context.age, context.weight,
                        context.height, context.activity_level,
                        context.goal_type.value if context.goal_type else None,
                        context.goal_target, context.goal_unit.value if context.goal_unit else None,
                        context.goal_deadline.isoformat() if context.goal_deadline else None,
                        context.dietary_preference.value, food_allergies_json,
                        medical_conditions_json, context.injury_notes, context.theme
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to save user context: {e}")
            return False
    
    def load_user_context(self, user_id: str) -> Optional[UserSessionContext]:
        """Load user context from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Convert row to dict
                user_data = dict(row)
                
                # Parse JSON fields
                user_data['food_allergies'] = json.loads(user_data.get('food_allergies', '[]'))
                user_data['medical_conditions'] = json.loads(user_data.get('medical_conditions', '[]'))
                
                # Load recent conversations
                cursor.execute('''
                    SELECT role, content, agent_type, timestamp 
                    FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                ''', (user_id,))
                conversations = cursor.fetchall()
                
                # Load recent progress
                cursor.execute('''
                    SELECT metric, value, unit, notes, recorded_at 
                    FROM progress 
                    WHERE user_id = ? 
                    ORDER BY recorded_at DESC 
                    LIMIT 100
                ''', (user_id,))
                progress_entries = cursor.fetchall()
                
                # Build context object
                context_data = {
                    'user_id': user_data['user_id'],
                    'name': user_data['name'],
                    'age': user_data.get('age'),
                    'weight': user_data.get('weight'),
                    'height': user_data.get('height'),
                    'activity_level': user_data.get('activity_level', 'moderate'),
                    'food_allergies': user_data['food_allergies'],
                    'injury_notes': user_data.get('injury_notes'),
                    'theme': user_data.get('theme', 'light')
                }
                
                # Handle enums safely
                from context import GoalType, GoalUnit, DietaryPreference, MedicalCondition
                
                try:
                    if user_data.get('goal_type'):
                        context_data['goal_type'] = GoalType(user_data['goal_type'])
                except ValueError:
                    context_data['goal_type'] = GoalType.GENERAL_FITNESS
                
                try:
                    if user_data.get('goal_unit'):
                        context_data['goal_unit'] = GoalUnit(user_data['goal_unit'])
                except ValueError:
                    context_data['goal_unit'] = GoalUnit.KG
                
                try:
                    if user_data.get('dietary_preference'):
                        context_data['dietary_preference'] = DietaryPreference(user_data['dietary_preference'])
                except ValueError:
                    context_data['dietary_preference'] = DietaryPreference.NO_PREFERENCE
                
                # Convert medical conditions
                medical_conditions = []
                for condition in user_data['medical_conditions']:
                    try:
                        medical_conditions.append(MedicalCondition(condition))
                    except ValueError:
                        continue
                context_data['medical_conditions'] = medical_conditions
                
                if user_data.get('goal_target'):
                    context_data['goal_target'] = user_data['goal_target']
                
                if user_data.get('goal_deadline'):
                    from datetime import date
                    context_data['goal_deadline'] = date.fromisoformat(user_data['goal_deadline'])
                
                return UserSessionContext(**context_data)
                
        except Exception as e:
            logger.error(f"Failed to load user context: {e}")
            return None
    
    def save_progress_entry(self, user_id: str, metric: str, value: float, unit: str = "", notes: str = None) -> bool:
        """Save a progress entry."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO progress (user_id, metric, value, unit, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, metric, value, unit, notes))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save progress entry: {e}")
            return False
    
    def save_meal_plan(self, user_id: str, plan_data: Dict[str, Any], plan_name: str = None) -> bool:
        """Save a meal plan."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO meal_plans (user_id, plan_name, plan_data)
                    VALUES (?, ?, ?)
                ''', (user_id, plan_name, json.dumps(plan_data)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save meal plan: {e}")
            return False
    
    def save_workout_plan(self, user_id: str, plan_data: Dict[str, Any], plan_name: str = None) -> bool:
        """Save a workout plan."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO workout_plans (user_id, plan_name, plan_data)
                    VALUES (?, ?, ?)
                ''', (user_id, plan_name, json.dumps(plan_data)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save workout plan: {e}")
            return False
    
    def save_conversation_message(self, user_id: str, role: str, content: str, agent_type: str = None) -> bool:
        """Save a conversation message."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (user_id, role, content, agent_type)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, role, content, agent_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save conversation message: {e}")
            return False
    
    def get_user_progress(self, user_id: str, metric: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user progress entries."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if metric:
                    cursor.execute('''
                        SELECT * FROM progress 
                        WHERE user_id = ? AND metric = ? 
                        ORDER BY recorded_at DESC 
                        LIMIT ?
                    ''', (user_id, metric, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM progress 
                        WHERE user_id = ? 
                        ORDER BY recorded_at DESC 
                        LIMIT ?
                    ''', (user_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get user progress: {e}")
            return []

# Global database instance
db_manager = DatabaseManager()
