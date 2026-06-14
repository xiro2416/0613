"""
全局类型定义 — 系统所有模块共享的唯一类型源。

类型来源（原 backend/ 分散文件，现已收拢）：
  - persona:    PersonaType, EmotionTag, PersonaConfig, VisualStyle, TTSVoice
  - time_gate:  TimeSlot, TimeFeature
  - rendering:  PlanYFrame, VisualTrack, TextTrack, AudioTrack, PlanYRenderRequest
  - modules:    ToolContext, ToolResult（原 ModuleContext, ModuleResult）
  - memory:     UserProfile, SessionContext, Message
  - knowledge:  KnowledgeDomain, RetrievalMode, KnowledgeQuery, KnowledgeResult, KnowledgeEntry
  - market_data: MarketSnapshot, NewsItem, MarketContext
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Persona
# ═══════════════════════════════════════════════════════════════

class PersonaType(Enum):
    GENTLE = "gentle"          # 温柔红颜（默认）
    RATIONAL = "rational"      # 理性分析
    MEME = "meme"              # 沙雕自嘲


class EmotionTag(Enum):
    """情绪标签 — 方案Y视觉轨选图 + 动效文本轨风格的依据"""
    WARM = "warm"
    COOL = "cool"
    HUMOROUS = "humorous"
    COMFORTING = "comforting"
    SERIOUS = "serious"


@dataclass
class VisualStyle:
    color_palette: str         # "暖色调、低饱和度"
    ui_theme: str
    art_style: str


@dataclass
class TTSVoice:
    voice_id: str
    profile: str               # "轻柔、带呼吸感真人女声"
    speed: float = 1.0


@dataclass
class PersonaConfig:
    """单一人设的全维度配置"""
    persona_type: PersonaType
    system_prompt: str                     # LLM 系统提示词
    module_weights: dict[str, float] = field(default_factory=dict)  # 模块名 → 路由权重
    enabled_modules: set[str] = field(default_factory=set)
    visual_style: Optional[VisualStyle] = None
    tts_voice: Optional[TTSVoice] = None
    knowledge_base_weights: dict[str, float] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# TimeGate
# ═══════════════════════════════════════════════════════════════

class TimeSlot(Enum):
    TRADING_HOURS = "trading_hours"        # 盘中 9:15-15:00
    POST_MARKET = "post_market"            # 盘后 15:00-次日 9:15
    WEEKEND_HOLIDAY = "weekend_holiday"    # 周末/法定节假日
    UNKNOWN = "unknown"


@dataclass
class TimeFeature:
    time_slot: TimeSlot
    is_trading_day: bool
    market_status: str                     # 可读中文描述
    next_open_time: str                    # ISO 格式
    next_action_hint: str                  # "距下一次开盘还有 X 小时"


# ═══════════════════════════════════════════════════════════════
# Rendering (PlanY)
# ═══════════════════════════════════════════════════════════════

@dataclass
class VisualTrack:
    image_url: str
    emotion_tag: EmotionTag
    style_theme: str


@dataclass
class TextTrack:
    content: str
    emotion_tag: EmotionTag
    type_speed_ms: int = 80


@dataclass
class AudioTrack:
    audio_url: str
    voice_profile: str
    duration_ms: int
    sync_text: str


@dataclass
class PlanYFrame:
    """方案Y 单帧 — 三轨最小传输单元"""
    visual: VisualTrack
    text: TextTrack
    audio: AudioTrack


@dataclass
class PlanYRenderRequest:
    content: str
    emotion_tag: EmotionTag
    persona_type: PersonaType


# ═══════════════════════════════════════════════════════════════
# Module → Tool 契约 (MCP 架构下工具只返回纯数据)
# ═══════════════════════════════════════════════════════════════

@dataclass
class ToolContext:
    """工具入参 — Host 装配后传入 MCP Tool"""
    session_id: str
    user_input: str
    user_profile: Optional["UserProfile"] = None
    session_context: Optional["SessionContext"] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具产出 — 纯数据结果（不含 Persona 色彩、不含 EmotionTag）

    MCP 架构下 Persona 转换由 Host LLM 在 Phase 2 完成。
    """
    tool_name: str
    data: dict                            # 结构化纯数据
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# Memory
# ═══════════════════════════════════════════════════════════════

@dataclass
class Message:
    """单条对话消息"""
    role: str                  # "user" | "agent"
    content: str
    emotion_tag: Optional[EmotionTag] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """用户画像 — 长期记忆"""
    user_id: str
    holdings: list[str] = field(default_factory=list)
    trading_style: str = ""
    risk_tolerance: str = ""
    psychological_state: str = ""
    defense_boundary: str = ""
    consecutive_losses: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionContext:
    """会话上下文 — 短期记忆"""
    session_id: str
    user_id: str
    active_persona: PersonaType
    conversation_history: list[Message] = field(default_factory=list)
    today_pnl: Optional[float] = None
    emotional_state: str = ""
    time_slot: Optional[TimeSlot] = None
    created_at: datetime = field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════════
# Knowledge
# ═══════════════════════════════════════════════════════════════

class KnowledgeDomain(Enum):
    MARKET_NARRATIVES = "market_narratives"
    MARKET_TERMS = "market_terms"
    MEME = "meme"


class RetrievalMode(Enum):
    GREP = "grep"
    RAG = "rag"
    HYBRID = "hybrid"


@dataclass
class KnowledgeQuery:
    domain: KnowledgeDomain
    persona: PersonaType
    query: str = ""
    keywords: list[str] = field(default_factory=list)
    mode: RetrievalMode = RetrievalMode.GREP
    filters: dict = field(default_factory=dict)
    top_k: int = 5


@dataclass
class KnowledgeEntry:
    id: str
    content: str
    domain: KnowledgeDomain
    score: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class KnowledgeResult:
    entries: list[KnowledgeEntry] = field(default_factory=list)
    confidence: float = 0.0
    source_domain: Optional[KnowledgeDomain] = None
    retrieval_mode: RetrievalMode = RetrievalMode.GREP


# ═══════════════════════════════════════════════════════════════
# Market Data
# ═══════════════════════════════════════════════════════════════

@dataclass
class MarketSnapshot:
    timestamp: datetime
    index_name: str
    current_price: float
    change_pct: float
    volume: int


@dataclass
class NewsItem:
    source: str
    title: str
    content: str
    sentiment: str             # "positive" | "negative" | "neutral"
    published_at: datetime


@dataclass
class MarketContext:
    snapshots: list[MarketSnapshot] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)
    holdings_snapshot: dict = field(default_factory=dict)
