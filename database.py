# database.py - FIXED DATABASE MODULE
import sqlite3
import hashlib
import streamlit as st
import datetime

# Get database file from secrets or use default
try:
    DB_FILE = st.secrets["database"]["db_file"]
except:
    DB_FILE = "visionmate.db"
    print("⚠️ Using default database file: visionmate.db")

def init_db():
    """Initialize database with users table"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except sqlite3.Error as e:
        st.error(f"❌ Database initialization error: {e}")
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def add_user(name, email, username, password):
    """Add a new user to the database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert user into database
        c.execute(
            "INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)",
            (name, email, username, hashed_password)
        )
        
        conn.commit()
        print(f"✅ User registered: {username}")
        return True
        
    except sqlite3.IntegrityError as e:
        error_msg = str(e).lower()
        if "username" in error_msg:
            print(f"❌ Username already exists: {username}")
            return "This username is already taken. Please choose another username."
        elif "email" in error_msg:
            print(f"❌ Email already exists: {email}")
            return "This email is already registered. Please use another email address."
        else:
            print(f"❌ Database integrity error: {e}")
            return f"Registration error: {e}"
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return f"Database error: {e}"
        
    finally:
        if conn:
            conn.close()

def check_user(username, password):
    """Check user credentials for login"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Hash the input password
        hashed_password = hash_password(password)
        
        # Get user data
        c.execute(
            "SELECT name, password FROM users WHERE username = ?", 
            (username,)
        )
        user_data = c.fetchone()
        
        if user_data:
            name, stored_hash = user_data
            
            # Compare hashed passwords
            if hashed_password == stored_hash:
                # Update last login
                c.execute(
                    "UPDATE users SET last_login = ? WHERE username = ?",
                    (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username)
                )
                conn.commit()
                
                print(f"✅ Login successful: {username}")
                return True, name
            else:
                print(f"❌ Incorrect password for: {username}")
                return False, "Incorrect password. Please try again."
        else:
            print(f"❌ Username not found: {username}")
            return False, "Username not found. Please check your username and try again."
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False, f"Database error: {e}"
        
    finally:
        if conn:
            conn.close()

# The following functions are included for completeness but are not strictly used in the main app flow:
def get_user_info(username):
    """Get user information"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, name, email, username, created_at, last_login FROM users WHERE username = ?",
            (username,)
        )
        
        user = c.fetchone()
        
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "username": user[3],
                "created_at": user[4],
                "last_login": user[5]
            }
        return None
        
    except sqlite3.Error as e:
        print(f"❌ Error getting user info: {e}")
        return None
        
    finally:
        if conn:
            conn.close()

def get_all_users():
    """Get all users (for testing/admin)"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, name, email, username, created_at, last_login FROM users ORDER BY created_at DESC"
        )
        
        users = []
        for row in c.fetchall():
            users.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "username": row[3],
                "created_at": row[4],
                "last_login": row[5]
            })
        
        return users
        
    except sqlite3.Error as e:
        print(f"❌ Error getting users: {e}")
        return []
        
    finally:
        if conn:
            conn.close()

def delete_user(username):
    """Delete a user (for testing)"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        
        if c.rowcount > 0:
            print(f"✅ User deleted: {username}")
            return True
        else:
            print(f"❌ User not found: {username}")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Error deleting user: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def reset_database():
    """Reset database (for testing)"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()
        
        print("✅ Database reset successfully!")
        init_db()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error resetting database: {e}")
        return False