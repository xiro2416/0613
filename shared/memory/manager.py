"""MemoryManager — 记忆系统统一入口。

职责:
  - 用户画像生命周期管理
  - 会话上下文读写
  - 时间特征注入
  - 人设切换状态同步

调用模式: Host 在 LLM 调用之前/之后确定性调用，不走 MCP 协议。
"""

from typing import Optional

from shared.memory.store import MemoryStore
from shared.types import Message, SessionContext, TimeSlot, UserProfile


class MemoryManager:
    """记忆管理器 — Host 和业务 Server 均可 import"""

    def __init__(self, db_path: str = "data/stock_agent.db"):
        self._store = MemoryStore(db_path)

    # ── 用户画像 ──────────────────────────────

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像，不存在时返回 None"""
        return self._store.get_user_profile(user_id)

    def create_user_profile(self, user_id: str) -> UserProfile:
        """为新用户创建画像"""
        return self._store.create_user_profile(user_id)

    def update_user_profile(self, user_id: str, update: dict) -> UserProfile:
        """增量更新用户画像字段"""
        return self._store.update_user_profile(user_id, update)

    # ── 会话管理 ──────────────────────────────

    def create_session(self, user_id: str) -> SessionContext:
        """创建新会话"""
        return self._store.create_session(user_id)

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """获取会话上下文"""
        return self._store.get_session(session_id)

    def append_message(self, session_id: str, message: Message) -> None:
        """向会话历史追加一条消息"""
        self._store.append_message(session_id, message)

    def set_persona(self, session_id: str, persona_type: str) -> None:
        """更新会话的活跃人设"""
        self._store.set_persona(session_id, persona_type)

    # ── 时间特征注入 ──────────────────────────

    def update_time_context(self, session_id: str, time_slot: TimeSlot) -> None:
        """将当前时间状态注入会话上下文"""
        self._store.update_time_context(session_id, time_slot.value)

    def close_session(self, session_id: str) -> None:
        """关闭会话，持久化关键信息到用户画像"""
        self._store.close_session(session_id)
