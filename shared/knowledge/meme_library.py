"""热梗语料库 — 股民自嘲亚文化内容。

深度对接主流炒股社区实时语料，按亏损程度、情绪状态、
人设匹配返回不同风格的梗。

梗分类:
  - 轻度亏损 (0-3%): 自嘲调侃类
  - 中度亏损 (3-8%): 黑色幽默类
  - 重度亏损 (>8%): 疗伤共鸣类
  - 通用: 社群共鸣类
"""

from shared.types import KnowledgeEntry, KnowledgeResult, PersonaType


class MemeLibrary:
    """热梗语料库"""

    def pick(self, loss_level: str, persona: PersonaType) -> KnowledgeResult:
        """按亏损程度 + 人设匹配热梗

        Args:
            loss_level: 亏损级别 ("mild" | "moderate" | "severe" | "any")
            persona: 当前人设（影响梗的风格筛选）

        Returns:
            匹配的梗列表

        实现要点:
          - 语料按 loss_level + persona 双维度标注
          - GENTLE 下返回温和版梗
          - MEME 下返回全量原味梗
          - RATIONAL 下不建议调用此方法
        """
        ...
        return KnowledgeResult()
