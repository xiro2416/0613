"""
market-analyzer 工具实现 — 行情分析及买卖建议。

工具返回纯数据（不含 Persona 色彩）。
Persona 转换由 Host LLM 在 Phase 2 完成。

数据依赖:
  - compute_value_score    → shared.knowledge (market_terms, market_narratives)
  - compute_shortterm_heat → shared.market_data (MarketDataService)
"""

from typing import Optional

from shared.knowledge.manager import KnowledgeManager
from shared.market_data.client import MarketDataService
from shared.types import ToolContext


class MarketAnalyzerTools:
    """行情分析工具集"""

    def __init__(
        self,
        market_data: Optional[MarketDataService] = None,
        knowledge: Optional[KnowledgeManager] = None,
    ):
        self._market_data = market_data or MarketDataService()
        self._knowledge = knowledge

    def compute_value_score(
        self,
        user_query: str,
        tickers: Optional[list[str]] = None,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """按价值投资框架计算个股/市场的基本面得分。

        适用于: 中长线价值投资者、需要研报和基本面分析时。
        不适合: 日内短线交易、打板题材。

        数据来源: KnowledgeManager → market_terms + market_narratives

        Returns:
            { score: float, signals: [dict], summary: str, fundamentals: dict }
        """
        # 实现要点:
        # 1. 从 shared.knowledge 检索术语定义和叙事上下文
        # 2. 从 shared.market_data 拉取 PE/PB/ROE 等基本面数据
        # 3. 综合打分（0.0-1.0），生成多维度信号
        # 4. 返回结构化纯数据，不含 Persona 包装
        ...

        return {
            "score": 0.0,
            "signals": [],
            "summary": "",
            "fundamentals": {},
        }

    def compute_shortterm_heat(
        self,
        user_query: str,
        tickers: Optional[list[str]] = None,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """计算短期赚钱/亏钱效应得分，输出打板情绪热力。

        适用于: 短线/打板/题材轮动交易者。
        不适合: 价值投资、长线持有。

        数据来源: MarketDataService（直接依赖，高频结构化数据）

        Returns:
            { heat_score: float, flow_analysis: dict, risk_flags: list[str] }
        """
        # 实现要点:
        # 1. 从 shared.market_data 拉取龙虎榜、涨停板、资金流向
        # 2. 计算赚钱效应得分（0.0-1.0，越高越好）
        # 3. 标注风险信号（炸板率、核按钮概率等）
        # 4. 返回结构化纯数据
        ...

        return {
            "heat_score": 0.0,
            "flow_analysis": {},
            "risk_flags": [],
        }
