"""
life-service 工具实现 — 生活服务 Skills 连接器。

工具返回纯数据（不含 Persona 色彩）。

核心定位: 高压决策后的生理补给站、认知无载荷行动链。
MVP 阶段适配瑞幸咖啡等补给场景。
"""

from datetime import datetime

from shared.types import ToolContext


# ── 疲劳类型 → 服务卡片模板 ──────────────────────

_FATIGUE_SERVICES: dict[str, list[dict]] = {
    "深夜复盘疲劳": [
        {"name": "热牛奶助眠", "type": "饮品", "delivery_time": "15分钟", "estimated_cost": 15,
         "description": "温热牛奶，帮助身心放松，自然入眠"},
        {"name": "睡眠引导音频", "type": "健康", "delivery_time": "即时", "estimated_cost": 0,
         "description": "10分钟冥想引导，缓解交易焦虑"},
        {"name": "明日盘前提醒", "type": "工具", "delivery_time": "定时", "estimated_cost": 0,
         "description": "设定明早 8:30 推送盘前资讯 + 策略提醒"},
    ],
    "盘后分析疲劳": [
        {"name": "瑞幸咖啡提神", "type": "饮品", "delivery_time": "30分钟", "estimated_cost": 18,
         "description": "生椰拿铁 / 美式咖啡，提神醒脑，继续战斗"},
        {"name": "肩颈放松操", "type": "健康", "delivery_time": "即时", "estimated_cost": 0,
         "description": "5分钟办公室拉伸，缓解盯盘肩颈压力"},
        {"name": "复盘笔记模板", "type": "工具", "delivery_time": "即时", "estimated_cost": 0,
         "description": "结构化复盘模板：今日操作回顾 + 情绪记录 + 明日计划"},
    ],
    "盘中盯盘疲劳": [
        {"name": "深呼吸引导", "type": "健康", "delivery_time": "即时", "estimated_cost": 0,
         "description": "5-4-3-2-1 呼吸法，快速恢复决策专注力"},
        {"name": "盯盘姿势提醒", "type": "健康", "delivery_time": "即时", "estimated_cost": 0,
         "description": "调整坐姿、活动手腕、保护腰椎和颈椎"},
        {"name": "水分补给提醒", "type": "饮品", "delivery_time": "即时", "estimated_cost": 0,
         "description": "喝杯水，脱水会降低认知判断能力"},
    ],
    "日常疲劳": [
        {"name": "散步放松", "type": "健康", "delivery_time": "即时", "estimated_cost": 0,
         "description": "出去走15分钟，让大脑切换场景"},
        {"name": "能量小食", "type": "饮品", "delivery_time": "30分钟", "estimated_cost": 20,
         "description": "坚果/水果/酸奶，补充脑力消耗"},
        {"name": "交易日志回顾", "type": "工具", "delivery_time": "即时", "estimated_cost": 0,
         "description": "回顾本周交易记录，客观评估决策质量"},
    ],
}

# ── 深夜关怀项 ───────────────────────────────────

_CARE_ITEMS: list[dict] = [
    {"type": "睡眠提醒", "content": "已经凌晨了，明天还要看盘呢。放下手机，闭上眼睛休息吧",
     "base_priority": 0.9},
    {"type": "护眼提醒", "content": "长时间盯屏幕对眼睛不好，试试20-20-20法则：每20分钟看20英尺外20秒",
     "base_priority": 0.7},
    {"type": "情绪安抚", "content": "股市有涨有跌，身体才是革命的本钱。先睡个好觉，明天又是新的一天",
     "base_priority": 0.5},
    {"type": "补水提醒", "content": "熬夜脱水会让第二天精神状态更差，喝杯温水吧",
     "base_priority": 0.4},
    {"type": "明日建议", "content": "如果真的睡不着，不如起来用纸笔记下明天的交易计划。写完通常就困了",
     "base_priority": 0.3},
]


class LifeServiceTools:
    """生活服务工具集 — 自包含，无外部依赖"""

    # ── 疲劳检测 ──────────────────────────────────

    def fatigue_suggest(self, context: ToolContext = None) -> dict:
        """为疲劳状态用户推荐补给服务。

        根据当前时间窗口判定疲劳类型，返回匹配的服务卡片。
        无外部依赖，纯时间推断。

        Returns:
            { services: [dict], triggered_by: str, action_cards: [dict] }
        """
        now = datetime.now()
        fatigue_type = self._detect_fatigue(now, context)

        services = _FATIGUE_SERVICES.get(fatigue_type, _FATIGUE_SERVICES["日常疲劳"])

        # 构建 action_cards
        action_cards = []
        for svc in services:
            action_cards.append({
                "action_type": self._action_type(svc["type"]),
                "display_text": svc["description"],
                "service_name": svc["name"],
                "estimated_cost": svc["estimated_cost"],
            })

        # 用户画像增强
        escalation = ""
        profile = context.user_profile if context else None
        if profile and profile.consecutive_losses >= 3:
            escalation = "检测到连续亏损，强烈建议暂停交易，先照顾好身体状态"

        return {
            "services": services,
            "triggered_by": fatigue_type,
            "action_cards": action_cards,
            "escalation": escalation,
        }

    def _detect_fatigue(self, now: datetime, context: ToolContext = None) -> str:
        """根据时间推断疲劳类型。"""
        hour = now.hour

        if 23 <= hour or hour < 6:
            return "深夜复盘疲劳"
        elif 18 <= hour < 23:
            return "盘后分析疲劳"
        elif (9 <= hour < 11) or (13 <= hour < 15):
            return "盘中盯盘疲劳"
        else:
            return "日常疲劳"

    @staticmethod
    def _action_type(service_type: str) -> str:
        mapping = {
            "饮品": "order_beverage",
            "健康": "wellness_reminder",
            "工具": "open_tool",
        }
        return mapping.get(service_type, "generic_action")

    # ── 深夜关怀 ──────────────────────────────────

    def late_night_care(self, context: ToolContext = None) -> dict:
        """深夜陪伴关怀建议。

        根据时间 + 用户画像计算健康分数，
        分数越低 → 返回越多关怀项。

        Returns:
            { care_items: [dict], wellness_score: float, suggestions: [str] }
        """
        now = datetime.now()
        hour = now.hour

        # 只在深夜/凌晨触发
        if not (hour >= 23 or hour < 6):
            return {
                "care_items": [],
                "wellness_score": 1.0,
                "suggestions": ["现在时间还早，但也要注意休息哦 ✨"],
            }

        wellness = self._calc_wellness(hour, context)
        threshold = 1.0 - wellness  # wellness 越低，threshold 越高 → 更多关怀项

        care_items = []
        for item in _CARE_ITEMS:
            if item["base_priority"] >= threshold:
                care_items.append({
                    "type": item["type"],
                    "content": item["content"],
                    "priority": item["base_priority"],
                })

        # 按 priority 降序
        care_items.sort(key=lambda x: x["priority"], reverse=True)

        # 生成建议文本
        suggestions = self._build_suggestions(wellness, care_items)

        return {
            "care_items": care_items,
            "wellness_score": round(wellness, 2),
            "suggestions": suggestions,
        }

    @staticmethod
    def _calc_wellness(hour: int, context: ToolContext = None) -> float:
        """计算健康评估分 (0.0~1.0)。

        越低 = 越需要关怀。
        """
        # 时间因子：越晚越低
        if 0 <= hour < 4:
            time_factor = 0.1
        elif 4 <= hour < 6:
            time_factor = 0.4
        elif hour >= 23:
            time_factor = 0.5
        else:
            time_factor = 0.8

        score = time_factor

        # 用户画像修正
        if context and context.user_profile:
            profile = context.user_profile
            if profile.consecutive_losses >= 5:
                score -= 0.15
            elif profile.consecutive_losses >= 3:
                score -= 0.1

            if profile.psychological_state in ("焦虑", "恐惧", "沮丧", "绝望"):
                score -= 0.1

        return max(0.0, min(1.0, score))

    @staticmethod
    def _build_suggestions(
        wellness: float,
        care_items: list[dict],
    ) -> list[str]:
        """根据 wellness 分数生成总体建议。"""
        suggestions = []

        if wellness <= 0.2:
            suggestions.append(
                "你的状态已经到了临界点。关闭所有交易软件，"
                "给自己一个完整的休息周期。钱可以再赚，身体只有一个。"
            )
        elif wellness <= 0.4:
            suggestions.append(
                "这么晚了还在复盘，说明你很认真。"
                "但过度疲劳会降低明天的决策质量。休息也是一种投资策略。"
            )
        elif wellness <= 0.6:
            suggestions.append(
                "夜深了，可以准备收工了。"
                "明天开盘前再检查一次计划，比熬到凌晨更有价值。"
            )
        else:
            suggestions.append("夜深了，该休息啦 ✨ 明天又是新的一天")

        if care_items:
            top_item = care_items[0]
            suggestions.append(f"推荐：{top_item['content']}")

        return suggestions
