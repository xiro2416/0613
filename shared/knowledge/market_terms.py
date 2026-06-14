"""交易术语库 — 市场概念与术语解释。

覆盖:
  - 基础术语: 涨停/跌停/打板/超短/波段/龙头...
  - 圈层黑话: 核按钮/天地板/地天板/核武器...
  - 策略术语: 价值投资/成长投资/趋势跟踪/均值回归...
"""

from shared.types import KnowledgeEntry, KnowledgeResult


class MarketTermsKnowledge:
    """交易术语知识库"""

    def search(self, keywords: list[str]) -> KnowledgeResult:
        """查术语定义

        实现要点:
          - 术语 → 定义映射表
          - 支持模糊匹配和同义词
          - 返回最相关的 top_k 条
        """
        ...
        return KnowledgeResult()
