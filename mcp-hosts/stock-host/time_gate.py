"""时间门控 — Context Feature Provider。

职责: 提供 A 股当前时间特征，供 Host 注入 system_prompt。

不再拒绝盘中响应，而是通过时间特征动态切换 Prompt:
  - TRADING_HOURS  → "专心看盘，收盘后陪你复盘"
  - POST_MARKET    → 全量激活所有业务路由
  - WEEKEND_HOLIDAY → 全量激活，陪伴式回应

门控参数化:
  - 对接中国A股交易日历（周末 + 法定节假日判定）
  - 实时输出时间特征
"""

from datetime import datetime

from shared.types import TimeFeature, TimeSlot


# 中国A股法定节假日（2026年，后续应对接交易日历 API）
_CHINA_HOLIDAYS_2026: set[tuple[int, int]] = {
    (1, 1), (1, 2), (1, 3),           # 元旦
    (2, 15), (2, 16), (2, 17),         # 春节
    (2, 18), (2, 19), (2, 20), (2, 21),
    (4, 4), (4, 5), (4, 6),            # 清明节
    (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),  # 劳动节
    (6, 12), (6, 13), (6, 14),         # 端午节
    (9, 15), (9, 16), (9, 17),         # 中秋节
    (10, 1), (10, 2), (10, 3), (10, 4),  # 国庆节
    (10, 5), (10, 6), (10, 7), (10, 8),
}

# A 股交易时间
_TRADING_START_HOUR = 9
_TRADING_START_MINUTE = 15
_TRADING_END_HOUR = 15
_TRADING_END_MINUTE = 0


class TimeGate:
    """时间门控 — Context Feature Provider"""

    def get_time_features(self, now: datetime) -> TimeFeature:
        """获取完整时间特征（主入口）

        返回值供 Host 注入 system_prompt:
          - TRADING_HOURS  → Prompt 提示"盘中专注，盘后复盘"
          - POST_MARKET    → 全量激活
          - WEEKEND_HOLIDAY → 全量激活
        """
        time_slot = self._determine_time_slot(now)
        is_trading_day = self._is_trading_day(now)

        return TimeFeature(
            time_slot=time_slot,
            is_trading_day=is_trading_day,
            market_status=self._market_status(now, time_slot),
            next_open_time=self._next_open_time(now),
            next_action_hint=self._next_action_hint(now, time_slot),
        )

    def is_active(self, now: datetime) -> bool:
        """系统是否应全量激活"""
        slot = self._determine_time_slot(now)
        return slot != TimeSlot.TRADING_HOURS

    # ── 内部 ──────────────────────────────────

    def _determine_time_slot(self, now: datetime) -> TimeSlot:
        if not self._is_trading_day(now):
            return TimeSlot.WEEKEND_HOLIDAY

        minutes = now.hour * 60 + now.minute
        open_mins = _TRADING_START_HOUR * 60 + _TRADING_START_MINUTE
        close_mins = _TRADING_END_HOUR * 60 + _TRADING_END_MINUTE

        if open_mins <= minutes < close_mins:
            return TimeSlot.TRADING_HOURS
        elif minutes >= close_mins:
            return TimeSlot.POST_MARKET
        else:
            return TimeSlot.POST_MARKET  # 盘前算盘后

    def _is_trading_day(self, now: datetime) -> bool:
        if now.weekday() >= 5:  # 周六/日
            return False
        if (now.month, now.day) in _CHINA_HOLIDAYS_2026:
            return False
        return True

    def _market_status(self, now: datetime, time_slot: TimeSlot) -> str:
        status_map = {
            TimeSlot.TRADING_HOURS: "盘中交易",
            TimeSlot.POST_MARKET: "盘后休市",
            TimeSlot.WEEKEND_HOLIDAY: "节假日休市",
            TimeSlot.UNKNOWN: "未知",
        }
        return status_map.get(time_slot, "未知")

    def _next_open_time(self, now: datetime) -> str:
        # 简化版: 找下一个交易日的 9:15
        from datetime import timedelta

        cursor = now.replace(hour=9, minute=15, second=0, microsecond=0)
        if now >= cursor:
            cursor += timedelta(days=1)
        while not self._is_trading_day(cursor):
            cursor += timedelta(days=1)
        return cursor.isoformat()

    def _next_action_hint(self, now: datetime, time_slot: TimeSlot) -> str:
        if time_slot == TimeSlot.TRADING_HOURS:
            return "专心看盘，盘后帮你复盘"
        elif time_slot == TimeSlot.POST_MARKET:
            return "盘后时间，尽情复盘和放松"
        else:
            return "休市期间，好好休息"
