"""SQLite 存储层 — 用户画像与会话的持久化。

MVP 阶段使用 SQLite 单文件存储。
替换为 PostgreSQL 只需实现相同接口的 PostgresStore。
"""

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime
from typing import Optional

from shared.types import (
    EmotionTag,
    Message,
    PersonaType,
    SessionContext,
    TimeSlot,
    UserProfile,
)


class MemoryStore:
    """SQLite 存储后端 — 可替换为 PostgresStore"""

    def __init__(self, db_path: str = "data/stock_agent.db"):
        self._db_path = db_path
        self._lock = threading.Lock()

        # 自动创建数据目录
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    # ── 建表 ──────────────────────────────────────

    def _create_tables(self) -> None:
        with self._lock:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    holdings TEXT NOT NULL DEFAULT '[]',
                    trading_style TEXT NOT NULL DEFAULT '',
                    risk_tolerance TEXT NOT NULL DEFAULT '',
                    psychological_state TEXT NOT NULL DEFAULT '',
                    defense_boundary TEXT NOT NULL DEFAULT '',
                    consecutive_losses INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    active_persona TEXT NOT NULL DEFAULT 'gentle',
                    today_pnl REAL,
                    emotional_state TEXT NOT NULL DEFAULT '',
                    time_slot TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'agent')),
                    content TEXT NOT NULL,
                    emotion_tag TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_sessions_user
                    ON sessions(user_id);
            """)

    # ── 用户画像 CRUD ──────────────────────────────

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()

        if row is None:
            return None

        return UserProfile(
            user_id=row["user_id"],
            holdings=json.loads(row["holdings"]),
            trading_style=row["trading_style"],
            risk_tolerance=row["risk_tolerance"],
            psychological_state=row["psychological_state"],
            defense_boundary=row["defense_boundary"],
            consecutive_losses=row["consecutive_losses"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_user_profile(self, user_id: str) -> UserProfile:
        now = datetime.now()
        now_iso = now.isoformat()

        with self._lock:
            self._conn.execute(
                """INSERT INTO users (user_id, holdings, created_at, updated_at)
                   VALUES (?, '[]', ?, ?)""",
                (user_id, now_iso, now_iso),
            )
            self._conn.commit()

        return UserProfile(
            user_id=user_id,
            holdings=[],
            trading_style="",
            risk_tolerance="",
            psychological_state="",
            defense_boundary="",
            consecutive_losses=0,
            created_at=now,
            updated_at=now,
        )

    def update_user_profile(self, user_id: str, update: dict) -> UserProfile:
        allowed = {
            "holdings",
            "trading_style",
            "risk_tolerance",
            "psychological_state",
            "defense_boundary",
            "consecutive_losses",
        }
        filtered = {k: v for k, v in update.items() if k in allowed}
        if not filtered:
            return self.get_user_profile(user_id)

        now_iso = datetime.now().isoformat()
        set_clauses = []
        params = []

        for key, value in filtered.items():
            if key == "holdings":
                value = json.dumps(value, ensure_ascii=False)
            set_clauses.append(f"{key} = ?")
            params.append(value)

        set_clauses.append("updated_at = ?")
        params.append(now_iso)
        params.append(user_id)

        with self._lock:
            self._conn.execute(
                f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = ?",
                params,
            )
            self._conn.commit()

        return self.get_user_profile(user_id)

    # ── 会话 CRUD ──────────────────────────────────

    def create_session(self, user_id: str) -> SessionContext:
        session_id = uuid.uuid4().hex[:12]
        now = datetime.now()

        with self._lock:
            self._conn.execute(
                """INSERT INTO sessions (session_id, user_id, created_at)
                   VALUES (?, ?, ?)""",
                (session_id, user_id, now.isoformat()),
            )
            self._conn.commit()

        return SessionContext(
            session_id=session_id,
            user_id=user_id,
            active_persona=PersonaType.GENTLE,
            conversation_history=[],
            created_at=now,
        )

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM sessions WHERE session_id = ? AND is_active = 1",
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        # 重建会话历史（最近 100 条）
        messages = self._load_messages(session_id)
        time_slot = None
        if row["time_slot"]:
            try:
                time_slot = TimeSlot(row["time_slot"])
            except ValueError:
                pass

        persona = PersonaType.GENTLE
        try:
            persona = PersonaType(row["active_persona"])
        except ValueError:
            pass

        return SessionContext(
            session_id=row["session_id"],
            user_id=row["user_id"],
            active_persona=persona,
            conversation_history=messages,
            today_pnl=row["today_pnl"],
            emotional_state=row["emotional_state"],
            time_slot=time_slot,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def append_message(self, session_id: str, message: Message) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO messages (session_id, role, content, emotion_tag, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    session_id,
                    message.role,
                    message.content,
                    message.emotion_tag.value if message.emotion_tag else None,
                    message.timestamp.isoformat() if message.timestamp else
                    datetime.now().isoformat(),
                ),
            )
            self._conn.commit()

    def set_persona(self, session_id: str, persona_type: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET active_persona = ? WHERE session_id = ?",
                (persona_type, session_id),
            )
            self._conn.commit()

    def update_time_context(self, session_id: str, time_slot: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET time_slot = ? WHERE session_id = ?",
                (time_slot, session_id),
            )
            self._conn.commit()

    def close_session(self, session_id: str) -> None:
        """关闭会话。MVP 仅标记结束，不做画像回流。"""
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET is_active = 0, closed_at = ? WHERE session_id = ?",
                (datetime.now().isoformat(), session_id),
            )
            self._conn.commit()

    # ── 内部辅助 ──────────────────────────────────

    def _load_messages(self, session_id: str) -> list[Message]:
        rows = self._conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC LIMIT 100",
            (session_id,),
        ).fetchall()

        messages = []
        for row in rows:
            emotion_tag = None
            if row["emotion_tag"]:
                try:
                    emotion_tag = EmotionTag(row["emotion_tag"])
                except ValueError:
                    pass

            messages.append(Message(
                role=row["role"],
                content=row["content"],
                emotion_tag=emotion_tag,
                timestamp=datetime.fromisoformat(row["timestamp"]),
            ))
        return messages
