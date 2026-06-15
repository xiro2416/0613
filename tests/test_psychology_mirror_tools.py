"""PsychologyMirrorTools 单元测试"""

import importlib
import sys
import unittest

_saved_path = sys.path.copy()
sys.path.insert(0, "mcp-servers/psychology-mirror")
try:
    _mod = importlib.import_module("tools")
    PsychologyMirrorTools = _mod.PsychologyMirrorTools
finally:
    sys.path[:] = _saved_path
    sys.modules.pop("tools", None)

from shared.types import ToolContext, UserProfile


class TestGreedDetect(unittest.TestCase):

    def setUp(self):
        self.tools = PsychologyMirrorTools()

    def test_empty_input_returns_zero(self):
        result = self.tools.greed_detect("")
        self.assertEqual(result["greed_index"], 0.0)
        self.assertEqual(len(result["signals"]), 0)

    def test_detect_chase_signal(self):
        result = self.tools.greed_detect("追涨追涨赶紧上车来不及了")
        self.assertGreater(result["greed_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("追涨冲动", categories)

    def test_detect_overconfidence(self):
        result = self.tools.greed_detect("这个票一定涨，肯定赚，绝对没问题")
        self.assertGreater(result["greed_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("过度自信", categories)

    def test_detect_aggressive_position(self):
        result = self.tools.greed_detect("我要满仓梭哈all in干进去")
        self.assertGreater(result["greed_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("仓位激进", categories)

    def test_detect_hold_on(self):
        result = self.tools.greed_detect("不卖不卖，只要不卖就不亏，再等等等回本")
        self.assertGreater(result["greed_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("死扛倾向", categories)

    def test_multiple_signals(self):
        """一句话触发多个信号类别"""
        result = self.tools.greed_detect(
            "满仓干进去，赶紧上车，一定涨，稳了！"
        )
        self.assertGreaterEqual(len(result["signals"]), 2)

    def test_greed_index_capped_at_one(self):
        result = self.tools.greed_detect(
            "追涨追高赶紧上车别踏空来不及了快买冲冲冲 "
            "一定涨肯定赚稳了没问题不可能跌绝对百分之百 "
            "满仓梭哈all in全仓重仓杠杆借钱"
        )
        self.assertLessEqual(result["greed_index"], 1.0)

    def test_profile_boosts_greed(self):
        ctx = ToolContext(
            session_id="s1", user_input="追涨",
            user_profile=UserProfile(
                user_id="u1",
                risk_tolerance="high",
                consecutive_losses=5,
            ),
        )
        result = self.tools.greed_detect("追涨", context=ctx)
        # 关键词 + 高风险偏好 + 连续亏损 → 显著于 0
        self.assertGreater(result["greed_index"], 0.0)

    def test_returns_boundary(self):
        result = self.tools.greed_detect("追涨")
        self.assertTrue(len(result["suggested_boundary"]) > 0)

    def test_boundary_from_trading_style(self):
        ctx = ToolContext(
            session_id="s1", user_input="追涨",
            user_profile=UserProfile(
                user_id="u1",
                trading_style="短线",
            ),
        )
        result = self.tools.greed_detect("追涨", context=ctx)
        self.assertIn("5%", result["suggested_boundary"])

    def test_boundary_from_custom(self):
        ctx = ToolContext(
            session_id="s1", user_input="追涨",
            user_profile=UserProfile(
                user_id="u1",
                defense_boundary="我自己设的止损线：3%",
            ),
        )
        result = self.tools.greed_detect("追涨", context=ctx)
        self.assertIn("3%", result["suggested_boundary"])

    def test_signals_limited_to_3(self):
        result = self.tools.greed_detect(
            "追涨赶紧上车满仓梭哈一定涨稳了不卖死扛"
        )
        self.assertLessEqual(len(result["signals"]), 3)

    def test_no_context_no_crash(self):
        result = self.tools.greed_detect("稳定持有中", context=None)
        self.assertIsNotNone(result["greed_index"])


class TestFearDetect(unittest.TestCase):

    def setUp(self):
        self.tools = PsychologyMirrorTools()

    def test_empty_input_returns_zero(self):
        result = self.tools.fear_detect("")
        self.assertEqual(result["fear_index"], 0.0)
        self.assertEqual(len(result["signals"]), 0)

    def test_detect_panic_sell(self):
        result = self.tools.fear_detect("受不了了我要割肉清仓跑了不玩了")
        self.assertGreater(result["fear_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("恐慌抛售", categories)

    def test_detect_despair(self):
        result = self.tools.fear_detect("亏死了天天跌撑不住绝望了崩了没救了")
        self.assertGreater(result["fear_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("绝望情绪", categories)

    def test_detect_paralysis(self):
        result = self.tools.fear_detect("不敢买再观望等等看犹豫迷茫看不清")
        self.assertGreater(result["fear_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("决策瘫痪", categories)

    def test_detect_regret(self):
        result = self.tools.fear_detect("后悔早知道要是当初错过了要是卖了就好了")
        self.assertGreater(result["fear_index"], 0.0)
        categories = [s["category"] for s in result["signals"]]
        self.assertIn("后悔反刍", categories)

    def test_fear_index_capped_at_one(self):
        result = self.tools.fear_detect(
            "割肉清仓跑了不玩了受不了了 "
            "亏死了天天跌撑不住绝望崩了没救了 "
            "不敢买再观望犹豫迷茫看不清 "
            "后悔早知道要是当初错过了"
        )
        self.assertLessEqual(result["fear_index"], 1.0)

    def test_loss_streak_boosts_fear(self):
        ctx = ToolContext(
            session_id="s1", user_input="亏死了",
            user_profile=UserProfile(
                user_id="u1",
                consecutive_losses=7,
                psychological_state="焦虑",
            ),
        )
        result = self.tools.fear_detect("亏死了", context=ctx)
        self.assertGreater(result["fear_index"], 0.0)

    def test_high_fear_suggests_pause(self):
        ctx = ToolContext(
            session_id="s1", user_input="恐慌",
            user_profile=UserProfile(
                user_id="u1",
                consecutive_losses=7,
                psychological_state="绝望",
            ),
        )
        # 同时触发恐慌抛售 + 绝望情绪 + 决策瘫痪 → 极高恐惧
        result = self.tools.fear_detect(
            "割肉清仓跑了不玩了受不了了全卖了出场 "
            "亏死了天天跌撑不住绝望崩了没救了 "
            "不敢买再观望犹豫迷茫看不清",
            context=ctx,
        )
        self.assertIn("暂停交易", result["suggested_action"])

    def test_low_fear_suggests_calm(self):
        result = self.tools.fear_detect("今天市场还行，继续持有")
        self.assertIn("平稳", result["suggested_action"])

    def test_no_context_no_crash(self):
        result = self.tools.fear_detect("有点担心", context=None)
        self.assertIsNotNone(result["fear_index"])

    def test_neutral_text_returns_low_fear(self):
        result = self.tools.fear_detect("看看今天的行情怎么样")
        self.assertLessEqual(result["fear_index"], 0.1)


if __name__ == "__main__":
    unittest.main()
