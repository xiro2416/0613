"""
shared/market_data/ — 结构化行情数据服务。

提供实时行情快照、资讯、持仓上下文的统一访问接口。
高频结构化数据，不经过 KnowledgeManager。
"""

from shared.market_data.client import MarketDataService

__all__ = ["MarketDataService"]
