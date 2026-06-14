"""方案Y 三轨渲染管线 — 将 LLM 文本装配为 PlanYFrame。

渲染流程:
  content + emotion_tag + persona_type
    ├─→ visual_track()  → 匹配静态原画底图
    ├─→ text_track()    → 生成打字机参数化文本
    └─→ audio_track()   → 调用 TTS 服务生成语音

三轨并行装配，数据就绪后封装为 PlanYFrame 返回。
"""

from shared.types import (
    AudioTrack,
    EmotionTag,
    PersonaType,
    PlanYFrame,
    PlanYRenderRequest,
    TextTrack,
    VisualTrack,
)


class PlanYPipeline:
    """方案Y 三轨渲染管线"""

    def render(self, request: PlanYRenderRequest) -> PlanYFrame:
        """装配三轨帧"""
        return PlanYFrame(
            visual=self.visual_track(request.emotion_tag, request.persona_type),
            text=self.text_track(request.content, request.emotion_tag),
            audio=self.audio_track(request.content, request.persona_type),
        )

    def visual_track(self, emotion: EmotionTag, persona_type: PersonaType) -> VisualTrack:
        """根据情绪标签 + 人设匹配静态原画

        实现要点:
          - 云端维护 IP 原画库，按 (persona, emotion) 索引
          - 根据人设差异，同一情绪配不同风格的底图
        """
        # MVP: 返回预设映射（后续对接云端资源库）
        style_map = {
            PersonaType.GENTLE: "暖色调治愈风",
            PersonaType.RATIONAL: "科技蓝高冷工业风",
            PersonaType.MEME: "高饱和撞色街头风",
        }

        return VisualTrack(
            image_url=f"cdn://art/{persona_type.value}/{emotion.value}.png",
            emotion_tag=emotion,
            style_theme=style_map.get(persona_type, "默认"),
        )

    def text_track(self, content: str, emotion: EmotionTag) -> TextTrack:
        """生成带打字机参数的文本轨

        打字速度:
          - WARM/COMFORTING → 慢速 (~100ms/字)
          - COOL/SERIOUS → 中速 (~80ms/字)
          - HUMOROUS → 快速 (~60ms/字)
        """
        speed_map = {
            EmotionTag.WARM: 100,
            EmotionTag.COMFORTING: 100,
            EmotionTag.COOL: 80,
            EmotionTag.SERIOUS: 80,
            EmotionTag.HUMOROUS: 60,
        }

        return TextTrack(
            content=content,
            emotion_tag=emotion,
            type_speed_ms=speed_map.get(emotion, 80),
        )

    def audio_track(self, content: str, persona_type: PersonaType) -> AudioTrack:
        """调用 TTS 服务生成语音轨"""
        voice_map = {
            PersonaType.GENTLE: "gentle_v1",
            PersonaType.RATIONAL: "rational_v1",
            PersonaType.MEME: "meme_v1",
        }

        # MVP: 返回 TTS 请求元数据（后续对接 TTS 服务）
        return AudioTrack(
            audio_url=f"tts://generate?voice={voice_map.get(persona_type)}&text={content[:100]}",
            voice_profile=voice_map.get(persona_type, "default"),
            duration_ms=len(content) * 80,  # 粗略估算
            sync_text=content,
        )
