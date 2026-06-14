"""
检索后端抽象 — Grep / RAG / Hybrid 可插拔。

切换检索方式只需替换 Retriever 实现，
KnowledgeManager 调用方代码不变。
"""

from abc import ABC, abstractmethod

from shared.types import KnowledgeQuery, KnowledgeResult, RetrievalMode


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
    """关键词精确匹配检索器 — MVP 默认后端"""

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.GREP

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """关键词精确匹配

        实现要点:
          - 对 query.keywords 做倒排索引匹配
          - 支持同义词扩展（如 "打板" ↔ "涨停板"）
          - 按匹配度排序，取 top_k
        """
        ...


class RAGRetriever(KnowledgeRetriever):
    """语义向量检索器 — 升级路径"""

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.RAG

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """向量语义检索

        实现要点:
          - query.query → embedding → 向量库搜索
          - 兼容 Chroma / Pinecone / 自建向量库
          - top_k 条结果返回
        """
        ...


class HybridRetriever(KnowledgeRetriever):
    """混合检索器 — Grep 初筛 + RAG 精排"""

    @property
    def mode(self) -> RetrievalMode:
        return RetrievalMode.HYBRID

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Grep 粗筛 → RAG 精排

        实现要点:
          - 先用 Grep 快速召回候选集 (top_k * 3)
          - 再用 RAG 语义精排，返回 top_k
        """
        ...
