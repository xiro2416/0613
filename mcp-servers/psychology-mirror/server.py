"""
psychology-mirror MCP Server — 人性对齐与深度交流。

暴露 2 个工具:
  - greed_detect → 贪婪心理信号检测
  - fear_detect  → 恐惧/防御心理信号检测

数据依赖: import shared.knowledge（进程内调用）。
"""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server

from tools import PsychologyMirrorTools

server = Server("psychology-mirror")
tools = PsychologyMirrorTools()


@server.tool()
async def greed_detect(user_query: str) -> str:
    """检测用户当前的贪婪心理信号。

    触发场景: 用户过度乐观、想追涨、想满仓、赌徒心理浮现时。
    返回贪婪指标（0-1）和对应的镜像反思提示。
    """
    result = tools.greed_detect(user_query)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def fear_detect(user_query: str) -> str:
    """检测用户当前的恐惧/防御心理信号。

    触发场景: 连续回撤后想割肉、恐慌抛售、过度防御时。
    返回恐惧指标（0-1）和对应的安抚提示。
    """
    result = tools.fear_detect(user_query)
    return json.dumps(result, ensure_ascii=False)


def main():
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
