"""对话记忆（SQLite 持久化）。"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from ..config import APP_CONFIG
from ..utils.logger import get_logger

logger = get_logger("agents.memory")


class ConversationMemory:
    """简单的 SQLite 对话记忆。"""

    def __init__(self, db_path: Path | None = None, session_id: str = "default") -> None:
        self.db_path = db_path or (APP_CONFIG.vectorstore_dir / "conversations.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ts REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_ts ON messages(session_id, ts)"
            )
            conn.commit()

    def add(self, role: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, ts) VALUES (?, ?, ?, ?)",
                (self.session_id, role, content, time.time()),
            )
            conn.commit()

    def get_history(self, limit: int = 20) -> list[BaseMessage]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY ts ASC LIMIT ?",
                (self.session_id, limit),
            ).fetchall()
        out: list[BaseMessage] = []
        for role, content in rows:
            if role == "user":
                out.append(HumanMessage(content=content))
            elif role == "assistant":
                out.append(AIMessage(content=content))
            elif role == "system":
                out.append(SystemMessage(content=content))
        return out

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (self.session_id,))
            conn.commit()

    def export(self) -> list[dict]:
        """导出全部历史为 JSON 列表。"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content, ts FROM messages WHERE session_id = ? ORDER BY ts ASC",
                (self.session_id,),
            ).fetchall()
        return [{"role": r, "content": c, "ts": t} for r, c, t in rows]

    def import_json(self, data: str | list[dict]) -> None:
        if isinstance(data, str):
            data = json.loads(data)
        with sqlite3.connect(self.db_path) as conn:
            for item in data:
                conn.execute(
                    "INSERT INTO messages (session_id, role, content, ts) VALUES (?, ?, ?, ?)",
                    (self.session_id, item["role"], item["content"], item["ts"]),
                )
            conn.commit()