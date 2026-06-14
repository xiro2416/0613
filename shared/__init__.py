"""
shared/ — 公共 Python 库层。

不启动任何进程，仅作为标准 Python 包被 import。
包含：全局类型定义、知识检索、行情数据、用户记忆四个子模块。

架构约定（见 docs/mcp-skill-migration.md §六-B）：
  - 由 LLM 语义决策调用的组件 → MCP Tool（进程隔离）
  - 确定性执行的组件（每次请求必然/由 Tool 内部调用）→ shared/ 库（Python import）
"""
