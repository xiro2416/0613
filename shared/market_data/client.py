"""行情数据客户端 — 对接第三方行情 API。

MVP 阶段对接 Akshare / Tushare（免费源）。
生产环境可替换为商业数据源（Wind / 东方财富）。

所有业务 MCP Server 在自己的进程中实例化此客户端。
"""

from shared.types import MarketContext, MarketSnapshot, NewsItem


class MarketDataService:
    """行情数据服务"""

    def __init__(self, api_key: str = ""):
        self._api_key = api_key

    def get_snapshot(self, index_name: str) -> MarketSnapshot:
        """获取指定指数的实时快照（盘前/盘中/盘后均可调）

        Args:
            index_name: 指数名称 (e.g. "上证指数", "创业板指")

        Returns:
            包含价格、涨跌幅、成交量的快照
        """
        ...

    def get_news(self, keywords: list[str], limit: int = 20) -> list[NewsItem]:
        """获取相关资讯

        Args:
            keywords: 搜索关键词
            limit: 最大条数

        Returns:
            资讯条目列表（含情绪倾向标注）
        """
        ...

    def get_holdings_context(self, holdings: list[str]) -> MarketContext:
        """获取用户持仓的市场全景上下文

        Args:
            holdings: 持仓标的列表 (e.g. ["600519", "000858"])

        Returns:
            包含快照、资讯、持仓行情的完整市场上下文
        """
        ...
