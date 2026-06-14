"""
shared/memory/ — 用户画像与会话管理。

提供用户画像读写、会话生命周期管理的统一接口。
Host 在每次请求前/后通过 import 直接调用，不走 MCP 协议。

存储: SQLite (MVP) → PostgreSQL (规模化)
"""

from shared.memory.manager import MemoryManager

__all__ = ["MemoryManager"]
