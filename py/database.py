import sqlite3
import pickle
import base64
import datetime
import numpy as np

conn = sqlite3.connect('db/attendance.db', check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                (user_id TEXT, time TIMESTAMP, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id TEXT PRIMARY KEY, name TEXT, phone TEXT, gender TEXT, memo TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, encodings BLOB)''')
    conn.commit()

def update_table():
    c.execute("PRAGMA table_info(attendance)")
    attendance_columns = [column[1] for column in c.fetchall()]
    if 'user_id' not in attendance_columns:
        c.execute("ALTER TABLE attendance ADD COLUMN user_id TEXT")
    
    c.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in c.fetchall()]
    if 'phone' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    if 'gender' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    if 'memo' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN memo TEXT")
    if 'created_at' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
    if 'updated_at' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP")
    conn.commit()

def log_attendance(user_id, status):
    now = datetime.datetime.now()
    c.execute("INSERT INTO attendance (user_id, time, status) VALUES (?, ?, ?)", (user_id, now, status))
    conn.commit()
    
def get_user_logs(user_id):
    c.execute("""
        SELECT attendance.time, attendance.status, users.name
        FROM attendance
        JOIN users ON attendance.user_id = users.id
        WHERE attendance.user_id = ?
    """, (user_id,))
    logs = [{"time": row[0], "status": row[1], "name": row[2]} for row in c.fetchall()]
    return logs

def get_today_logs():
    today = datetime.datetime.now().date()
    c.execute("""
        SELECT attendance.user_id, attendance.time, attendance.status, users.name
        FROM attendance
        JOIN users ON attendance.user_id = users.id
        WHERE DATE(attendance.time) = ?
    """, (today,))
    logs = [{"user_id": row[0], "time": row[1], "status": row[2], "name": row[3]} for row in c.fetchall()]
    return logs

    return logs

def add_user(user_id, name, phone, gender, memo, encodings):
    now = datetime.datetime.now()
    c.execute("INSERT OR REPLACE INTO users (id, name, phone, gender, memo, created_at, updated_at, encodings) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              (user_id, name, phone, gender, memo, now, now, pickle.dumps(encodings)))
    conn.commit()

def update_user(user_id, phone, gender, memo, encodings):
    now = datetime.datetime.now()
    c.execute("UPDATE users SET phone = ?, gender = ?, memo = ?, encodings = ?, updated_at = ? WHERE id = ?", 
              (phone, gender, memo, pickle.dumps(encodings), now, user_id))
    conn.commit()

def get_users():
    c.execute("SELECT id, name, created_at, updated_at FROM users")
    return [{"id": row[0], "name": row[1], "created_at": row[2], "updated_at": row[3]} for row in c.fetchall()]

def delete_user(user_id):
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

def get_user_info(user_id):
    c.execute("SELECT id, name, phone, gender, memo, encodings FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if row:
        encodings = pickle.loads(row[5])
        if len(encodings) > 0:
            image_base64 = base64.b64encode(np.array(encodings[0]).tobytes()).decode('utf-8')
        else:
            image_base64 = None
        return {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "gender": 'F' if row[3].lower() == 'female' else 'M',
            "memo": row[4],
            "image": image_base64
        }
    return None

def check_existing_name(name):
    c.execute("SELECT COUNT(*) FROM users WHERE name LIKE ?", (name + '%',))
    count = c.fetchone()[0]
    return count

def check_existing_face(encodings):
    c.execute("SELECT encodings FROM users")
    rows = c.fetchall()
    for row in rows:
        known_encodings = pickle.loads(row[0])
        if any(np.linalg.norm(known_encoding - encodings[0]) < 0.6 for known_encoding in known_encodings):
            return True
    return False

create_table()
update_table()  # Ensure the table schema is up-to-date

def load_known_faces():
    c.execute("SELECT id, encodings FROM users")
    rows = c.fetchall()
    known_faces = {}
    for row in rows:
        user_id, encodings_blob = row
        encodings = pickle.loads(encodings_blob)
        known_faces[user_id] = encodings
    return known_faces

known_faces = load_known_faces()
