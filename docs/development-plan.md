# 开发计划：非行情依赖模块实现

> 状态：待实施 | 更新：2026-06-15

## 背景

当前骨架完整（类型系统、MCP 协议层、编排器、人设状态机、时间门控、渲染管线均已完成），但所有业务逻辑全是 `...` 存根。行情数据源暂不推进，先实现**所有不依赖实时行情的模块**，让系统具备完整的盘后陪伴能力。

---

## 依赖关系总览

```
Phase 1: Memory Store ──── 无依赖，最深瓶颈
Phase 2: Knowledge Base ── 无依赖
Phase 3: Life Service ──── 无依赖
Phase 4: Psychology Mirror  无依赖
Phase 5: Meme Comfort ──── 依赖 Phase 2a (MemeLibrary)
Phase 6: Social Tactician ─ 无依赖
```

Phase 1、2、3、4、6 可并行。Phase 5 需在 Phase 2a 之后。

---

## Phase 1: Memory Store (SQLite) ⭐ 最高优先级 ✅ 已完成

**文件**: `shared/memory/store.py` — 10 个方法已全部实现

> 完成日期：2026-06-15 | 17 个单元测试全部通过

所有会话/消息/用户画像的持久化依赖于此。Host 启动时直接实例化，当前无法工作。

### 数据库 Schema

```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    holdings TEXT DEFAULT '[]',          -- JSON array
    trading_style TEXT DEFAULT '',
    risk_tolerance TEXT DEFAULT '',
    psychological_state TEXT DEFAULT '',
    defense_boundary TEXT DEFAULT '',
    consecutive_losses INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    active_persona TEXT DEFAULT 'gentle',
    today_pnl REAL,
    emotional_state TEXT DEFAULT '',
    time_slot TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('user','agent')) NOT NULL,
    content TEXT NOT NULL,
    emotion_tag TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### User 表字段的更新策略（MVP）

MVP 阶段所有心理相关字段**仅通过用户手动设置**，行为推断留到后续版本：

| 字段 | MVP 更新方式 | 后续版本（行为推断） |
|------|-------------|-------------------|
| `holdings` | 用户通过 API 手动填写（股票代码列表） | — |
| `trading_style` | 用户首次使用时选择（短线/中长线/打板） | 从交易模式中自动推断 |
| `risk_tolerance` | 用户选择（高/中/低），默认未设置 | 从仓位管理 + 回撤行为推断 |
| `psychological_state` | 用户自选标签，默认空 | 从 Session 中 greed/fear 信号自动回流 |
| `defense_boundary` | 用户自定义止损规则文本，默认空 | 从多次交易模式中学习 |
| `consecutive_losses` | 用户手动维护，默认 0 | 对接行情数据后自动计算 |

对应的 API 已经存在于 `app.py`：

```
POST /api/sessions              → 创建会话时传入默认 persona
GET  /api/users/{user_id}/profile  → 读取用户画像
POST /api/users/{user_id}/profile  → 更新用户画像（手动设置上述字段）
```

需要新增的 API（Phase 1 同步实现）：`POST /api/users/{user_id}/profile` 接收 `UpdateUserProfileRequest`，将可更新的字段写入 SQLite。

### 实现要点

- 使用 `sqlite3` 标准库 + `threading.Lock` 串行化写操作
- `check_same_thread=False`（FastAPI 多线程）
- WAL 模式 + 外键约束
- `holdings` 字段 JSON 序列化/反序列化
- `get_session()` 从 messages 表重建 `conversation_history`（上限 100 条）
- `close_session()` MVP 阶段仅设 `is_active=0`，不做画像回流（留给后续版本）
- 自动创建 `data/` 目录

### 验证

- 新建 `tests/test_memory_store.py`，用 `:memory:` 隔离测试
- 验证 CRUD 全部操作
- 验证 `conversation_history` 正确重建

---

## Phase 2: Knowledge Base ✅ 已完成

> 完成日期：2026-06-15 | 35 个单元测试全部通过

三个独立子任务，可并行。

### 2a. Meme Library

**文件**: `shared/knowledge/meme_library.py`

**方法**: `pick(loss_level: str, persona: PersonaType) -> KnowledgeResult`

- 内置 ~30 条中文股民热梗
- 四个亏损等级: `mild` / `moderate` / `severe` / `any`，各 6-8 条
- 每条梗有 GENTLE/MEME 变体，RATIONAL 返回空
- 按 `freshness` 排序，返回 top 5
- 示例梗：

| 亏损等级 | 示例 |
|----------|------|
| mild | "今天小亏，问题不大，明天又是一条好汉" |
| moderate | "我的账户就像过山车，可惜只有下坡没有上坡" |
| severe | "别人炒股是为了赚钱，我炒股是为了见证历史" |
| any | "A股虐我千百遍，我待A股如初恋" |

### 2b. Market Terms

**文件**: `shared/knowledge/market_terms.py`

**方法**: `search(keywords: list[str]) -> KnowledgeResult`

- 内置 ~50 条交易术语
- 四类: 基础交易(15) / 圈层黑话(15) / 策略术语(10) / 技术分析(10)
- 支持术语名 + 别名匹配 + 定义全文搜索

### 2c. GrepRetriever

**文件**: `shared/knowledge/retriever.py`

**方法**: `retrieve(query: KnowledgeQuery) -> KnowledgeResult`

- 纯关键词计分匹配: `matches / len(keywords)`
- 支持 domain 过滤 + top_k 截断
- `KnowledgeManager.__init__` 中 seed 来自 domain classes 的 entries
- RAG/Hybrid Retriever 保持 stub

---

## Phase 3: Life Service Tools ✅ 已完成

> 完成日期：2026-06-15 | 17 个单元测试全部通过

**文件**: `mcp-servers/life-service/tools.py` — 2 个方法全是 `...`

零外部依赖，最独立的 MCP Server。

### `fatigue_suggest()`

- 基于时间窗口判定疲劳类型：

| 时间段 | 疲劳类型 | 服务卡片 |
|--------|----------|----------|
| 23:00-06:00 | 深夜复盘疲劳 | 热牛奶助眠 / 睡眠引导 / 明日盘前提醒 |
| 18:00-22:59 | 盘后分析疲劳 | 瑞幸咖啡 / 肩颈放松操 / 复盘笔记模板 |
| 09:15-15:00 | 盘中盯盘疲劳 | 深呼吸引导 / 盯盘姿势提醒 / 水分补给 |
| 其他 | 日常疲劳 | 通用放松建议 |

- 每 session 每 2 小时最多触发一次

### `late_night_care()`

- 23:00-06:00 触发
- 根据时间 + 用户状态计算 `wellness_score` (0.0-1.0)
- 分数越低 → 返回越多关怀项（睡眠提醒 / 护眼提醒 / 情绪安抚 / 补水提醒）

---

## Phase 4: Psychology Mirror Tools ✅ 已完成

> 完成日期：2026-06-15 | 24 个单元测试全部通过

**文件**: `mcp-servers/psychology-mirror/tools.py` — 2 个方法全是 `...`

### `greed_detect()` — 贪婪检测

| 信号类别 | 权重 | 关键词示例 |
|----------|------|-----------|
| 追涨冲动 | 0.35 | 追涨、追高、赶紧上车、别踏空、来不及了 |
| 过度自信 | 0.30 | 一定涨、肯定赚、稳了、不可能跌 |
| 仓位激进 | 0.25 | 满仓、梭哈、all in、全仓、杠杆 |
| 死扛倾向 | 0.10 | 不卖、再等等、只要不卖就不亏 |

- 关键词匹配 → 加权计算 `greed_index` [0.0, 1.0]
- 用户画像加成: high risk_tolerance +0.1, consecutive_losses>=3 +0.1
- 返回 `mirror_prompt`（镜像反思文本）+ `suggested_boundary`

### `fear_detect()` — 恐惧检测

| 信号类别 | 权重 | 关键词示例 |
|----------|------|-----------|
| 恐慌抛售 | 0.35 | 割肉、清仓、跑了、不玩了、受不了了 |
| 绝望情绪 | 0.30 | 亏死了、天天跌、撑不住、绝望、崩了 |
| 决策瘫痪 | 0.20 | 不敢买、再观望、犹豫、不确定、迷茫 |
| 后悔反刍 | 0.15 | 后悔、早知道、要是、当初、错过了 |

- 用户画像加成: consecutive_losses>=5 +0.15
- 返回 `mirror_prompt` + `suggested_action`

---

## Phase 5: Meme Comfort Tools ✅ 已完成

> 完成日期：2026-06-15 | 15 个单元测试全部通过

**文件**: `mcp-servers/meme-comfort/tools.py` — 2 个方法全是 `...`

**前置依赖**: Phase 2a MemeLibrary 完成

### `loss_meme_pick(loss_level: str)`

- 调用 `MemeLibrary.pick()` → 转换为 API 格式
- 返回 memes 列表 + matched_scenario

### `emo_detox_pick(trigger: str)`

- 4 类情绪化解场景: loss / fomo / lonely / tired
- 每类 3 个化解项: 心理事实 + 行动建议 + 视角转换

| Trigger | 化解方向 |
|---------|----------|
| loss | "A股历史上每10年有7年上涨，短期亏损是正常波动" |
| fomo | "你只会注意到别人晒的赚钱单，不会看到他们亏钱的时候" |
| lonely | "大部分交易者都在独自面对屏幕，这种感觉你并不孤单" |
| tired | "你的身体不是AI，不能24小时运转。休息是对账户的负责任" |

---

## Phase 6: Social Tactician Tools ✅ 已完成

> 完成日期：2026-06-15 | 16 个单元测试全部通过

**文件**: `mcp-servers/social-tactician/tools.py` — 2 个方法全是 `...`

### `ice_break_suggest(target_holdings, context)`

- 4 种场景模板: market_down / market_up / specific_holding / generic
- 无行情数据时从 user_input 关键词推断市场方向
- 返回 topics + ice_breakers + market_hooks

### `deep_talk_suggest(topic, context)`

- 5 个深度话题框架:

| 话题 | opener 示例 |
|------|------------|
| 投资哲学 | "你是什么时候开始意识到，投资其实是在投自己对这个世界的认知？" |
| 风险认知 | "你觉得自己能承受的最大回撤是多少？不是理性上的，是心理上的。" |
| 市场周期 | "你有没有发现，每次你忍不住想买的时候，往往是阶段高点？" |
| 交易心理 | "你觉得交易中最难控制的情绪是什么？贪婪还是恐惧？" |
| 生活平衡 | "除了看盘，你最近一次完全忘记股票是什么时候？" |

- 每个框架含: opener + bridge + core_theme + closer + discussion_points + pitfalls（社交雷区指南）
- 返回结构化框架供 Phase 2 LLM 人格化生成

---

## 验证策略

每个 Phase 完成后新建对应测试文件：

```
tests/
  test_memory_store.py
  test_meme_library.py
  test_market_terms.py
  test_retriever.py
  test_life_service_tools.py
  test_psychology_mirror_tools.py
  test_meme_comfort_tools.py
  test_social_tactician_tools.py
```

- 纯 Python 标准库（`unittest`），无需外部服务
- 时间敏感测试 mock `datetime.now()`
- Memory store 使用 `:memory:` SQLite
- 每个 Phase 完成后可独立跑通验证
