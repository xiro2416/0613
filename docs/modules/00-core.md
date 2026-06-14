# 中枢系统 — 进度文档

> 包含：中枢调度器、时间门控（特征提供者）、人设状态机、方案Y渲染管线、记忆系统

## 架构状态 ✅

三层架构已设计：

```
中枢调度器 (Orchestrator)
  ├─ 时间门控 (TimeGate)     → Context Feature Provider（不再拒绝请求）
  │    ↓                       → 时间特征注入 MemoryManager.SessionContext
  │                             → 中枢按时间状态动态切换 Prompt
  ├─ 人设管理器 (PersonaManager) → 三人设秒级切换
  ├─ 模块路由 (→ 5 个 BaseModule)
  └─ 方案Y管线 (PlanYPipeline) → 三轨装配
```

## 接口完成度

| 组件 | 文件 | 接口 | 类型定义 | 功能实现 |
|---|---|---|---|---|
| TimeGate | `backend/core/time_gate.py` | `get_time_features()`, `check()`, `is_active()` | `TimeSlot`, `TimeFeature` | ⏳ |
| Orchestrator | `backend/core/orchestrator.py` | `handle_message()`, `switch_persona()`, `create_session()` 等 | `PersonaSwitchAck` | ⏳ |
| PersonaManager | `backend/persona/manager.py` | `get_config()`, `switch()`, `map_emotion()` | — | ⏳ |
| Persona Types | `backend/persona/types.py` | — | `PersonaType`, `EmotionTag`, `PersonaConfig`, `VisualStyle`, `TTSVoice` | ✅ |
| PlanYPipeline | `backend/rendering/pipeline.py` | `render()`, `visual_track()`, `text_track()`, `audio_track()` | — | ⏳ |
| PlanY Types | `backend/rendering/types.py` | — | `PlanYFrame`, `VisualTrack`, `TextTrack`, `AudioTrack`, `PlanYRenderRequest` | ✅ |
| MemoryManager | `backend/memory/manager.py` | `get_user_profile()`, `create_session()`, `append_message()` 等 | — | ⏳ |
| Memory Types | `backend/memory/types.py` | — | `UserProfile`, `SessionContext`, `Message` | ✅ |
| TTS Service | `backend/services/tts.py` | `synthesize()` | `TTSRequest`, `TTSResult` | ⏳ |
| MarketData | `backend/services/market_data.py` | `get_snapshot()`, `get_news()`, `get_holdings_context()` | `MarketSnapshot`, `NewsItem`, `MarketContext` | ⏳ |
| API Routes | `backend/api/routes.py` | REST + WebSocket 端点 | — | ⏳ |

## 待定功能细节

1. **时间门控**：交易日历（A股休市日）如何获取？当前硬编码 2026 年节假日，后续应对接交易日历 API。
2. **人设切换**：切换时的过渡动画时长？是否需要切换确认？
3. **方案Y管线**：原画库存储在本地还是云端 CDN？原画数量规模？
4. **TTS 引擎**：使用哪个 TTS 服务（自建/第三方API）？是否支持流式合成？
5. **记忆系统**：用户画像存储方案（SQLite/PostgreSQL/Redis）？会话历史保留策略？
6. **模块路由**：单次输入路由到几个模块？多模块结果的选取/融合策略？

## 下次工作入口

1. 确认上述待定功能细节
2. 从 `Orchestrator.handle_message()` 开始实现核心链路
3. 同步实现 WebSocket 通信层
