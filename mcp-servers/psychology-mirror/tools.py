"""
psychology-mirror 工具实现 — 人性对齐与深度交流。

工具返回纯数据（不含 Persona 色彩）。
Persona 转换由 Host LLM 在 Phase 2 完成。

核心定位: 交易劣根性可视化外显、多模态心理沙盘。
MVP 实现: 基于关键词加权匹配的 greedy/fear 信号检测。
"""

from typing import Optional

from shared.knowledge.manager import KnowledgeManager
from shared.types import ToolContext


# ═══════════════════════════════════════════════════════════
# 贪婪信号关键词字典
# ═══════════════════════════════════════════════════════════

_GREED_SIGNALS: list[dict] = [
    {
        "category": "追涨冲动",
        "keywords": ["追涨", "追高", "赶紧上车", "别踏空", "来不及了", "快买", "冲冲冲",
                      "跑步进场", "冲进去", "买买买", "干就完了"],
        "weight": 0.35,
        "mirror_text": "你似乎有一种'怕错过'的紧迫感。市场永远有机会，真正的机会不需要追。",
    },
    {
        "category": "过度自信",
        "keywords": ["一定涨", "肯定赚", "稳了", "没问题", "不可能跌", "我看准了", "绝对",
                      "必涨", "百分之百", "包赚", "放心吧", "相信我就"],
        "weight": 0.30,
        "mirror_text": "确定性是投资中最昂贵的幻觉。没有任何一笔交易是100%确定的。",
    },
    {
        "category": "仓位激进",
        "keywords": ["满仓", "梭哈", "all in", "全仓", "重仓", "杠杆", "借钱",
                      "allin", "all-in", "加杠杆", "配资", "融资"],
        "weight": 0.25,
        "mirror_text": "高风险仓位下，一次回撤就可能击穿你的心理防线。仓位管理是长期存活的关键。",
    },
    {
        "category": "死扛倾向",
        "keywords": ["不卖", "再等等", "还会涨回来", "我不信", "只要不卖就不亏", "持有",
                      "死扛", "扛着", "等回本", "一定会回去的", "不走"],
        "weight": 0.10,
        "mirror_text": "'只要不卖就不亏'是一种心理防御机制。设定客观止损点比等待回本更有效。",
    },
]

# ═══════════════════════════════════════════════════════════
# 恐惧信号关键词字典
# ═══════════════════════════════════════════════════════════

_FEAR_SIGNALS: list[dict] = [
    {
        "category": "恐慌抛售",
        "keywords": ["割肉", "清仓", "跑了", "不玩了", "受不了了", "全卖了", "出场",
                      "止损", "赶紧卖", "逃", "认输"],
        "weight": 0.35,
        "mirror_text": "恐慌时做出的决定，事后往往让人后悔。你可以在情绪平复后再做决策。",
    },
    {
        "category": "绝望情绪",
        "keywords": ["亏死了", "又跌", "天天跌", "撑不住", "绝望", "完蛋了", "崩了",
                      "没救了", "跌没了", "血亏", "归零", "倾家荡产"],
        "weight": 0.30,
        "mirror_text": "亏损是交易的一部分，但你不等于你的交易结果。感到沮丧是正常的。",
    },
    {
        "category": "决策瘫痪",
        "keywords": ["不敢买", "再观望", "等等看", "犹豫", "不确定", "看不清", "迷茫",
                      "观望", "怕", "再等等看", "不知道该", "拿不定主意"],
        "weight": 0.20,
        "mirror_text": "有时候什么都不做，就是最好的操作。等待也是一种纪律。",
    },
    {
        "category": "后悔反刍",
        "keywords": ["后悔", "早知道", "要是", "当初", "要是卖了就好了", "错过了",
                      "要是我", "当时应该", "我本来", "可惜没"],
        "weight": 0.15,
        "mirror_text": "'早知道'是交易中最没有生产力的三个字。从当前盘面出发，不被历史成本锚定。",
    },
]

# ── 默认操作边界 ──────────────────────────────────

_DEFAULT_BOUNDARIES = {
    "短线": "建议单只个股仓位不超过总资金的20%，设置5%硬止损线，当日亏损超3%暂停交易",
    "中长线": "建议单只个股仓位不超过总资金的30%，设置10%硬止损线，不因短期波动频繁操作",
    "打板": "建议打板资金不超过总资金的10%，炸板即止损、不补仓，当日打板亏损超5%休息",
    "default": "建议单只个股仓位不超过总资金的20%，设置明确止损点，不因情绪追涨杀跌",
}


class PsychologyMirrorTools:
    """人性对齐工具集"""

    def __init__(self, knowledge: Optional[KnowledgeManager] = None):
        self._knowledge = knowledge

    # ── 贪婪检测 ──────────────────────────────────

    def greed_detect(
        self,
        user_query: str,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """检测用户当前的贪婪心理信号。

        Returns:
            { greed_index: float, signals: [dict],
              mirror_prompt: str, suggested_boundary: str }
        """
        signals = []
        total_weight = 0.0

        # 关键词匹配
        query_lower = user_query.lower()
        for signal_def in _GREED_SIGNALS:
            matched = self._match_keywords(query_lower, signal_def["keywords"])
            if matched:
                strength = (len(matched) / len(signal_def["keywords"])) * signal_def["weight"]
                signals.append({
                    "category": signal_def["category"],
                    "matched_keywords": matched,
                    "strength": round(strength, 3),
                    "mirror_text": signal_def["mirror_text"],
                })
                total_weight += strength

        # 用户画像修正
        if context and context.user_profile:
            profile = context.user_profile
            if profile.risk_tolerance == "high":
                total_weight += 0.10
            if profile.consecutive_losses >= 3:
                total_weight += 0.10

        greed_index = min(1.0, max(0.0, total_weight))

        # 选择最高分信号的 mirror_text
        signals.sort(key=lambda s: s["strength"], reverse=True)
        mirror_prompt = signals[0]["mirror_text"] if signals else ""

        # 建议的操作边界
        suggested_boundary = self._get_boundary(context)

        return {
            "greed_index": round(greed_index, 2),
            "signals": signals[:3],  # top 3
            "mirror_prompt": mirror_prompt,
            "suggested_boundary": suggested_boundary,
        }

    # ── 恐惧检测 ──────────────────────────────────

    def fear_detect(
        self,
        user_query: str,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """检测用户当前的恐惧/防御心理信号。

        Returns:
            { fear_index: float, signals: [dict],
              mirror_prompt: str, suggested_action: str }
        """
        signals = []
        total_weight = 0.0

        # 关键词匹配
        query_lower = user_query.lower()
        for signal_def in _FEAR_SIGNALS:
            matched = self._match_keywords(query_lower, signal_def["keywords"])
            if matched:
                strength = (len(matched) / len(signal_def["keywords"])) * signal_def["weight"]
                signals.append({
                    "category": signal_def["category"],
                    "matched_keywords": matched,
                    "strength": round(strength, 3),
                    "mirror_text": signal_def["mirror_text"],
                })
                total_weight += strength

        # 用户画像修正
        if context and context.user_profile:
            profile = context.user_profile
            if profile.consecutive_losses >= 5:
                total_weight += 0.15
            elif profile.consecutive_losses >= 3:
                total_weight += 0.08
            if profile.psychological_state in ("焦虑", "恐惧", "沮丧", "绝望"):
                total_weight += 0.10

        fear_index = min(1.0, max(0.0, total_weight))

        # 选择最高分信号
        signals.sort(key=lambda s: s["strength"], reverse=True)
        mirror_prompt = signals[0]["mirror_text"] if signals else ""

        # 建议行动
        suggested_action = self._get_action(fear_index, context)

        return {
            "fear_index": round(fear_index, 2),
            "signals": signals[:3],
            "mirror_prompt": mirror_prompt,
            "suggested_action": suggested_action,
        }

    # ── 辅助 ──────────────────────────────────────

    @staticmethod
    def _match_keywords(query_lower: str, keywords: list[str]) -> list[str]:
        """从 query 中提取匹配的关键词列表。"""
        return [kw for kw in keywords if kw.lower() in query_lower]

    @staticmethod
    def _get_boundary(context: ToolContext = None) -> str:
        """根据用户画像返回建议的防御边界。"""
        if context and context.user_profile:
            style = context.user_profile.trading_style
            if style in _DEFAULT_BOUNDARIES:
                return _DEFAULT_BOUNDARIES[style]
            boundary = context.user_profile.defense_boundary
            if boundary:
                return boundary
        return _DEFAULT_BOUNDARIES["default"]

    @staticmethod
    def _get_action(fear_index: float, context: ToolContext = None) -> str:
        """根据恐惧指数推荐行动。"""
        if fear_index >= 0.7:
            return "建议暂停交易1-3天，让情绪回到基线。不要在恐惧中做任何买卖决定。"
        elif fear_index >= 0.4:
            return "建议将仓位降低到你能安心睡觉的水平。如果持仓让你失眠，说明仓位太大了。"
        elif fear_index > 0:
            return "建议写下你的交易理由和止损计划。用文字梳理思路，而非在脑中反复纠结。"
        else:
            return "当前情绪状态平稳，适合客观决策。保持复盘和计划执行的习惯。"
