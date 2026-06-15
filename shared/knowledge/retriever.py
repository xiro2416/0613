"""
检索后端 — Grep / RAG / Hybrid 可插拔。

切换检索方式只需替换 Retriever 实现，
KnowledgeManager 调用方代码不变。

MVP: GrepRetriever 已实现（关键词精确匹配）。
升级路径: RAGRetriever / HybridRetriever 保持 stub。
"""

from abc import ABC, abstractmethod

from shared.types import KnowledgeEntry, KnowledgeQuery, KnowledgeResult, RetrievalMode


class KnowledgeRetriever(ABC):
    """检索后端基类"""

    @property
    @abstractmethod
    def mode(self) -> RetrievalMode:
        """返回检索模式标识"""
        ...

    @abstractmethod
    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """执行检索"""
        ...


class GrepRetriever(KnowledgeRetriever):
    """关键词精确匹配检索器 — MVP 默认后端。

    KnowledgeManager 在初始化时通过 add_entries() 注入来自
    各 domain class (market_terms / meme_library) 的 KnowledgeEntry，
    然后按 query.keywords 做关键词计分匹配。
    """

    def __init__(self):
        self._corpus: list[KnowledgeEntry] = []

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.GREP

    def add_entries(self, entries: list[KnowledgeEntry]) -> None:
        """批量注入语料条目"""
        self._corpus.extend(entries)

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """关键词精确匹配检索。

        1. Domain 过滤（如果 query.domain 指定了）
        2. 按 keywords 对 corpus 中每条 entry 计分
        3. 按分数降序，取 top_k
        """
        keywords = query.keywords
        if not keywords:
            return KnowledgeResult(
                entries=[],
                confidence=0.0,
                source_domain=query.domain,
                retrieval_mode=RetrievalMode.GREP,
            )

        scored = []
        for entry in self._corpus:
            # Domain 过滤
            if query.domain is not None and entry.domain != query.domain:
                continue

            score = self._score(keywords, entry.content)
            if score > 0:
                entry.score = score
                scored.append(entry)

        scored.sort(key=lambda e: e.score, reverse=True)
        top = scored[:query.top_k]

        avg_score = sum(e.score for e in top) / len(top) if top else 0.0
        return KnowledgeResult(
            entries=top,
            confidence=avg_score,
            source_domain=query.domain,
            retrieval_mode=RetrievalMode.GREP,
        )

    @staticmethod
    def _score(keywords: list[str], text: str) -> float:
        """计算关键词命中率（0.0 ~ 1.0）。"""
        text_lower = text.lower()
        matches = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                matches += 1
        return matches / len(keywords)


class RAGRetriever(KnowledgeRetriever):
    """语义向量检索器 — 升级路径（当前 stub）"""

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.RAG

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """向量语义检索

        未来实现:
          - query.query → embedding → 向量库搜索
          - 兼容 Chroma / Pinecone / pgvector
        """
        return KnowledgeResult(
            entries=[],
            confidence=0.0,
            source_domain=query.domain,
            retrieval_mode=RetrievalMode.RAG,
        )


class HybridRetriever(KnowledgeRetriever):
    """混合检索器 — Grep 初筛 + RAG 精排（当前 stub）"""

    def __init__(self):
        self._grep = GrepRetriever()

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.HYBRID

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Grep 粗筛 → RAG 精排

        未来实现:
          - 先用 Grep 快速召回候选集 (top_k * 3)
          - 再用 RAG 语义精排，返回 top_k
        """
        # MVP: 回退到纯 grep
        return self._grep.retrieve(query)
