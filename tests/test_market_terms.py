"""MarketTermsKnowledge 单元测试"""

import unittest

from shared.knowledge.market_terms import MarketTermsKnowledge


class TestMarketTerms(unittest.TestCase):

    def setUp(self):
        self.terms = MarketTermsKnowledge()

    def test_search_exact_term(self):
        result = self.terms.search(["涨停板"])
        self.assertGreaterEqual(len(result.entries), 1)
        top = result.entries[0]
        self.assertIn("涨停板", top.content)
        self.assertEqual(top.metadata["term"], "涨停板")

    def test_search_alias(self):
        """搜索别名应能匹配到正名"""
        result = self.terms.search(["PE"])
        self.assertGreaterEqual(len(result.entries), 1)
        found_pe = False
        for entry in result.entries:
            if "市盈率" in entry.metadata["term"]:
                found_pe = True
                break
        self.assertTrue(found_pe, "搜索 'PE' 应匹配到 '市盈率'")

    def test_search_multiple_keywords(self):
        result = self.terms.search(["涨停", "跌停"])
        self.assertGreaterEqual(len(result.entries), 2)

    def test_search_nonexistent_returns_empty(self):
        result = self.terms.search(["量子缠结股"])
        self.assertEqual(len(result.entries), 0)

    def test_search_empty_keywords(self):
        result = self.terms.search([])
        self.assertEqual(len(result.entries), 0)

    def test_search_returns_up_to_5(self):
        result = self.terms.search(["交易", "分析"])
        self.assertLessEqual(len(result.entries), 5)

    def test_search_slang_term(self):
        """搜索圈层黑话"""
        result = self.terms.search(["关灯吃面"])
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].metadata["term"], "关灯吃面")
        self.assertIn("重庆啤酒", result.entries[0].content)

    def test_search_case_insensitive(self):
        """搜索忽略大小写"""
        result = self.terms.search(["macd"])
        self.assertGreaterEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].metadata["term"], "MACD")

    def test_get_all_entries(self):
        entries = self.terms.get_all_entries()
        self.assertEqual(len(entries), 50)
        for entry in entries:
            self.assertIsNotNone(entry.id)
            self.assertIsNotNone(entry.content)

    def test_category_coverage(self):
        """四类术语都应存在"""
        entries = self.terms.get_all_entries()
        categories = {e.metadata["category"] for e in entries}
        expected = {"基础交易", "圈层黑话", "策略术语", "技术分析"}
        self.assertEqual(categories, expected)


if __name__ == "__main__":
    unittest.main()
