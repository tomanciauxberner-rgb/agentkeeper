import sqlite3
import json
from pathlib import Path
from src.cso.types import CognitiveStateObject


class Storage:
    def __init__(self, db_path: str = "agentkeeper.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

    def save(self, cso: CognitiveStateObject):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents (agent_id, state_json, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (cso.agent_id, json.dumps(cso.to_dict()), cso.created_at, cso.updated_at))
            conn.commit()

    def load(self, agent_id: str) -> CognitiveStateObject | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT state_json FROM agents WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            if row:
                return CognitiveStateObject.from_dict(json.loads(row[0]))
            return None

    def delete(self, agent_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
            conn.commit()
