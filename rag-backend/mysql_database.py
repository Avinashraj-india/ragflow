import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255),
            google_id VARCHAR(255) UNIQUE,
            password_hash VARCHAR(255),
            team VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_user(email, name, google_id=None, password=None, team=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
    
    try:
        cursor.execute('''
            INSERT INTO users (email, name, google_id, password_hash, team)
            VALUES (%s, %s, %s, %s, %s)
        ''', (email, name, google_id, password_hash, team))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_password(email, password):
    user = get_user_by_email(email)
    if user and user[4]:
        return hashlib.sha256(password.encode()).hexdigest() == user[4]
    return False