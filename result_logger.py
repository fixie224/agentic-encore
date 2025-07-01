import sqlite3
from datetime import datetime

# Initialize SQLite DB (run once)
def init_db():
    conn = sqlite3.connect('data/results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT,
        topic TEXT,
        is_correct INTEGER,
        time_taken REAL,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

# Log result into DB
def log_result_db(question_id, topic, is_correct, time_taken):
    conn = sqlite3.connect('data/results.db')
    c = conn.cursor()
    c.execute('''INSERT INTO results (question_id, topic, is_correct, time_taken, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
              (question_id, topic, int(is_correct), time_taken, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Optional: Get summary by topic
def get_topic_summary():
    conn = sqlite3.connect('data/results.db')
    c = conn.cursor()
    c.execute('''SELECT topic, COUNT(*) as total,
                        SUM(is_correct) as correct
                 FROM results
                 GROUP BY topic''')
    rows = c.fetchall()
    conn.close()
    return rows