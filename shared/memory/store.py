"""SQLite 存储层 — 用户画像与会话的持久化。

MVP 阶段使用 SQLite 单文件存储。
替换为 PostgreSQL 只需实现相同接口的 PostgresStore。
"""

from typing import Optional

from shared.types import Message, SessionContext, UserProfile


class MemoryStore:
    """SQLite 存储后端 — 可替换为 PostgresStore"""

    def __init__(self, db_path: str = "data/stock_agent.db"):
        self._db_path = db_path
        # 实现要点: 自动建表 + 迁移

    # ── 用户画像 CRUD ──────────────────────────

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        ...

    def create_user_profile(self, user_id: str) -> UserProfile:
        ...

    def update_user_profile(self, user_id: str, update: dict) -> UserProfile:
        ...

    # ── 会话 CRUD ──────────────────────────────

    def create_session(self, user_id: str) -> SessionContext:
        ...

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        ...

    def append_message(self, session_id: str, message: Message) -> None:
        ...

    def set_persona(self, session_id: str, persona_type: str) -> None:
        ...

    def update_time_context(self, session_id: str, time_slot: str) -> None:
        ...

    def close_session(self, session_id: str) -> None:
        ...
