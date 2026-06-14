"""
life-service MCP Server — 生活服务 Skills 连接器。

暴露 2 个工具:
  - fatigue_suggest   → 疲劳补给推荐
  - late_night_care   → 深夜陪伴关怀

自包含，无外部依赖（除 shared.types）。
"""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server

from tools import LifeServiceTools

server = Server("life-service")
tools = LifeServiceTools()


@server.tool()
async def fatigue_suggest() -> str:
    """为疲劳状态用户推荐补给服务。

    触发场景: 深夜复盘后、脑力透支、长时间盯盘后。
    返回轻量化服务卡片（可一键下单）。
    """
    result = tools.fatigue_suggest()
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def late_night_care() -> str:
    """深夜陪伴关怀建议。

    触发场景: 凌晨还在复盘、失眠看盘、盘后焦虑。
    返回关怀建议和健康评分。
    """
    result = tools.late_night_care()
    return json.dumps(result, ensure_ascii=False)


def main():
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
