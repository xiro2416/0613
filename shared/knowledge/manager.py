"""
KnowledgeManager — 知识库统一入口。

职责:
  - 管理多个 KnowledgeRetriever（每种 RetrievalMode 一个）
  - 按 KnowledgeDomain 路由到对应的知识域
  - 提供领域快捷查询方法

拓扑隔离协定:
  KnowledgeManager 仅处理非结构化文本检索:
    - MARKET_NARRATIVES → 市场周期/范式叙事
    - MARKET_TERMS     → 交易术语/市场概念
    - MEME             → 热梗语料库
  高频结构化行情数据由 shared/market_data/ 直接消费，不经过此入口。
"""

from shared.knowledge.market_narratives import MarketNarrativesKnowledge
from shared.knowledge.market_terms import MarketTermsKnowledge
from shared.knowledge.meme_library import MemeLibrary
from shared.knowledge.retriever import KnowledgeRetriever
from shared.types import KnowledgeDomain, KnowledgeQuery, KnowledgeResult, PersonaType, RetrievalMode


class KnowledgeManager:
    """知识库统一入口"""

    def __init__(self, retrievers: dict[RetrievalMode, KnowledgeRetriever]):
        """注入检索后端

        Args:
            retrievers: {GREP: GrepRetriever(), RAG: RAGRetriever(), ...}
        """
        self._retrievers = retrievers
        self._narratives = MarketNarrativesKnowledge()
        self._terms = MarketTermsKnowledge()
        self._meme = MemeLibrary()
        # 知识域权重（人设切换时同步更新）
        self._weights: dict[str, float] = {}

        # 向 GrepRetriever 注入语料
        self._seed_retriever()

    def _seed_retriever(self) -> None:
        """从各 domain class 导出 entries 注入 GrepRetriever。"""
        grep = self._retrievers.get(RetrievalMode.GREP)
        if grep is None or not hasattr(grep, "add_entries"):
            return
        grep.add_entries(self._terms.get_all_entries())
        grep.add_entries(self._meme.get_all_entries())

    # ── 通用查询 ──────────────────────────────

    def query(self, query: KnowledgeQuery) -> KnowledgeResult:
        """通用知识查询 — 按 query.mode 选择 retriever"""
        retriever = self._retrievers.get(query.mode)
        if retriever is None:
            # 回退到第一个可用检索器
            retriever = next(iter(self._retrievers.values()))
        return retriever.retrieve(query)

    # ── 领域快捷方法 ───────────────────────────

    def get_market_narratives(self, keywords: list[str]) -> KnowledgeResult:
        """检索市场历史叙事（纯文本，高度抽象）"""
        return self._narratives.search(keywords)

    def get_market_terms(self, keywords: list[str]) -> KnowledgeResult:
        """查交易术语"""
        return self._terms.search(keywords)

    def get_meme(self, loss_level: str, persona: PersonaType) -> KnowledgeResult:
        """按亏损程度 + 人设取热梗"""
        return self._meme.pick(loss_level, persona)

    # ── 权重同步 ──────────────────────────────

    def sync_weights(self, weights: dict[str, float]) -> None:
        """人设切换时同步知识域权重"""
        self._weights.update(weights)
