"""
meme-comfort MCP Server — 心理按摩与股民热梗库。

暴露 2 个工具:
  - loss_meme_pick → 按亏损程度匹配自嘲热梗
  - emo_detox_pick → 匹配 emo 化解内容

数据依赖: import shared.knowledge.meme_library（进程内调用）。
"""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server

from tools import MemeComfortTools

server = Server("meme-comfort")
tools = MemeComfortTools()


@server.tool()
async def loss_meme_pick(loss_level: str = "any") -> str:
    """按亏损程度匹配自嘲热梗。

    loss_level: "mild"(轻) | "moderate"(中) | "severe"(重) | "any"(不限)
    返回匹配的梗列表，供 LLM 根据 Persona 人格化输出。
    """
    result = tools.loss_meme_pick(loss_level)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def emo_detox_pick(trigger: str = "") -> str:
    """匹配 emo 化解内容。

    trigger: "loss" | "fomo" | "lonely" | "tired" | ""(自动检测)
    返回化解内容列表。
    """
    result = tools.emo_detox_pick(trigger)
    return json.dumps(result, ensure_ascii=False)


def main():
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
