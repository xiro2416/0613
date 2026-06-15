"""LifeServiceTools 单元测试"""

import importlib.util
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

# mcp-servers 含连字符，用 spec_from_file_location 以唯一模块名加载
_spec = importlib.util.spec_from_file_location(
    "life_service_tools",
    "mcp-servers/life-service/tools.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["life_service_tools"] = _mod
_spec.loader.exec_module(_mod)
LifeServiceTools = _mod.LifeServiceTools

from shared.types import ToolContext, UserProfile


class TestFatigueSuggest(unittest.TestCase):

    def setUp(self):
        self.tools = LifeServiceTools()

    def _mock_now(self, hour: int):
        return datetime(2026, 6, 15, hour, 30, 0)

    def test_late_night_fatigue(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(1)
            result = self.tools.fatigue_suggest()
            self.assertEqual(result["triggered_by"], "深夜复盘疲劳")

    def test_post_market_fatigue(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest()
            self.assertEqual(result["triggered_by"], "盘后分析疲劳")

    def test_trading_hours_fatigue(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(10)
            result = self.tools.fatigue_suggest()
            self.assertEqual(result["triggered_by"], "盘中盯盘疲劳")

    def test_daytime_fatigue(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(7)
            result = self.tools.fatigue_suggest()
            self.assertEqual(result["triggered_by"], "日常疲劳")

    def test_returns_service_cards(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest()
            self.assertGreater(len(result["services"]), 0)
            self.assertGreater(len(result["action_cards"]), 0)

    def test_each_service_has_required_fields(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest()
            for svc in result["services"]:
                self.assertIn("name", svc)
                self.assertIn("type", svc)
                self.assertIn("delivery_time", svc)

    def test_each_action_card_has_required_fields(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest()
            for card in result["action_cards"]:
                self.assertIn("action_type", card)
                self.assertIn("display_text", card)
                self.assertIn("service_name", card)

    def test_escalation_on_loss_streak(self):
        ctx = ToolContext(
            session_id="s1",
            user_input="好累",
            user_profile=UserProfile(
                user_id="u1",
                consecutive_losses=5,
            ),
        )
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest(context=ctx)
            self.assertIn("连续亏损", result["escalation"])

    def test_no_escalation_without_context(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(20)
            result = self.tools.fatigue_suggest(context=None)
            self.assertEqual(result["escalation"], "")


class TestLateNightCare(unittest.TestCase):

    def setUp(self):
        self.tools = LifeServiceTools()

    def _mock_now(self, hour: int):
        return datetime(2026, 6, 15, hour, 30, 0)

    def test_triggers_at_midnight(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(1)
            result = self.tools.late_night_care()
            self.assertGreater(len(result["care_items"]), 0)
            self.assertLess(result["wellness_score"], 1.0)

    def test_triggers_at_23(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(23)
            result = self.tools.late_night_care()
            self.assertGreater(len(result["care_items"]), 0)

    def test_silent_during_day(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(14)
            result = self.tools.late_night_care()
            self.assertEqual(len(result["care_items"]), 0)
            self.assertEqual(result["wellness_score"], 1.0)

    def test_deep_night_lower_wellness(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(3)
            result1 = self.tools.late_night_care()

        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(23)
            result2 = self.tools.late_night_care()

        self.assertLess(result1["wellness_score"], result2["wellness_score"])

    def test_more_care_when_lower_wellness(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(2)
            result = self.tools.late_night_care()
            self.assertGreaterEqual(len(result["care_items"]), 1)

    def test_consecutive_losses_lower_wellness(self):
        ctx = ToolContext(
            session_id="s1",
            user_input="睡不着",
            user_profile=UserProfile(
                user_id="u1",
                consecutive_losses=7,
                psychological_state="焦虑",
            ),
        )
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(1)
            result = self.tools.late_night_care(context=ctx)
            self.assertLess(result["wellness_score"], 0.2)

    def test_returns_suggestions(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(1)
            result = self.tools.late_night_care()
            self.assertGreater(len(result["suggestions"]), 0)

    def test_wellness_score_range(self):
        with patch("life_service_tools.datetime") as mock_dt:
            mock_dt.now.return_value = self._mock_now(3)
            result = self.tools.late_night_care()
            self.assertGreaterEqual(result["wellness_score"], 0.0)
            self.assertLessEqual(result["wellness_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
