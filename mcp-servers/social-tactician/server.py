"""
social-tactician MCP Server — 股市圈层社交辅助。

暴露 2 个工具:
  - ice_break_suggest → 行情感知破冰建议
  - deep_talk_suggest → 深度交流话题框架

数据依赖: import shared.knowledge（进程内调用）。
"""

import asyncio
import json
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from tools import SocialTacticianTools

server = Server("social-tactician")
tools = SocialTacticianTools()


@server.tool()
async def ice_break_suggest(target_holdings: Optional[list[str]] = None) -> str:
    """根据市场行情和持仓信息生成社交破冰建议。

    可感知社交对象的持仓板块行情，生成低刻意度的自然开场白方向。
    返回话题角度、破冰话术方向、市场钩子。
    """
    result = tools.ice_break_suggest(target_holdings=target_holdings)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def deep_talk_suggest(topic: str = "") -> str:
    """生成深度交流话题框架。

    返回完整的对话框架（开场→过渡→核心主题→收尾），
    以及需要避免的尬聊雷区。
    """
    result = tools.deep_talk_suggest(topic=topic)
    return json.dumps(result, ensure_ascii=False)


def main():
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
