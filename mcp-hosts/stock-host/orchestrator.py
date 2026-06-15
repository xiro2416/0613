"""中枢编排器 — 两阶段 LLM 执行（OpenAI Compatible）。

Phase 1 (数据采集):
  用户消息 + system_prompt → LLM 选择工具 → MCP Server 返回纯数据
  支持多轮 tool calls（OpenAI 模式下 tool_calls 和 content 互斥，需循环）

Phase 2 (人格化生成):
  工具数据 + Persona system_prompt → LLM 生成最终文本 + EmotionTag

架构约定:
  - Tool 不传 Persona 参数，不返回人格化文本
  - 所有 Persona 转换集中在 Phase 2
  - 时间感知在 system_prompt 层注入
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from openai import OpenAI

from persona import PersonaManager
from rendering import PlanYPipeline
from shared.types import (
    EmotionTag,
    Message,
    PersonaType,
    PlanYFrame,
    PlanYRenderRequest,
    TimeSlot,
)
from time_gate import TimeGate


@dataclass
class OrchestratorContext:
    """编排上下文 — 一次请求的完整状态"""
    session_id: str
    user_input: str
    persona_type: PersonaType
    time_slot: TimeSlot
    conversation_history: list[Message] = field(default_factory=list)
    user_profile: Optional[dict] = None


class Orchestrator:
    """中枢编排器 — 两阶段 LLM 执行"""

    def __init__(
        self,
        client: OpenAI,
        model: str = "qwen3.7-plus",
        mcp_clients: dict[str, Any] = None,
    ):
        """
        Args:
            client: OpenAI 兼容客户端 (阿里云百炼)
            model: 模型名称
            mcp_clients: {server_name: MCPClient} 字典
        """
        self._client = client
        self._model = model
        self._mcp_clients = mcp_clients or {}
        self._time_gate = TimeGate()
        self._persona_manager = PersonaManager()
        self._renderer = PlanYPipeline()

    # ═══════════════════════════════════════════════════════════
    # 主入口
    # ═══════════════════════════════════════════════════════════

    async def process(self, ctx: OrchestratorContext) -> PlanYFrame:
        """处理用户消息 — 两阶段执行。"""
        persona_config = self._persona_manager.get_config(ctx.persona_type)
        system_prompt = self._build_system_prompt(persona_config, ctx.time_slot)

        # ── Phase 1: 数据采集 ──
        tool_results = await self._phase1_data_collection(
            system_prompt=system_prompt,
            user_input=ctx.user_input,
            history=ctx.conversation_history,
        )

        # ── Phase 2: 人格化生成 ──
        final_text, emotion_tag = await self._phase2_persona_generation(
            system_prompt=system_prompt,
            persona_type=ctx.persona_type,
            user_input=ctx.user_input,
            tool_results=tool_results,
            history=ctx.conversation_history,
        )

        # ── 方案Y 渲染 ──
        frame = self._renderer.render(PlanYRenderRequest(
            content=final_text,
            emotion_tag=emotion_tag,
            persona_type=ctx.persona_type,
        ))

        return frame

    # ═══════════════════════════════════════════════════════════
    # Phase 1: 数据采集（支持多轮 tool calls）
    # ═══════════════════════════════════════════════════════════

    async def _phase1_data_collection(
        self,
        system_prompt: str,
        user_input: str,
        history: list[Message],
    ) -> list[dict]:
        """Phase 1: LLM 选择工具 → MCP 执行 → 收集纯数据。

        OpenAI Chat Completions 模式下，tool_calls 和 content 互斥。
        需要循环：LLM 返回 tool_calls → 执行工具 → 追加结果 → 再次调 LLM。

        Returns:
            [{tool_name: str, result: dict}, ...]
        """
        tools = await self._build_tool_definitions()
        messages = self._build_messages(system_prompt, user_input, history)

        all_tool_results = []

        # 最多 3 轮 tool calls 循环
        for _ in range(3):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools if tools else None,
                max_tokens=1024,
            )

            msg = response.choices[0].message

            # 有 tool_calls → 执行并继续
            if msg.tool_calls:
                # 将 assistant 消息加入对话
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                # 执行每个 tool call
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    try:
                        tool_input = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}

                    tool_result = await self._execute_mcp_tool(
                        tool_name=tool_name,
                        tool_input=tool_input,
                    )
                    all_tool_results.append({
                        "tool_name": tool_name,
                        "result": tool_result,
                    })

                    # 将 tool 结果加入对话
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    })
            else:
                # 没有 tool_calls → 结束循环
                break

        return all_tool_results

    # ═══════════════════════════════════════════════════════════
    # Phase 2: 人格化生成
    # ═══════════════════════════════════════════════════════════

    async def _phase2_persona_generation(
        self,
        system_prompt: str,
        persona_type: PersonaType,
        user_input: str,
        tool_results: list[dict],
        history: list[Message],
    ) -> tuple[str, EmotionTag]:
        """Phase 2: 工具数据 + Persona → LLM 生成最终文本。"""
        tool_context = self._format_tool_results(tool_results)

        persona_system = (
            f"{system_prompt}\n\n"
            "以下是通过工具获取的原始数据，请根据你的角色设定，"
            "将这些数据转化为符合你人格的回复。\n\n"
            f"原始数据:\n{tool_context}\n\n"
            f"用户原始问题: {user_input}\n\n"
            "请在回复末尾附加一行情绪标签（只输出标签名，不要其他文字）："
            "标签可选: WARM / COOL / HUMOROUS / COMFORTING / SERIOUS"
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": persona_system},
                {"role": "user", "content": "请生成回复。"},
            ],
            max_tokens=512,
        )

        text = response.choices[0].message.content or ""

        # 提取情绪标签
        emotion_tag = self._extract_emotion_tag(text, persona_type)
        clean_text = self._strip_emotion_tag(text)

        return clean_text, emotion_tag

    # ═══════════════════════════════════════════════════════════
    # System Prompt 装配
    # ═══════════════════════════════════════════════════════════

    def _build_system_prompt(
        self,
        persona_config,
        time_slot: TimeSlot,
    ) -> str:
        """装配 system_prompt = 人设 Prompt + 时间上下文"""
        prompt = persona_config.system_prompt

        if time_slot == TimeSlot.TRADING_HOURS:
            prompt += (
                "\n\n现在是盘中交易时间(9:15-15:00)。用户可能在盯盘。"
                "回复应简短(≤80字)、聚焦交易，不要长篇大论。"
                "如果用户问非交易问题，温柔提醒「安心看盘，收盘后陪你聊」。"
            )
        elif time_slot == TimeSlot.POST_MARKET:
            prompt += (
                "\n\n现在是盘后时间。可以深入复盘、提供详细分析、"
                "安抚情绪。不限回复篇幅。"
            )
        else:
            prompt += (
                "\n\n现在是休市时间。陪伴式回应，关注用户身心状态。"
            )

        return prompt

    # ═══════════════════════════════════════════════════════════
    # MCP 工具集成
    # ═══════════════════════════════════════════════════════════

    async def _build_tool_definitions(self) -> list[dict]:
        """从所有 MCP Server 聚合 tool 定义（OpenAI function calling 格式）。"""
        tools = []
        for name, client in self._mcp_clients.items():
            try:
                mcp_tools = await client.list_tools()
                for t in mcp_tools:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description or "",
                            "parameters": t.inputSchema or {
                                "type": "object",
                                "properties": {},
                            },
                        },
                    })
            except Exception:
                continue
        return tools

    async def _execute_mcp_tool(self, tool_name: str, tool_input: dict) -> dict:
        """执行 MCP tool 调用。"""
        for server_name, client in self._mcp_clients.items():
            try:
                result = await client.call_tool(tool_name, tool_input)
                if result.content:
                    text = result.content[0].text
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"raw": text}
                return {}
            except Exception:
                continue
        return {"error": f"Tool '{tool_name}' not found"}

    # ═══════════════════════════════════════════════════════════
    # 消息构造
    # ═══════════════════════════════════════════════════════════

    def _build_messages(
        self,
        system_prompt: str,
        user_input: str,
        history: list[Message],
    ) -> list[dict]:
        """构造 OpenAI Chat Completions 消息列表。

        system prompt 作为第一条 role="system" 消息。
        历史消息直接映射 role + content。
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # 最近 20 条历史
        for msg in history[-20:]:
            role = "user" if msg.role == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": user_input})
        return messages

    # ═══════════════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════════════

    def _format_tool_results(self, tool_results: list[dict]) -> str:
        """格式化工具结果为 LLM 可读的文本"""
        if not tool_results:
            return "(未调用任何工具)"

        lines = []
        for item in tool_results:
            name = item.get("tool_name", "unknown")
            result = item.get("result", {})
            lines.append(f"## {name}")
            lines.append(json.dumps(result, ensure_ascii=False, indent=2))
            lines.append("")
        return "\n".join(lines)

    def _extract_emotion_tag(self, text: str, persona: PersonaType) -> EmotionTag:
        """从 LLM 输出中提取情绪标签"""
        for line in reversed(text.strip().split("\n")):
            line = line.strip()
            for tag in EmotionTag:
                if tag.value.upper() in line.upper():
                    return tag
        return self._persona_manager.map_emotion("analysis", persona)

    def _strip_emotion_tag(self, text: str) -> str:
        """移除文本末尾的情绪标签行"""
        lines = text.strip().split("\n")
        if lines and any(
            tag.value.upper() in lines[-1].strip().upper()
            for tag in EmotionTag
        ):
            return "\n".join(lines[:-1]).strip()
        return text.strip()
