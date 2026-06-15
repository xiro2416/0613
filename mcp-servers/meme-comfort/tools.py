"""
meme-comfort 工具实现 — 心理按摩与股民热梗库。

工具返回纯数据（不含 Persona 色彩）。
LLM 在 Phase 2 根据 Persona 决定如何使用这些梗。

核心定位: 股市亚文化情绪缓冲垫、交易创伤轻量化解构中心。
"""

from shared.knowledge.manager import KnowledgeManager
from shared.knowledge.meme_library import MemeLibrary
from shared.types import PersonaType


# ── Emo 化解内容库 ───────────────────────────────

_DETOX_CONTENT: dict[str, dict] = {
    "loss": {
        "label": "亏损情绪化解",
        "items": [
            {
                "type": "心理事实",
                "content": "A股历史上，上证指数从长期来看整体向上。短期亏损是大多数人都会经历的正常波动，你并不孤单。",
            },
            {
                "type": "行动建议",
                "content": "拿出一张纸，写下：1) 我的止损线是多少 2) 达到后我会怎么做。写下来比在脑子里反复想有效10倍。",
            },
            {
                "type": "视角转换",
                "content": "如果你最好的朋友亏了同样多的钱，你会怎么安慰他/她？试试用同样的语气对自己说话。",
            },
        ],
    },
    "fomo": {
        "label": "踏空焦虑化解",
        "items": [
            {
                "type": "心理事实",
                "content": "你只会注意到别人晒的赚钱单，不会看到他们亏钱的时候。幸存者偏差让踏空感被无限放大。",
            },
            {
                "type": "行动建议",
                "content": "写下你看好但没买的那只票的理由。如果理由只是'它涨了'，那不是投资逻辑，是后悔。",
            },
            {
                "type": "视角转换",
                "content": "市场每天都有机会。今天错过了一个涨停，不代表明天没有。耐心是散户最大的竞争优势。",
            },
        ],
    },
    "lonely": {
        "label": "孤独感化解",
        "items": [
            {
                "type": "心理事实",
                "content": "股市是一个孤独的战场。大部分交易者都在独自面对屏幕，这种感觉你并不孤单。",
            },
            {
                "type": "行动建议",
                "content": "要不要在雪球/淘股吧发个帖？很多股民都愿意交流，有时候一句'我也是'就能缓解很多。",
            },
            {
                "type": "陪伴提示",
                "content": "我随时在这里。你可以跟我聊聊今天的盘面，或者聊聊完全不相干的事情。",
            },
        ],
    },
    "tired": {
        "label": "交易疲劳化解",
        "items": [
            {
                "type": "心理事实",
                "content": "职业交易是最消耗心力的工作之一。每天4小时的高度专注，盘后还要复盘，疲劳是正常的生理反应。",
            },
            {
                "type": "行动建议",
                "content": "关掉交易软件，去看一部电影或者出门散个步。大脑需要切换场景才能恢复决策质量。",
            },
            {
                "type": "视角转换",
                "content": "你的身体不是AI，不能24小时运转。休息不是偷懒，是对交易账户的负责任。",
            },
        ],
    },
}


class MemeComfortTools:
    """心理按摩工具集"""

    def __init__(self, knowledge: KnowledgeManager = None):
        self._meme_library = MemeLibrary()

    # ── 热梗匹配 ──────────────────────────────────

    def loss_meme_pick(self, loss_level: str = "any") -> dict:
        """按亏损程度匹配自嘲热梗。

        Args:
            loss_level: 亏损等级 — mild / moderate / severe / any

        Returns:
            { memes: [dict], matched_scenario: str, total_available: int }
        """
        valid = {"mild", "moderate", "severe", "any"}
        if loss_level not in valid:
            loss_level = "any"

        # 请求 MEME 人设获取原味梗（Phase2 LLM 负责做 Persona 包装）
        result = self._meme_library.pick(loss_level, PersonaType.MEME)

        memes = []
        for entry in result.entries:
            memes.append({
                "id": entry.id,
                "text": entry.content,
                "loss_level": entry.metadata.get("loss_level", loss_level),
                "tags": entry.metadata.get("tags", []),
                "source": entry.metadata.get("source", ""),
            })

        return {
            "memes": memes,
            "matched_scenario": loss_level,
            "total_available": len(memes),
        }

    # ── Emo 化解 ──────────────────────────────────

    def emo_detox_pick(self, trigger: str = "") -> dict:
        """匹配 emo 化解内容。

        Args:
            trigger: 情绪触发类型 — loss / fomo / lonely / tired / ""

        Returns:
            { detox_items: [dict], matched_trigger: str, label: str }
        """
        # 规范化 trigger
        trigger = trigger.strip().lower()
        valid_triggers = {"loss", "fomo", "lonely", "tired"}
        if trigger not in valid_triggers:
            trigger = ""

        if trigger:
            detox = _DETOX_CONTENT.get(trigger)
        else:
            # 未指定时返回所有场景（供 LLM 选择）
            detox = None

        if detox:
            items = [
                {"type": item["type"], "content": item["content"]}
                for item in detox["items"]
            ]
            return {
                "detox_items": items,
                "matched_trigger": trigger,
                "label": detox["label"],
            }
        else:
            # 返回全部场景摘要
            all_items = []
            for trig, content in _DETOX_CONTENT.items():
                all_items.append({
                    "trigger": trig,
                    "label": content["label"],
                    "preview": content["items"][0]["content"][:50] + "...",
                })
            return {
                "detox_items": [],
                "matched_trigger": "",
                "label": "全部场景",
                "available_triggers": all_items,
            }
