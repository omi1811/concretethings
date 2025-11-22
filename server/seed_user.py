import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data.sqlite3"

def seed_user():
    print(f"Seeding user into {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    email = "admin@example.com"
    password = "password123"
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"User {email} already exists. ID: {existing[0]}")
            # Ensure is_system_admin is true
            cursor.execute("UPDATE users SET is_system_admin = 1, is_active = 1, password_hash = ? WHERE id = ?", (password_hash, existing[0]))
            print("Updated user permissions and password.")
        else:
            cursor.execute("""
                INSERT INTO users (email, phone, full_name, password_hash, is_system_admin, is_company_admin, is_active, failed_login_attempts, role, is_support_admin, is_email_verified, is_phone_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (email, "1234567890", "System Admin", password_hash, 1, 1, 1, 0, "system_admin", 0, 1, 1))
            print(f"Created user {email}.")
            
        conn.commit()
        print("Seeding successful!")
        
    except Exception as e:
        print(f"Error seeding user: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_user()
