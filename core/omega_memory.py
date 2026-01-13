import sqlite3
import os
import json
import logging
from datetime import datetime

class OmegaMemory:
    def __init__(self, db_path="memory/umbrasol.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.logger = logging.getLogger("Umbrasol.Memory")
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. TASK QUEUE: For reboot survival
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request TEXT NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, running, completed, failed
                    checkpoint TEXT, -- JSON blob of internal state
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. AUDIT TRAIL: Immutable history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    result TEXT,
                    risk_level TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 3. KNOWLEDGE BASE: Learned facts/preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 4. SEMANTIC CACHE: Request hash -> command mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_cache (
                    hash TEXT PRIMARY KEY,
                    tool TEXT NOT NULL,
                    command TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 5. HABITS: (TimeSlot, Context) -> frequency
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    context_key TEXT PRIMARY KEY, -- slot|app
                    counts TEXT NOT NULL, -- JSON blob of command frequencies
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 6. EXPERIENCE: task -> lesson mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience (
                    task_key TEXT PRIMARY KEY,
                    lesson TEXT NOT NULL, -- JSON blob
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_task(self, request):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (request) VALUES (?)", (request,))
            conn.commit()
            return cursor.lastrowid

    def update_task_checkpoint(self, task_id, status, checkpoint_data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, checkpoint = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status, json.dumps(checkpoint_data), task_id))
            conn.commit()

    def get_pending_tasks(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE status != 'completed' AND status != 'failed'")
            return [dict(row) for row in cursor.fetchall()]

    def log_action(self, command, result, risk_level="low"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_trail (command, result, risk_level) 
                VALUES (?, ?, ?)
            """, (command, str(result), risk_level))
            conn.commit()

    def save_preference(self, key, value, category="general"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (key, value, category) 
                VALUES (?, ?, ?) 
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """, (key, value, category))
            conn.commit()

    def get_preference(self, key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM knowledge WHERE key = ?", (key,))
            res = cursor.fetchone()
            return res[0] if res else None

    # --- UNIFIED MEMORY EXTENSIONS ---
    
    def get_cache(self, req_hash):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT tool, command FROM semantic_cache WHERE hash = ?", (req_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def set_cache(self, req_hash, tool, command):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO semantic_cache (hash, tool, command) 
                VALUES (?, ?, ?) 
                ON CONFLICT(hash) DO UPDATE SET tool=excluded.tool, command=excluded.command
            """, (req_hash, tool, command))
            conn.commit()

    def get_habit(self, context_key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT counts FROM habits WHERE context_key = ?", (context_key,))
            res = cursor.fetchone()
            return json.loads(res[0]) if res else {}

    def save_habit(self, context_key, counts):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO habits (context_key, counts) 
                VALUES (?, ?) 
                ON CONFLICT(context_key) DO UPDATE SET counts=excluded.counts, updated_at=CURRENT_TIMESTAMP
            """, (context_key, json.dumps(counts)))
            conn.commit()

    def get_experience(self, task_key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lesson FROM experience WHERE task_key = ?", (task_key,))
            res = cursor.fetchone()
            return json.loads(res[0]) if res else None

    def save_experience(self, task_key, lesson):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO experience (task_key, lesson) 
                VALUES (?, ?) 
                ON CONFLICT(task_key) DO UPDATE SET lesson=excluded.lesson, updated_at=CURRENT_TIMESTAMP
            """, (task_key, json.dumps(lesson)))
            conn.commit()
