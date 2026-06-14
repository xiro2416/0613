"""
meme-comfort 工具实现 — 心理按摩与股民热梗库。

工具返回纯数据（不含 Persona 色彩）。
LLM 在 Phase 2 根据 Persona 决定如何使用这些梗。

核心定位: 股市亚文化情绪缓冲垫、交易创伤轻量化解构中心。
"""

from shared.knowledge.manager import KnowledgeManager
from shared.knowledge.meme_library import MemeLibrary
from shared.types import PersonaType


class MemeComfortTools:
    """心理按摩工具集"""

    def __init__(self, knowledge: KnowledgeManager = None):
        self._meme_library = MemeLibrary()

    def loss_meme_pick(self, loss_level: str = "any") -> dict:
        """按亏损程度匹配自嘲热梗。

        Returns:
            { memes: [dict], matched_scenario: str }
            每个 meme: { id, text, loss_level, source }
        """
        # 实现要点:
        # 1. 从 MemeLibrary 按 loss_level 筛选
        # 2. 按热门度/新鲜度排序
        # 3. 返回纯梗数据，不做 Persona 包装
        ...

        return {
            "memes": [],
            "matched_scenario": loss_level,
        }

    def emo_detox_pick(self, trigger: str = "") -> dict:
        """匹配 emo 化解内容。

        trigger 可选值: "loss" | "fomo" | "lonely" | "tired" | ""

        Returns:
            { detox_items: [dict], matched_trigger: str }
        """
        ...

        return {
            "detox_items": [],
            "matched_trigger": trigger,
        }
