# 模块一：行情分析及买卖建议大脑

> 核心定位：群体认知偏差修正器、非结构化信息智能萃取机

## 接口状态 ✅

- 文件：`backend/modules/market_analyzer.py`
- 类：`MarketAnalyzer(BaseModule)`
- 模块名：`market_analyzer`
- 方法：`process(context: ModuleContext) -> ModuleResult`

## 人设路由策略

| 人设 | 激活方式 | 置信度权重 |
|---|---|---|
| GENTLE | 轻量参与，温和提示 | 低 |
| RATIONAL | **强触发**，主导路由 | **最高** |
| MEME | 默认禁用 | — |

## 依赖

- `services/market_data.py` — 行情数据服务（**直接依赖**，高频结构化数据）
- `KnowledgeManager → market_narratives` — 市场历史叙事（纯文本，高度抽象）
- `KnowledgeManager → market_terms` — 术语库/研报（非结构化知识）
- `memory/manager.py` — 用户持仓/画像

## 核心职责（PRD 定义）

1. 清洗龙虎榜、市场公告、舆情资讯、圈层信息流
2. 剥离无效市场噪音，量化输出市场赚钱/亏钱效应
3. 输出大白话、可落地的次日操作边界
4. 强制修正认知偏差，规范交易决策逻辑

## 待定功能细节

1. 数据源接入方式（API 拉取 vs 爬虫）？更新频率？
2. 非结构化数据清洗的具体策略？
3. 市场情绪量化模型选型？
4. "操作边界"的输出格式和粒度？
5. 如何识别用户的赌徒心理/主观臆断？

## 下次工作入口

1. 确认数据源和清洗策略
2. 设计 `process()` 的内部处理链路
3. 定义 `ModuleResult.metadata` 的具体结构（操作边界数据格式）
