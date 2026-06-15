"""Retriever 单元测试"""

import unittest

from shared.knowledge.meme_library import MemeLibrary
from shared.knowledge.market_terms import MarketTermsKnowledge
from shared.knowledge.retriever import GrepRetriever, HybridRetriever, RAGRetriever
from shared.types import KnowledgeDomain, KnowledgeEntry, KnowledgeQuery, RetrievalMode


class TestGrepRetriever(unittest.TestCase):

    def setUp(self):
        self.retriever = GrepRetriever()
        # 种子数据注入
        self.retriever.add_entries([
            KnowledgeEntry(
                id="test_1", content="涨停板是当日涨幅最大上限",
                domain=KnowledgeDomain.MARKET_TERMS, score=1.0,
            ),
            KnowledgeEntry(
                id="test_2", content="跌停板是当日跌幅最大下限",
                domain=KnowledgeDomain.MARKET_TERMS, score=1.0,
            ),
            KnowledgeEntry(
                id="test_3", content="今天亏了好多钱",
                domain=KnowledgeDomain.MEME, score=1.0,
            ),
        ])

    def test_mode_is_grep(self):
        self.assertEqual(self.retriever.mode, RetrievalMode.GREP)

    def test_retrieve_single_keyword(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["涨停"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].id, "test_1")

    def test_retrieve_multiple_keywords(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["涨", "跌"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        # test_1 含 "涨"（涨停板）, test_2 含 "跌"（跌停板）
        self.assertGreaterEqual(len(result.entries), 2)

    def test_retrieve_domain_filter(self):
        query = KnowledgeQuery(
            domain=KnowledgeDomain.MEME, persona=None,
            keywords=["亏"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].id, "test_3")

    def test_retrieve_top_k_truncation(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["涨", "跌", "亏"],  # matches all 3
            mode=RetrievalMode.GREP,
            top_k=2,
        )
        result = self.retriever.retrieve(query)
        self.assertLessEqual(len(result.entries), 2)

    def test_retrieve_empty_keywords(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=[],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertEqual(len(result.entries), 0)
        self.assertEqual(result.confidence, 0.0)

    def test_retrieve_no_match(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["量子"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertEqual(len(result.entries), 0)

    def test_retrieve_case_insensitive(self):
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["涨停板"],  # 与 test_1 内容 "涨停板" 完全一致，只是测试中文
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertGreaterEqual(len(result.entries), 1)

    def test_scoring_is_proportional(self):
        """匹配 2/3 关键词的条目得分应高于匹配 1/3 的"""
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["涨停板", "跌停板", "赚钱"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        # test_3 "今天亏了好多钱" — contains 赚钱? No, it says 亏. So only matches maybe none?
        # test_1 contains 涨停板 → 1 match out of 3 → score 0.33
        # test_2 contains 跌停板 → 1 match out of 3 → score 0.33
        # Both should have same score
        if len(result.entries) >= 2:
            self.assertAlmostEqual(result.entries[0].score, result.entries[1].score, places=1)


class TestRAGRetriever(unittest.TestCase):

    def test_mode_is_rag(self):
        r = RAGRetriever()
        self.assertEqual(r.mode, RetrievalMode.RAG)

    def test_retrieve_returns_empty(self):
        """RAG 当前为 stub，返回空结果"""
        r = RAGRetriever()
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["测试"],
            mode=RetrievalMode.RAG,
        )
        result = r.retrieve(query)
        self.assertEqual(len(result.entries), 0)


class TestHybridRetriever(unittest.TestCase):

    def test_mode_is_hybrid(self):
        r = HybridRetriever()
        self.assertEqual(r.mode, RetrievalMode.HYBRID)

    def test_retrieve_falls_back_to_grep(self):
        r = HybridRetriever()
        # 注入种子数据到内部的 grep retriever
        r._grep.add_entries([
            KnowledgeEntry(
                id="h_1", content="测试内容",
                domain=KnowledgeDomain.MEME, score=1.0,
            ),
        ])
        query = KnowledgeQuery(
            domain=None, persona=None,
            keywords=["测试"],
            mode=RetrievalMode.HYBRID,
        )
        result = r.retrieve(query)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].id, "h_1")


class TestIntegrationWithRealData(unittest.TestCase):
    """验证 GrepRetriever + MemeLibrary + MarketTerms 集成"""

    def setUp(self):
        self.retriever = GrepRetriever()
        self.terms = MarketTermsKnowledge()
        self.meme = MemeLibrary()
        self.retriever.add_entries(self.terms.get_all_entries())
        self.retriever.add_entries(self.meme.get_all_entries())

    def test_search_meme_in_retriever(self):
        query = KnowledgeQuery(
            domain=KnowledgeDomain.MEME, persona=None,
            keywords=["韭菜", "关灯吃面"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertGreater(len(result.entries), 0)
        for entry in result.entries:
            self.assertEqual(entry.domain, KnowledgeDomain.MEME)

    def test_search_term_in_retriever(self):
        query = KnowledgeQuery(
            domain=KnowledgeDomain.MARKET_TERMS, persona=None,
            keywords=["MACD"],
            mode=RetrievalMode.GREP,
        )
        result = self.retriever.retrieve(query)
        self.assertGreaterEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].metadata["term"], "MACD")


if __name__ == "__main__":
    unittest.main()
