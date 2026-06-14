"""
shared/knowledge/ — 非结构化文本知识检索。

提供统一的知识查询接口，支持 Grep / RAG / Hybrid 三种检索后端。
所有业务 MCP Server 在自己的进程中 import 此库，实例互相独立。
"""
from shared.knowledge.manager import KnowledgeManager
from shared.knowledge.retriever import GrepRetriever, HybridRetriever, KnowledgeRetriever, RAGRetriever

__all__ = [
    "KnowledgeManager",
    "KnowledgeRetriever",
    "GrepRetriever",
    "RAGRetriever",
    "HybridRetriever",
]
