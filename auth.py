import streamlit as st
import hashlib
from database import get_db_connection
from datetime import datetime

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return hash_password(password) == hashed

def create_user(user_data):
    """Create a new user in the database."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (user_data['username'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False
        
        # Hash the password
        password_hash = hash_password(user_data['password'])
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, age, gender, height, weight, 
                             activity_level, fitness_goal, medical_conditions, dietary_restrictions, 
                             emergency_contact, preferred_language, created_at, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_data['username'],
            user_data.get('email', ''),
            password_hash,
            user_data.get('age', 25),
            user_data.get('gender', 'Male'),
            user_data.get('height', 170),
            user_data.get('weight', 70),
            user_data.get('activity_level', 'Moderately Active'),
            user_data.get('fitness_goal', 'General Health'),
            user_data.get('medical_conditions', ''),
            user_data.get('dietary_restrictions', ''),
            user_data.get('emergency_contact', ''),
            user_data.get('preferred_language', 'English'),
            datetime.now(),
            None
        ))
        
        user_id = cursor.fetchone()[0]
        result = cursor.fetchone()
        user_id = result[0] if result else None
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return user_id is not None
        
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

def authenticate_user(username, password):
    """Authenticate a user."""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        # Find user
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user[1]):
            user_id = user[0]
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(), user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return user_id
        
        cursor.close()
        conn.close()
        return None
        
    except Exception as e:
        st.error(f"Error authenticating user: {str(e)}")
        return None

def logout_user():
    """Logout the current user."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.success("👋 Logged out successfully!")

def get_user_profile(user_id):
    """Get user profile information."""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, age, gender, height, weight, activity_level, 
                   fitness_goal, medical_conditions, dietary_restrictions, emergency_contact, 
                   preferred_language, created_at, updated_at, last_login
            FROM users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            user_profile = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'age': user[3],
                'gender': user[4],
                'height': user[5],
                'weight': user[6],
                'activity_level': user[7],
                'fitness_goal': user[8],
                'medical_conditions': user[9],
                'dietary_restrictions': user[10],
                'emergency_contact': user[11],
                'preferred_language': user[12],
                'created_at': user[13],
                'updated_at': user[14],
                'last_login': user[15]
            }
            
            cursor.close()
            conn.close()
            return user_profile
        
        cursor.close()
        conn.close()
        return None
        
    except Exception as e:
        st.error(f"Error fetching user profile: {str(e)}")
        return None

def update_user_profile(user_id, update_data):
    """Update user profile information."""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for key, value in update_data.items():
            if key != 'id':  # Don't update ID
                update_fields.append(f"{key} = %s")
                values.append(value)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error updating user profile: {str(e)}")
        return False