"""
market-analyzer MCP Server — 行情分析及买卖建议。

暴露 2 个工具:
  - compute_value_score    → 价值投资基本面分析
  - compute_shortterm_heat → 短期赚/亏钱效应热力

进程隔离: 独立 Python 进程，通过 STDIO 与 Host 通信。
数据依赖: import shared.knowledge, shared.market_data（进程内调用）。
"""

import asyncio
import json
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from tools import MarketAnalyzerTools

# ── 服务初始化 ──────────────────────────────

server = Server("market-analyzer")
tools = MarketAnalyzerTools()


@server.tool()
async def compute_value_score(
    user_query: str,
    tickers: Optional[list[str]] = None,
) -> str:
    """按价值投资框架计算个股/市场的基本面得分。

    适用于: 中长线价值投资者，需要研报和基本面分析时。
    不适合: 日内短线交易、打板题材。
    """
    result = tools.compute_value_score(user_query, tickers)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def compute_shortterm_heat(
    user_query: str,
    tickers: Optional[list[str]] = None,
) -> str:
    """计算短期赚钱/亏钱效应得分，输出打板情绪热力。

    适用于: 短线/打板/题材轮动交易者。
    不适合: 价值投资、长线持有。
    """
    result = tools.compute_shortterm_heat(user_query, tickers)
    return json.dumps(result, ensure_ascii=False)


# ── 启动 ────────────────────────────────────

def main():
    """STDIO 模式入口"""
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    main()
