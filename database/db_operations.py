import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

DATABASE_PATH = "health_wellness.db"

DATABASE_PATH = Path(__file__).resolve().parent / 'health_data.db'

def init_db() -> bool:
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                agent_type TEXT NOT NULL
            )
        ''')
        
        # Create user_profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                user_name TEXT,
                age INTEGER,
                gender TEXT,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT,
                goal_type TEXT,
                dietary_restrictions TEXT,
                allergies TEXT,
                medical_conditions TEXT,
                medications TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create progress_tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                description TEXT,
                agent_type TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Create goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                description TEXT NOT NULL,
                target_value REAL,
                target_unit TEXT,
                target_date DATE,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Create handoffs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS handoffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                reason TEXT NOT NULL,
                context_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully.")
        return True
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        return False

def save_conversation(user_id: str, message: str, response: str, agent_type: str) -> bool:
    """Save a conversation to the database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, message, response, agent_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message, response, agent_type))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")
        return False

def get_conversation_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get conversation history for a user"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, message, response, agent_type
            FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'timestamp': row[0],
                'message': row[1],
                'response': row[2],
                'agent_type': row[3]
            })
        
        return conversations
        
    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}")
        return []

def save_user_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    """Save or update user profile"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        dietary_restrictions = json.dumps(profile_data.get('dietary_restrictions', []))
        allergies = json.dumps(profile_data.get('allergies', []))
        medical_conditions = json.dumps(profile_data.get('medical_conditions', []))
        medications = json.dumps(profile_data.get('medications', []))
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, user_name, age, gender, height_cm, weight_kg, activity_level, 
             goal_type, dietary_restrictions, allergies, medical_conditions, medications, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            profile_data.get('user_name'),
            profile_data.get('age'),
            profile_data.get('gender'),
            profile_data.get('height_cm'),
            profile_data.get('weight_kg'),
            profile_data.get('activity_level'),
            profile_data.get('goal_type'),
            dietary_restrictions,
            allergies,
            medical_conditions,
            medications,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving user profile: {str(e)}")
        return False

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_name, age, gender, height_cm, weight_kg, activity_level,
                   goal_type, dietary_restrictions, allergies, medical_conditions, medications
            FROM user_profiles
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_name': row[0],
                'age': row[1],
                'gender': row[2],
                'height_cm': row[3],
                'weight_kg': row[4],
                'activity_level': row[5],
                'goal_type': row[6],
                'dietary_restrictions': json.loads(row[7]) if row[7] else [],
                'allergies': json.loads(row[8]) if row[8] else [],
                'medical_conditions': json.loads(row[9]) if row[9] else [],
                'medications': json.loads(row[10]) if row[10] else []
            }
        
        return None
        
    except Exception as e:
        print(f"Error retrieving user profile: {str(e)}")
        return None

def save_progress_update(user_id: str, metric_type: str, value: float, 
                        unit: str, description: str, agent_type: str) -> bool:
    """Save a progress update"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO progress_tracking 
            (user_id, metric_type, value, unit, description, agent_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, metric_type, value, unit, description, agent_type))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving progress update: {str(e)}")
        return False

def get_progress_history(user_id: str, metric_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get progress history for a user"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        if metric_type:
            cursor.execute('''
                SELECT timestamp, metric_type, value, unit, description, agent_type
                FROM progress_tracking
                WHERE user_id = ? AND metric_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, metric_type, limit))
        else:
            cursor.execute('''
                SELECT timestamp, metric_type, value, unit, description, agent_type
                FROM progress_tracking
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        progress_updates = []
        for row in rows:
            progress_updates.append({
                'timestamp': row[0],
                'metric_type': row[1],
                'value': row[2],
                'unit': row[3],
                'description': row[4],
                'agent_type': row[5]
            })
        
        return progress_updates
        
    except Exception as e:
        print(f"Error retrieving progress history: {str(e)}")
        return []

def save_goal(user_id: str, goal_type: str, description: str, 
              target_value: float = None, target_unit: str = None, 
              target_date: str = None) -> bool:
    """Save a user goal"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goals 
            (user_id, goal_type, description, target_value, target_unit, target_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, goal_type, description, target_value, target_unit, target_date))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving goal: {str(e)}")
        return False

def get_user_goals(user_id: str, status: str = 'active') -> List[Dict[str, Any]]:
    """Get user goals"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, goal_type, description, target_value, target_unit, 
                   target_date, status, created_at
            FROM goals
            WHERE user_id = ? AND status = ?
            ORDER BY created_at DESC
        ''', (user_id, status))
        
        rows = cursor.fetchall()
        conn.close()
        
        goals = []
        for row in rows:
            goals.append({
                'id': row[0],
                'goal_type': row[1],
                'description': row[2],
                'target_value': row[3],
                'target_unit': row[4],
                'target_date': row[5],
                'status': row[6],
                'created_at': row[7]
            })
        
        return goals
        
    except Exception as e:
        print(f"Error retrieving user goals: {str(e)}")
        return []

def save_handoff(user_id: str, from_agent: str, to_agent: str, 
                reason: str, context_data: Dict[str, Any] = None) -> bool:
    """Save an agent handoff"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        context_json = json.dumps(context_data) if context_data else None
        
        cursor.execute('''
            INSERT INTO handoffs 
            (user_id, from_agent, to_agent, reason, context_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, from_agent, to_agent, reason, context_json))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving handoff: {str(e)}")
        return False

def get_handoff_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get handoff history for a user"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, from_agent, to_agent, reason, context_data
            FROM handoffs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        handoffs = []
        for row in rows:
            handoffs.append({
                'timestamp': row[0],
                'from_agent': row[1],
                'to_agent': row[2],
                'reason': row[3],
                'context_data': json.loads(row[4]) if row[4] else {}
            })
        
        return handoffs
        
    except Exception as e:
        print(f"Error retrieving handoff history: {str(e)}")
        return []

def cleanup_old_data(days_to_keep: int = 90) -> bool:
    """Clean up old conversation data"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_to_keep)
        
        cursor.execute('''
            DELETE FROM conversations 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        cursor.execute('''
            DELETE FROM handoffs 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error cleaning up old data: {str(e)}")
        return False

def get_database_stats() -> Dict[str, int]:
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count conversations
        cursor.execute('SELECT COUNT(*) FROM conversations')
        stats['total_conversations'] = cursor.fetchone()[0]
        
        # Count users
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
        stats['total_users'] = cursor.fetchone()[0]
        
        # Count progress updates
        cursor.execute('SELECT COUNT(*) FROM progress_tracking')
        stats['total_progress_updates'] = cursor.fetchone()[0]
        
        # Count goals
        cursor.execute('SELECT COUNT(*) FROM goals')
        stats['total_goals'] = cursor.fetchone()[0]
        
        # Count handoffs
        cursor.execute('SELECT COUNT(*) FROM handoffs')
        stats['total_handoffs'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {str(e)}")
        return {}
