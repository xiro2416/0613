"""
life-service 工具实现 — 生活服务 Skills 连接器。

工具返回纯数据（不含 Persona 色彩）。

核心定位: 高压决策后的生理补给站、认知无载荷行动链。

MVP 阶段适配瑞幸咖啡等补给场景。
"""

from shared.types import ToolContext


class LifeServiceTools:
    """生活服务工具集 — 自包含，无外部依赖"""

    def fatigue_suggest(self, context: ToolContext = None) -> dict:
        """为疲劳状态用户推荐补给服务。

        触发场景: 深夜复盘后、脑力透支、长时间盯盘后。

        Returns:
            { services: [dict], triggered_by: str, action_cards: [dict] }
            每个 service: { name, type, delivery_time, estimated_cost }
        """
        # 实现要点:
        # 1. 根据时间（深夜/凌晨）推荐不同服务类型
        # 2. 生成轻量化服务卡片（可一键下单）
        # 3. 适配瑞幸咖啡等补给场景
        ...

        return {
            "services": [],
            "triggered_by": "fatigue",
            "action_cards": [],
        }

    def late_night_care(self, context: ToolContext = None) -> dict:
        """深夜陪伴关怀建议。

        触发场景: 凌晨还在复盘、失眠看盘、盘后焦虑。

        Returns:
            { care_items: [dict], wellness_score: float, suggestions: [str] }
        """
        ...

        return {
            "care_items": [],
            "wellness_score": 0.0,
            "suggestions": [],
        }
