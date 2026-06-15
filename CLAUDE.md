# CLAUDE.md — 职业股民全场景陪伴式 AI Agent

## 启动时必做

每次会话启动后，**立即阅读 `docs/` 下的全部文档**，确保感知完整项目上下文：

1. `docs/stock-agent-prd.md` — PRD 原始文档（产品定位、功能定义）
2. `docs/PROGRESS.md` — 项目进度、技术栈、架构、状态
3. `docs/modules/00-core.md` — 核心中枢设计
4. `docs/modules/01-market-analyzer.md` — 行情分析模块
5. `docs/modules/02-psychology-mirror.md` — 人性对齐模块
6. `docs/modules/03-meme-comfort.md` — 心理按摩模块
7. `docs/modules/04-social-tactician.md` — 社交辅助模块
8. `docs/modules/05-life-service.md` — 生活服务模块
9. `docs/development-plan.md` — 下一步实现方案

## 项目概览

- **项目**：职业股民盘后全场景陪伴式 AI Agent
- **架构**：MCP Host (Python FastAPI) + 5 个 MCP Server（进程隔离）+ React 前端
- **传输**：MCP STDIO 协议
- **共享库**：`shared/` — knowledge / market_data / memory

## 目录结构

| 目录 | 说明 |
|------|------|
| `docs/` | 项目文档（PRD、进度、各模块设计） |
| `mcp-hosts/stock-host/` | Host 编排层（入口、编排器、时间门控、人设、渲染） |
| `mcp-servers/` | 5 个业务 MCP Server |
| `shared/` | 共享库（知识库、行情数据、记忆系统） |
| `frontend/` | 前端 TypeScript + React + Vite |

## 关键约束

- 开盘时段（9:15–15:00）静默，仅保留基础能力
- 盘后（15:00–次日 09:15）全量激活
- 全域禁止纯文本输出，强制执行三轨多模态渲染（视觉+动效文本+听觉）
- 三个人格（GENTLE / RATIONAL / MEME）状态机隔离，切换时全维度同步

## 工作 Tips

- 修改前先查阅对应 `docs/modules/` 文档确认设计意图
- 涉及多个 MCP Server 或 Host 的改动，需同时更新 `docs/PROGRESS.md`
- **每完成一个模块的计划或实现，必须同步更新对应的 md 文档**（development-plan 标记完成状态、PROGRESS 更新进度、modules 文档补充实现细节）
