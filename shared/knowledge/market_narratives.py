"""市场历史叙事知识 — 文本化市场周期/范式信息。

存储高度抽象的市场叙事，如:
  - "2021年是光伏大牛市"
  - "2026年是AI大牛市"
非实时量化数据，不消费 shared/market_data。
"""

from shared.types import KnowledgeEntry, KnowledgeResult


class MarketNarrativesKnowledge:
    """市场历史叙事库"""

    def search(self, keywords: list[str]) -> KnowledgeResult:
        """按关键词检索市场叙事

        实现要点:
          - 维护叙事语料索引（按行业、周期、事件标注）
          - 关键词匹配 + 语义扩展
          - 返回匹配的叙事条目
        """
        ...
        return KnowledgeResult()
