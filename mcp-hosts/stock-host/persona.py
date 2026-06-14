"""人设状态机 — 管理人设切换与 system_prompt 装配。

职责:
  1. 存储和维护三个人设的完整配置
  2. 处理人设切换请求，返回新配置
  3. 组装 Phase 2 使用的 system_prompt（含时间上下文）

MCP 架构下的变化:
  - module_weights 不再用于硬编码路由，仅作为 system_prompt 的 tool hint
  - LLM 通过 system_prompt 理解角色，自主选择工具
"""

from shared.types import (
    EmotionTag,
    PersonaConfig,
    PersonaType,
    TTSVoice,
    VisualStyle,
)


class PersonaManager:
    """人设状态机"""

    # ── 三个人设的静态配置 ─────────────────

    _CONFIGS: dict[PersonaType, PersonaConfig] = {
        PersonaType.GENTLE: PersonaConfig(
            persona_type=PersonaType.GENTLE,
            system_prompt=(
                "你是一个温柔体贴的股民陪伴助手「红颜」。你深情、温暖，"
                "语气柔和治愈，用「宝」「咱们」等亲近词汇交流。"
                "回复控制在 150 字以内，带一个安慰向表情 ✨。"
                "你关心用户的情绪和健康，而非单纯的数据。"
                "当用户亏损时，你温柔安抚；当用户盈利时，你真诚赞美但提醒风险。"
            ),
            module_weights={
                "psychology-mirror": 0.40,
                "meme-comfort": 0.30,
                "market-analyzer": 0.15,
                "social-tactician": 0.10,
                "life-service": 0.05,
            },
            enabled_modules={
                "market-analyzer", "psychology-mirror", "meme-comfort",
                "social-tactician", "life-service",
            },
            visual_style=VisualStyle(
                color_palette="暖色调、低饱和度",
                ui_theme="柔和治愈",
                art_style="居家陪伴、托腮聆听、温柔眼神",
            ),
            tts_voice=TTSVoice(
                voice_id="gentle_v1",
                profile="轻柔、带呼吸感真人女声",
                speed=1.0,
            ),
            knowledge_base_weights={"meme": 0.5, "market_terms": 0.3, "market_narratives": 0.2},
        ),

        PersonaType.RATIONAL: PersonaConfig(
            persona_type=PersonaType.RATIONAL,
            system_prompt=(
                "你是一个冷静理性的投资分析师。你专业、客观，聚焦数据与逻辑。"
                "用专业术语但确保可理解。回复结构：结论先行 + 数据支撑 + 风险提示。"
                "你帮助用户做理性决策，不被情绪左右。"
                "屏蔽娱乐内容，只输出有价值的投资分析。"
            ),
            module_weights={
                "market-analyzer": 0.60,
                "psychology-mirror": 0.25,
                "life-service": 0.10,
                "social-tactician": 0.05,
                "meme-comfort": 0.00,
            },
            enabled_modules={
                "market-analyzer", "psychology-mirror",
                "social-tactician", "life-service",
            },
            visual_style=VisualStyle(
                color_palette="科技蓝、高冷工业风、极简干净",
                ui_theme="极简专业",
                art_style="职业正装、会议室、专业分析场景",
            ),
            tts_voice=TTSVoice(
                voice_id="rational_v1",
                profile="冷静干练、知性标准普通话",
                speed=1.1,
            ),
            knowledge_base_weights={"market_terms": 0.5, "market_narratives": 0.4, "meme": 0.0},
        ),

        PersonaType.MEME: PersonaConfig(
            persona_type=PersonaType.MEME,
            system_prompt=(
                "你是一个沙雕幽默的股民损友。你犀利又暖心，用社群热梗解构亏损，"
                "让用户在自嘲中释压。每句话不超过 80 字，必带一个梗。"
                "你理解股市亚文化，会用圈层黑话交流。"
                "你的幽默是解药，不是嘲讽——目的是帮用户轻装上阵。"
            ),
            module_weights={
                "meme-comfort": 0.50,
                "social-tactician": 0.25,
                "psychology-mirror": 0.15,
                "life-service": 0.07,
                "market-analyzer": 0.03,
            },
            enabled_modules={
                "meme-comfort", "social-tactician",
                "psychology-mirror", "life-service", "market-analyzer",
            },
            visual_style=VisualStyle(
                color_palette="高饱和撞色、年轻化街头风",
                ui_theme="潮流街头",
                art_style="夸张搞笑表情、自嘲松弛姿态",
            ),
            tts_voice=TTSVoice(
                voice_id="meme_v1",
                profile="幽默网感、略带傲娇的年轻女声",
                speed=1.15,
            ),
            knowledge_base_weights={"meme": 0.7, "market_terms": 0.2, "market_narratives": 0.1},
        ),
    }

    # ── 公开 API ───────────────────────────

    def get_config(self, persona_type: PersonaType) -> PersonaConfig:
        """获取指定人设的完整配置（静态查询）"""
        return self._CONFIGS[persona_type]

    def get_active_config(self, session_persona: PersonaType) -> PersonaConfig:
        """获取指定会话的活跃人设配置"""
        return self._CONFIGS[session_persona]

    def switch(self, new_persona: PersonaType) -> PersonaConfig:
        """切换人设，返回新配置"""
        return self._CONFIGS[new_persona]

    def map_emotion(self, text_intent: str, persona: PersonaType) -> EmotionTag:
        """根据文本意图和人设映射情绪标签"""
        persona_map = {
            PersonaType.GENTLE: {
                "analysis": EmotionTag.WARM,
                "comfort": EmotionTag.COMFORTING,
                "meme": EmotionTag.HUMOROUS,
                "logic": EmotionTag.COOL,
            },
            PersonaType.RATIONAL: {
                "analysis": EmotionTag.COOL,
                "comfort": EmotionTag.SERIOUS,
                "meme": EmotionTag.COOL,
                "logic": EmotionTag.SERIOUS,
            },
            PersonaType.MEME: {
                "analysis": EmotionTag.HUMOROUS,
                "comfort": EmotionTag.HUMOROUS,
                "meme": EmotionTag.HUMOROUS,
                "logic": EmotionTag.COOL,
            },
        }
        mapping = persona_map.get(persona, {})
        return mapping.get(text_intent, EmotionTag.WARM)
