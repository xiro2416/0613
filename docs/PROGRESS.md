# 项目进度

> 职业股民全场景陪伴式 AI Agent 系统  
> 最后更新：2026-06-14 | 阶段：MCP+Skill 架构迁移 ✅ → 功能实现 ⏳

---

## 一、技术栈

| 层 | 技术 |
|---|---|
| Host 编排 | Python (FastAPI) + Anthropic SDK |
| MCP Server | Python (mcp SDK) × 5 进程 |
| 共享库 | Python (shared/) — knowledge / market_data / memory |
| 传输 | MCP Protocol (STDIO) |
| 前端 | TypeScript + React + Vite |
| 通信 | REST + WebSocket |

---

## 二、系统架构 (MCP+Skill)

```
                    ┌──────────────────────────┐
                    │   MCP Host (Python)       │
                    │                           │
                    │  FastAPI + WebSocket      │
                    │  TimeGate                 │
                    │  PersonaManager           │
                    │  PlanYPipeline            │
                    │  Two-Phase Orchestrator   │
                    └─────┬─────┬─────┬─────┬────┘
                          │     │     │     │
              MCP/STDIO   │     │     │     │  (5 条连接)
         ┌────────────────┼─────┼─────┼─────┼────────────┐
         │                │     │     │     │            │
    ┌────▼────┐  ┌────▼───┐ ┌───▼──┐ ┌──▼────┐  ┌─────▼─────┐
    │ market- │  │psych-  │ │ meme │ │social │  │ life-     │
    │analyzer │  │mirror  │ │comfort│ │tactic│  │ service   │
    │ server  │  │server  │ │server │ │server│  │ server    │
    └────┬────┘  └────┬───┘ └───┬──┘ └──┬────┘  └─────┬─────┘
         │            │         │       │             │
         └────────────┴─────────┴───────┴─────────────┘
                            │
                   Python import (进程内)
                            │
          ┌─────────────────┴─────────────────┐
          │            shared/                │
          │  knowledge/  market_data/  memory/│
          │  types.py                         │
          └───────────────────────────────────┘

进程: 1 Host + 5 MCP Server = 6 进程
```

---

## 三、MCP 架构组件映射

| 原组件 | MCP 角色 | 位置 |
|---|---|---|
| Orchestrator | Host 编排器（两阶段 LLM） | `mcp-hosts/stock-host/orchestrator.py` |
| MODULE_REGISTRY | 删除 → MCP `list_tools()` | — |
| CompositeModule | MCP Server（进程隔离） | `mcp-servers/*/server.py` |
| SubModule.process() | MCP Tool handler | `mcp-servers/*/tools.py` |
| route_sub_module() | 删除 → LLM 语义选择 | — |
| KnowledgeManager | `shared/knowledge/` | 公共 Python 库 |
| MarketDataService | `shared/market_data/` | 公共 Python 库 |
| MemoryManager | `shared/memory/` | 公共 Python 库 |
| TimeGate | Host 内置 | `mcp-hosts/stock-host/time_gate.py` |
| PersonaManager | Host 内置 | `mcp-hosts/stock-host/persona.py` |
| PlanYPipeline | Host 内置 | `mcp-hosts/stock-host/rendering.py` |

---

## 四、文件清单

### Host `mcp-hosts/stock-host/`

| 文件 | 说明 | 状态 |
|---|---|---|
| `app.py` | FastAPI + WebSocket 入口 | ✅ |
| `orchestrator.py` | 两阶段 LLM 编排（Phase1 数据采集 + Phase2 人格化） | ✅ |
| `time_gate.py` | 时间门控（Context Feature Provider） | ✅ |
| `persona.py` | 人设状态机 + system_prompt 装配 | ✅ |
| `rendering.py` | PlanYPipeline 三轨渲染 | ✅ |
| `config.py` | 5 个 MCP Server 连接配置 | ✅ |

### 业务 MCP Server `mcp-servers/`

| Server | 工具 | 状态 |
|---|---|---|
| `market-analyzer` | `compute_value_score`, `compute_shortterm_heat` | ✅ |
| `psychology-mirror` | `greed_detect`, `fear_detect` | ✅ |
| `meme-comfort` | `loss_meme_pick`, `emo_detox_pick` | ✅ |
| `social-tactician` | `ice_break_suggest`, `deep_talk_suggest` | ✅ |
| `life-service` | `fatigue_suggest`, `late_night_care` | ✅ |

### 共享库 `shared/`

| 文件 | 说明 | 状态 |
|---|---|---|
| `types.py` | 全局类型收拢 | ✅ |
| `knowledge/manager.py` | KnowledgeManager 统一入口 | ✅ (2026-06-15: 增加 _seed_retriever) |
| `knowledge/retriever.py` | Grep/RAG/Hybrid 检索器 | ✅ GrepRetriever 已实现 (2026-06-15) |
| `knowledge/market_narratives.py` | 市场历史叙事 | ⏳ 待后续 |
| `knowledge/market_terms.py` | 交易术语库 | ✅ 50条术语已实现 (2026-06-15) |
| `knowledge/meme_library.py` | 热梗语料库 | ✅ 30条热梗已实现 (2026-06-15) |
| `market_data/client.py` | 行情 API 对接层 | ✅ |
| `memory/manager.py` | MemoryManager | ✅ |
| `memory/store.py` | SQLite 存储层 | ✅ 已实现 (2026-06-15) |

### 前端 `frontend/`

| 文件 | 说明 | 状态 |
|---|---|---|
| `src/App.tsx` ~ | 无变化，API 契约兼容 | ✅ |

---

## 五、模块进度

| 模块 | 文档 | MCP Server | 工具实现 |
|---|---|---|---|
| 中枢 + 时间 + 人设 + 渲染 | [00-core.md](docs/modules/00-core.md) | Host 内置 | ⏳ |
| 知识库 | 本文档 | shared/knowledge/ | ✅ 术语+热梗已实现 (2026-06-15) |
| 行情数据 | 本文档 | shared/market_data/ | ⏳ |
| 记忆系统 | 本文档 | shared/memory/ | ✅ store.py ✅ (2026-06-15) |
| 一：行情分析 | [01-market-analyzer.md](docs/modules/01-market-analyzer.md) | market-analyzer server | ⚠️ 待行情数据 |
| 二：人性对齐 | [02-psychology-mirror.md](docs/modules/02-psychology-mirror.md) | psychology-mirror server | ✅ (2026-06-15) |
| 三：心理按摩 | [03-meme-comfort.md](docs/modules/03-meme-comfort.md) | meme-comfort server | ✅ (2026-06-15) |
| 四：社交辅助 | [04-social-tactician.md](docs/modules/04-social-tactician.md) | social-tactician server | ✅ (2026-06-15) |
| 五：生活服务 | [05-life-service.md](docs/modules/05-life-service.md) | life-service server | ✅ (2026-06-15) |

---

## 六、待定（按优先级）

### 高
- [ ] 各 Tool 功能逻辑实现（替换 `...` 存根）
- [ ] Anthropic API Key 配置 + LLM 联调
- [ ] 知识库检索后端选型（grep → RAG 迁移路径）
- [ ] TimeGate 交易日历 API 对接（当前硬编码 2026 年节假日）

### 中
- [ ] TTS 引擎选型与集成
- [ ] 原画库搭建方案（PlanYPipeline visual_track）
- [ ] Phase 2 人格化生成质量调优

### 低
- [ ] WebSocket 流式帧推送优化
- [ ] MCP Server 错误恢复与重连
- [ ] 前后端联调

---

## 七、参考

- [PRD 原始文档](stock-agent-prd.md)
