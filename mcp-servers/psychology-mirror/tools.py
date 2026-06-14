"""
psychology-mirror 工具实现 — 人性对齐与深度交流。

工具返回纯数据（不含 Persona 色彩）。
Persona 转换由 Host LLM 在 Phase 2 完成。

核心定位: 交易劣根性可视化外显、多模态心理沙盘。
"""

from typing import Optional

from shared.knowledge.manager import KnowledgeManager
from shared.types import ToolContext


class PsychologyMirrorTools:
    """人性对齐工具集"""

    def __init__(self, knowledge: Optional[KnowledgeManager] = None):
        self._knowledge = knowledge

    def greed_detect(
        self,
        user_query: str,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """检测用户当前的贪婪心理信号。

        触发场景: 用户过度乐观、想追涨、想满仓、赌徒心理浮现时。
        返回贪婪指标和对应的镜像反思提示。

        Returns:
            { greed_index: float, signals: [dict],
              mirror_prompt: str, suggested_boundary: str }
        """
        # 实现要点:
        # 1. 从 context.user_profile 读取交易风格和风险偏好
        # 2. NER 提取追涨关键词（"满仓""梭哈""all in"）
        # 3. 计算贪婪指数 (0.0-1.0)
        # 4. 生成镜像反思提示（不含 Persona 语气）
        ...

        return {
            "greed_index": 0.0,
            "signals": [],
            "mirror_prompt": "",
            "suggested_boundary": "",
        }

    def fear_detect(
        self,
        user_query: str,
        context: Optional[ToolContext] = None,
    ) -> dict:
        """检测用户当前的恐惧/防御心理信号。

        触发场景: 连续回撤后想割肉、恐慌抛售、过度防御时。
        返回恐惧指标和对应的安抚提示。

        Returns:
            { fear_index: float, signals: [dict],
              mirror_prompt: str, suggested_action: str }
        """
        # 实现要点:
        # 1. 从 context.user_profile 读取连续回撤天数
        # 2. 分析用户文本的情绪负面程度
        # 3. 计算恐惧指数 (0.0-1.0)
        # 4. 返回镜像反思提示
        ...

        return {
            "fear_index": 0.0,
            "signals": [],
            "mirror_prompt": "",
            "suggested_action": "",
        }
