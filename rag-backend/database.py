import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

# Use mounted volume path for database persistence
DB_PATH = os.path.join('/app/data', 'users.db') if os.path.exists('/app/data') else 'users.db'

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            google_id TEXT UNIQUE,
            password_hash TEXT,
            team TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def create_user(email, name, google_id=None, password=None, team=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
    
    try:
        cursor.execute('''
            INSERT INTO users (email, name, google_id, password_hash, team)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, name, google_id, password_hash, team))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_google_id(google_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_password(email, password):
    user = get_user_by_email(email)
    if user and user[4]:  # password_hash is at index 4
        return hashlib.sha256(password.encode()).hexdigest() == user[4]
    return False

def store_otp(email, otp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    expires_at = datetime.now() + timedelta(minutes=10)
    cursor.execute('''
        INSERT INTO password_reset (email, otp, expires_at)
        VALUES (?, ?, ?)
    ''', (email, otp, expires_at))
    conn.commit()
    conn.close()

def verify_otp(email, otp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM password_reset 
        WHERE email = ? AND otp = ? AND expires_at > ? AND used = 0
        ORDER BY id DESC LIMIT 1
    ''', (email, otp, datetime.now()))
    result = cursor.fetchone()
    if result:
        cursor.execute('UPDATE password_reset SET used = 1 WHERE id = ?', (result[0],))
        conn.commit()
    conn.close()
    return result is not None

def update_password(email, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

