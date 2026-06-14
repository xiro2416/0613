"""
social-tactician 工具实现 — 股市圈层社交辅助。

工具返回纯数据（不含 Persona 色彩）。
Persona 转换由 Host LLM 在 Phase 2 完成。

核心定位: 情境感知型关系策动器、同频共鸣发生器。
"""

from shared.knowledge.manager import KnowledgeManager
from shared.types import ToolContext


class SocialTacticianTools:
    """社交辅助工具集"""

    def __init__(self, knowledge: KnowledgeManager = None):
        self._knowledge = knowledge

    def ice_break_suggest(
        self,
        target_holdings: list[str] = None,
        context: ToolContext = None,
    ) -> dict:
        """根据市场行情和持仓信息生成社交破冰建议。

        Returns:
            { topics: [dict], ice_breakers: [str], market_hooks: [str] }
            每个 topic: { subject, angle, market_connection }
        """
        # 实现要点:
        # 1. 从 shared.market_data 获取 target_holdings 对应板块行情
        # 2. 生成低刻意度的自然破冰话术方向
        # 3. 借盘面聊认知、聊情绪、聊人生
        # 4. 返回纯话题和角度数据，不做 Persona 包装
        ...

        return {
            "topics": [],
            "ice_breakers": [],
            "market_hooks": [],
        }

    def deep_talk_suggest(
        self,
        topic: str = "",
        context: ToolContext = None,
    ) -> dict:
        """生成深度交流话题框架。

        Returns:
            { framework: dict, discussion_points: [str], pitfalls: [str] }
            framework: { opener, bridge, core_theme, closer }
            pitfalls: 需要避免的尬聊雷区
        """
        ...

        return {
            "framework": {},
            "discussion_points": [],
            "pitfalls": [],
        }
