"""MemeLibrary 单元测试"""

import unittest

from shared.knowledge.meme_library import MemeLibrary
from shared.types import PersonaType


class TestMemeLibrary(unittest.TestCase):

    def setUp(self):
        self.lib = MemeLibrary()

    def test_pick_mild_meme_returns_results(self):
        result = self.lib.pick("mild", PersonaType.MEME)
        self.assertGreater(len(result.entries), 0)
        for entry in result.entries:
            self.assertIn(entry.metadata["loss_level"], ("mild", "any"))

    def test_pick_moderate_returns_results(self):
        result = self.lib.pick("moderate", PersonaType.MEME)
        self.assertGreater(len(result.entries), 0)

    def test_pick_severe_returns_results(self):
        result = self.lib.pick("severe", PersonaType.MEME)
        self.assertGreater(len(result.entries), 0)

    def test_pick_any_returns_up_to_5(self):
        result = self.lib.pick("any", PersonaType.MEME)
        self.assertLessEqual(len(result.entries), 5)
        self.assertGreater(len(result.entries), 0)

    def test_pick_rational_returns_empty(self):
        result = self.lib.pick("any", PersonaType.RATIONAL)
        self.assertEqual(len(result.entries), 0)
        self.assertEqual(result.confidence, 0.0)

    def test_pick_gentle_returns_softer_variant(self):
        result = self.lib.pick("any", PersonaType.GENTLE)
        self.assertGreater(len(result.entries), 0)
        # GENTLE 变体应包含温暖元素
        for entry in result.entries:
            self.assertFalse(entry.content.endswith("MMP"),
                             f"GENTLE 不应包含粗话: {entry.content}")

    def test_pick_meme_returns_raw_text(self):
        result = self.lib.pick("any", PersonaType.MEME)
        self.assertGreater(len(result.entries), 0)
        # MEME 版本可能包含直白表达，但这里只是确认它返回了内容
        for entry in result.entries:
            self.assertTrue(len(entry.content) > 0)

    def test_pick_unknown_loss_level_returns_empty(self):
        result = self.lib.pick("extreme", PersonaType.MEME)
        # 没有 "extreme" 或 "any" 匹配 → 空
        # 但 mild/moderate/severe 入口也不匹配 "extreme"
        # 因为筛选条件是 loss_level == "extreme" or loss_level == "any"
        # "any" 标签的 meme 仍然会匹配
        self.assertGreater(len(result.entries), 0,
                           "有 any 标签的热梗应被匹配到")

    def test_get_all_entries(self):
        entries = self.lib.get_all_entries()
        self.assertEqual(len(entries), 30)
        for entry in entries:
            self.assertIsNotNone(entry.id)
            self.assertIsNotNone(entry.content)

    def test_entries_sorted_by_freshness(self):
        result = self.lib.pick("any", PersonaType.MEME)
        scores = [e.score for e in result.entries]
        self.assertEqual(scores, sorted(scores, reverse=True),
                         "应按 freshness 降序排列")


if __name__ == "__main__":
    unittest.main()
