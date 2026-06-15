"""MemoryStore 单元测试 — 使用 :memory: SQLite 隔离测试"""

import unittest
from datetime import datetime
from unittest.mock import patch

from shared.memory.store import MemoryStore
from shared.types import EmotionTag, Message, PersonaType


class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        self.store = MemoryStore(":memory:")

    # ── User Profile ──────────────────────────────

    def test_create_user_profile(self):
        profile = self.store.create_user_profile("user_001")
        self.assertEqual(profile.user_id, "user_001")
        self.assertEqual(profile.holdings, [])
        self.assertEqual(profile.trading_style, "")
        self.assertEqual(profile.risk_tolerance, "")
        self.assertEqual(profile.psychological_state, "")
        self.assertEqual(profile.defense_boundary, "")
        self.assertEqual(profile.consecutive_losses, 0)
        self.assertIsInstance(profile.created_at, datetime)
        self.assertIsInstance(profile.updated_at, datetime)

    def test_get_user_profile_exists(self):
        self.store.create_user_profile("user_001")
        profile = self.store.get_user_profile("user_001")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, "user_001")

    def test_get_user_profile_not_exists(self):
        profile = self.store.get_user_profile("nonexistent")
        self.assertIsNone(profile)

    def test_update_user_profile_single_field(self):
        self.store.create_user_profile("user_001")
        updated = self.store.update_user_profile("user_001", {
            "trading_style": "短线",
            "risk_tolerance": "high",
        })
        self.assertEqual(updated.trading_style, "短线")
        self.assertEqual(updated.risk_tolerance, "high")

    def test_update_user_profile_holdings_json(self):
        self.store.create_user_profile("user_001")
        holdings = ["600519", "000858"]
        updated = self.store.update_user_profile("user_001", {
            "holdings": holdings,
        })
        self.assertEqual(updated.holdings, holdings)

    def test_update_user_profile_ignores_unknown_fields(self):
        self.store.create_user_profile("user_001")
        updated = self.store.update_user_profile("user_001", {
            "trading_style": "中长线",
            "nonexistent_field": "should be ignored",
        })
        self.assertEqual(updated.trading_style, "中长线")
        # no error, unknown field silently dropped

    def test_update_user_profile_empty_update(self):
        self.store.create_user_profile("user_001")
        updated = self.store.update_user_profile("user_001", {})
        self.assertIsNotNone(updated)

    def test_update_consecutive_losses(self):
        self.store.create_user_profile("user_001")
        updated = self.store.update_user_profile("user_001", {
            "consecutive_losses": 5,
        })
        self.assertEqual(updated.consecutive_losses, 5)

    # ── Session CRUD ───────────────────────────────

    def test_create_session(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")
        self.assertIsNotNone(session.session_id)
        self.assertEqual(len(session.session_id), 12)
        self.assertEqual(session.user_id, "user_001")
        self.assertEqual(session.active_persona, PersonaType.GENTLE)
        self.assertEqual(session.conversation_history, [])

    def test_get_session_exists(self):
        self.store.create_user_profile("user_001")
        created = self.store.create_session("user_001")
        fetched = self.store.get_session(created.session_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.session_id, created.session_id)

    def test_get_session_not_exists(self):
        session = self.store.get_session("nonexistent")
        self.assertIsNone(session)

    def test_get_session_closed_returns_none(self):
        self.store.create_user_profile("user_001")
        created = self.store.create_session("user_001")
        self.store.close_session(created.session_id)
        fetched = self.store.get_session(created.session_id)
        self.assertIsNone(fetched)

    # ── Messages ───────────────────────────────────

    def test_append_and_load_messages(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")

        msg1 = Message(role="user", content="今天亏了好多", emotion_tag=None)
        msg2 = Message(role="agent", content="别急，慢慢来 ✨", emotion_tag=EmotionTag.COMFORTING)

        self.store.append_message(session.session_id, msg1)
        self.store.append_message(session.session_id, msg2)

        fetched = self.store.get_session(session.session_id)
        self.assertEqual(len(fetched.conversation_history), 2)
        self.assertEqual(fetched.conversation_history[0].role, "user")
        self.assertEqual(fetched.conversation_history[0].content, "今天亏了好多")
        self.assertEqual(fetched.conversation_history[0].emotion_tag, None)
        self.assertEqual(fetched.conversation_history[1].role, "agent")
        self.assertEqual(fetched.conversation_history[1].emotion_tag, EmotionTag.COMFORTING)

    def test_messages_preserve_timestamps(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")

        ts = datetime(2026, 6, 15, 22, 30, 0)
        msg = Message(role="user", content="测试时间", timestamp=ts)
        self.store.append_message(session.session_id, msg)

        fetched = self.store.get_session(session.session_id)
        self.assertEqual(
            fetched.conversation_history[0].timestamp,
            ts,
        )

    # ── Persona / TimeContext ──────────────────────

    def test_set_persona(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")
        self.store.set_persona(session.session_id, "rational")

        fetched = self.store.get_session(session.session_id)
        self.assertEqual(fetched.active_persona, PersonaType.RATIONAL)

    def test_update_time_context(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")
        self.store.update_time_context(session.session_id, "post_market")

        fetched = self.store.get_session(session.session_id)
        self.assertEqual(fetched.time_slot.value, "post_market")

    # ── Close Session ──────────────────────────────

    def test_close_session_marks_inactive(self):
        self.store.create_user_profile("user_001")
        session = self.store.create_session("user_001")
        self.store.close_session(session.session_id)

        # get_session should return None for closed sessions
        closed = self.store.get_session(session.session_id)
        self.assertIsNone(closed)


if __name__ == "__main__":
    unittest.main()
