import aiosqlite
import os
import json
import logging
from datetime import datetime

class OmegaMemory:
    def __init__(self, db_path="memory/umbrasol.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.logger = logging.getLogger("Umbrasol.Memory")
        self._conn = None

    async def ensure_db(self):
        """Initializes the database schema if it doesn't exist."""
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.db_path)
            self._conn.row_factory = aiosqlite.Row
            await self._init_db()

    async def _init_db(self):
        """Initialize the database schema."""
        # 1. TASK QUEUE: For reboot survival
        await self._conn.execute("""
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
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                result TEXT,
                risk_level TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 3. KNOWLEDGE BASE: Learned facts/preferences
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 4. SEMANTIC CACHE: Request hash -> command mapping
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_cache (
                hash TEXT PRIMARY KEY,
                tool TEXT NOT NULL,
                command TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 5. HABITS: (TimeSlot, Context) -> frequency
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                context_key TEXT PRIMARY KEY, -- slot|app
                counts TEXT NOT NULL, -- JSON blob of command frequencies
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 6. EXPERIENCE: task -> lesson mapping
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS experience (
                task_key TEXT PRIMARY KEY,
                lesson TEXT NOT NULL, -- JSON blob
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._conn.commit()

    async def add_task(self, request):
        await self.ensure_db()
        cursor = await self._conn.execute("INSERT INTO tasks (request) VALUES (?)", (request,))
        await self._conn.commit()
        return cursor.lastrowid

    async def update_task_checkpoint(self, task_id, status, checkpoint_data):
        await self.ensure_db()
        await self._conn.execute("""
            UPDATE tasks 
            SET status = ?, checkpoint = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (status, json.dumps(checkpoint_data), task_id))
        await self._conn.commit()

    async def get_pending_tasks(self):
        await self.ensure_db()
        async with self._conn.execute("SELECT * FROM tasks WHERE status != 'completed' AND status != 'failed'") as cursor:
            return [dict(row) for row in await cursor.fetchall()]

    async def log_action(self, command, result, risk_level="low"):
        await self.ensure_db()
        await self._conn.execute("""
            INSERT INTO audit_trail (command, result, risk_level) 
            VALUES (?, ?, ?)
        """, (command, str(result), risk_level))
        await self._conn.commit()

    async def save_preference(self, key, value, category="general"):
        await self.ensure_db()
        await self._conn.execute("""
            INSERT INTO knowledge (key, value, category) 
            VALUES (?, ?, ?) 
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
        """, (key, value, category))
        await self._conn.commit()

    async def get_preference(self, key):
        await self.ensure_db()
        async with self._conn.execute("SELECT value FROM knowledge WHERE key = ?", (key,)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else None

    # --- UNIFIED MEMORY EXTENSIONS ---
    
    async def get_cache(self, req_hash):
        await self.ensure_db()
        async with self._conn.execute("SELECT tool, command FROM semantic_cache WHERE hash = ?", (req_hash,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def set_cache(self, req_hash, tool, command):
        await self.ensure_db()
        await self._conn.execute("""
            INSERT INTO semantic_cache (hash, tool, command) 
            VALUES (?, ?, ?) 
            ON CONFLICT(hash) DO UPDATE SET tool=excluded.tool, command=excluded.command
        """, (req_hash, tool, command))
        await self._conn.commit()

    async def get_habit(self, context_key):
        await self.ensure_db()
        async with self._conn.execute("SELECT counts FROM habits WHERE context_key = ?", (context_key,)) as cursor:
            res = await cursor.fetchone()
            return json.loads(res[0]) if res else {}

    async def save_habit(self, context_key, counts):
        await self.ensure_db()
        await self._conn.execute("""
            INSERT INTO habits (context_key, counts) 
            VALUES (?, ?) 
            ON CONFLICT(context_key) DO UPDATE SET counts=excluded.counts, updated_at=CURRENT_TIMESTAMP
        """, (context_key, json.dumps(counts)))
        await self._conn.commit()

    async def get_experience(self, task_key):
        await self.ensure_db()
        async with self._conn.execute("SELECT lesson FROM experience WHERE task_key = ?", (task_key,)) as cursor:
            res = await cursor.fetchone()
            return json.loads(res[0]) if res else None

    async def save_experience(self, task_key, lesson):
        await self.ensure_db()
        await self._conn.execute("""
            INSERT INTO experience (task_key, lesson) 
            VALUES (?, ?) 
            ON CONFLICT(task_key) DO UPDATE SET lesson=excluded.lesson, updated_at=CURRENT_TIMESTAMP
        """, (task_key, json.dumps(lesson)))
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None
