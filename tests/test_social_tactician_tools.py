"""SocialTacticianTools 单元测试"""

import importlib.util
import sys
import unittest

_spec = importlib.util.spec_from_file_location(
    "social_tactician_tools",
    "mcp-servers/social-tactician/tools.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["social_tactician_tools"] = _mod
_spec.loader.exec_module(_mod)
SocialTacticianTools = _mod.SocialTacticianTools

from shared.types import ToolContext


class TestIceBreakSuggest(unittest.TestCase):

    def setUp(self):
        self.tools = SocialTacticianTools()

    def test_generic_scenario_by_default(self):
        result = self.tools.ice_break_suggest()
        self.assertEqual(result["scenario"], "generic")
        self.assertGreater(len(result["ice_breakers"]), 0)
        self.assertGreater(len(result["topics"]), 0)

    def test_down_market_from_user_input(self):
        ctx = ToolContext(
            session_id="s1",
            user_input="今天又跌了，亏死了",
        )
        result = self.tools.ice_break_suggest(context=ctx)
        self.assertEqual(result["scenario"], "market_down_broad")
        self.assertIn("市场下行", result["scenario_description"])

    def test_up_market_from_user_input(self):
        ctx = ToolContext(
            session_id="s1",
            user_input="今天大涨，赚翻了！",
        )
        result = self.tools.ice_break_suggest(context=ctx)
        self.assertEqual(result["scenario"], "market_up_broad")

    def test_specific_holding_with_tickers(self):
        result = self.tools.ice_break_suggest(
            target_holdings=["600519", "000858"],
        )
        self.assertEqual(result["scenario"], "specific_holding_down")

    def test_returns_market_hooks(self):
        result = self.tools.ice_break_suggest()
        self.assertGreater(len(result["market_hooks"]), 0)
        for hook in result["market_hooks"]:
            self.assertIsInstance(hook, str)

    def test_topics_have_required_fields(self):
        result = self.tools.ice_break_suggest()
        for topic in result["topics"]:
            self.assertIn("subject", topic)
            self.assertIn("angle", topic)
            self.assertIn("market_connection", topic)

    def test_topics_limited_to_3(self):
        result = self.tools.ice_break_suggest()
        self.assertLessEqual(len(result["topics"]), 3)

    def test_no_context_no_crash(self):
        result = self.tools.ice_break_suggest(context=None)
        self.assertIsNotNone(result["scenario"])


class TestDeepTalkSuggest(unittest.TestCase):

    def setUp(self):
        self.tools = SocialTacticianTools()

    def test_known_topic_returns_framework(self):
        for topic in ["投资哲学", "风险认知", "市场周期", "交易心理", "生活平衡"]:
            result = self.tools.deep_talk_suggest(topic=topic)
            self.assertEqual(result["topic"], topic)
            self.assertIn("opener", result["framework"])
            self.assertIn("core_theme", result["framework"])
            self.assertGreater(len(result["discussion_points"]), 0)
            self.assertGreater(len(result["pitfalls"]), 0)

    def test_unknown_topic_falls_back(self):
        result = self.tools.deep_talk_suggest(topic="量子力学")
        self.assertIn(result["topic"], ["交易心理", "投资哲学", "风险认知",
                                         "市场周期", "生活平衡"])

    def test_empty_topic_infers_from_context(self):
        ctx = ToolContext(
            session_id="s1",
            user_input="最近心态崩了，贪婪和恐惧交替",
        )
        result = self.tools.deep_talk_suggest(topic="", context=ctx)
        self.assertEqual(result["topic"], "交易心理")

    def test_empty_topic_and_context_defaults(self):
        result = self.tools.deep_talk_suggest(topic="", context=None)
        self.assertEqual(result["topic"], "交易心理")

    def test_framework_has_all_sections(self):
        result = self.tools.deep_talk_suggest(topic="投资哲学")
        fw = result["framework"]
        for key in ["opener", "bridge", "core_theme", "closer"]:
            self.assertIn(key, fw)
            self.assertGreater(len(fw[key]), 0)

    def test_pitfalls_are_meaningful(self):
        result = self.tools.deep_talk_suggest(topic="风险认知")
        for pitfall in result["pitfalls"]:
            self.assertGreater(len(pitfall), 0)
            self.assertTrue(
                pitfall.startswith("不要") or pitfall.startswith("别再"),
                f"Pitfall 应以 不要 开头: {pitfall}",
            )

    def test_list_topics(self):
        topics = self.tools.list_topics()
        self.assertEqual(len(topics), 5)
        self.assertIn("投资哲学", topics)
        self.assertIn("生活平衡", topics)

    def test_no_context_no_crash(self):
        result = self.tools.deep_talk_suggest(topic="交易心理", context=None)
        self.assertIsNotNone(result["framework"])


if __name__ == "__main__":
    unittest.main()
