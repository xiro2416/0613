"""MemeComfortTools 单元测试"""

import importlib.util
import sys
import unittest

_spec = importlib.util.spec_from_file_location(
    "meme_comfort_tools",
    "mcp-servers/meme-comfort/tools.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["meme_comfort_tools"] = _mod
_spec.loader.exec_module(_mod)
MemeComfortTools = _mod.MemeComfortTools


class TestLossMemePick(unittest.TestCase):

    def setUp(self):
        self.tools = MemeComfortTools()

    def test_mild_returns_memes(self):
        result = self.tools.loss_meme_pick("mild")
        self.assertGreater(len(result["memes"]), 0)
        self.assertEqual(result["matched_scenario"], "mild")

    def test_moderate_returns_memes(self):
        result = self.tools.loss_meme_pick("moderate")
        self.assertGreater(len(result["memes"]), 0)

    def test_severe_returns_memes(self):
        result = self.tools.loss_meme_pick("severe")
        self.assertGreater(len(result["memes"]), 0)

    def test_any_returns_up_to_5(self):
        result = self.tools.loss_meme_pick("any")
        self.assertLessEqual(len(result["memes"]), 5)
        self.assertGreater(len(result["memes"]), 0)

    def test_invalid_level_defaults_to_any(self):
        result = self.tools.loss_meme_pick("extreme")
        # 回退到 any → 应有结果
        self.assertGreater(len(result["memes"]), 0)
        self.assertEqual(result["matched_scenario"], "any")

    def test_each_meme_has_required_fields(self):
        result = self.tools.loss_meme_pick("any")
        for meme in result["memes"]:
            self.assertIn("id", meme)
            self.assertIn("text", meme)
            self.assertIn("loss_level", meme)
            self.assertIn("tags", meme)
            self.assertIn("source", meme)

    def test_total_available_matches_memes_count(self):
        result = self.tools.loss_meme_pick("moderate")
        self.assertEqual(result["total_available"], len(result["memes"]))


class TestEmoDetoxPick(unittest.TestCase):

    def setUp(self):
        self.tools = MemeComfortTools()

    def test_loss_trigger(self):
        result = self.tools.emo_detox_pick("loss")
        self.assertEqual(len(result["detox_items"]), 3)
        self.assertEqual(result["matched_trigger"], "loss")
        self.assertEqual(result["label"], "亏损情绪化解")

    def test_fomo_trigger(self):
        result = self.tools.emo_detox_pick("fomo")
        self.assertEqual(len(result["detox_items"]), 3)
        self.assertEqual(result["label"], "踏空焦虑化解")

    def test_lonely_trigger(self):
        result = self.tools.emo_detox_pick("lonely")
        self.assertEqual(len(result["detox_items"]), 3)

    def test_tired_trigger(self):
        result = self.tools.emo_detox_pick("tired")
        self.assertEqual(len(result["detox_items"]), 3)

    def test_empty_trigger_returns_overview(self):
        result = self.tools.emo_detox_pick("")
        self.assertEqual(len(result["detox_items"]), 0)
        self.assertEqual(result["matched_trigger"], "")
        self.assertIn("available_triggers", result)
        self.assertEqual(len(result["available_triggers"]), 4)

    def test_invalid_trigger_returns_overview(self):
        result = self.tools.emo_detox_pick("angry")
        self.assertEqual(result["matched_trigger"], "")
        self.assertIn("available_triggers", result)

    def test_each_detox_item_has_type_and_content(self):
        for trigger in ["loss", "fomo", "lonely", "tired"]:
            result = self.tools.emo_detox_pick(trigger)
            for item in result["detox_items"]:
                self.assertIn("type", item)
                self.assertIn("content", item)
                self.assertGreater(len(item["content"]), 0)

    def test_detox_types_coverage(self):
        """每个 trigger 应包含 心理事实 + 行动建议 + 视角转换/陪伴提示"""
        result = self.tools.emo_detox_pick("loss")
        types = {item["type"] for item in result["detox_items"]}
        self.assertIn("心理事实", types)
        self.assertIn("行动建议", types)


if __name__ == "__main__":
    unittest.main()
