"""MCP Host — 职业股民 AI Agent 系统唯一入口。

职责:
  - FastAPI REST: 会话管理、人设切换、用户画像
  - WebSocket:  双向流式通信（PlanYFrame 帧流）
  - MCP Client: 连接 5 个业务 MCP Server
  - 编排:      两阶段 LLM 执行（数据采集 + 人格化生成）

架构: docs/mcp-skill-migration.md
"""

import json
import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import MCP_SERVERS
from orchestrator import Orchestrator, OrchestratorContext
from persona import PersonaManager
from shared.memory.manager import MemoryManager
from shared.types import Message, PersonaType, SessionContext, TimeSlot
from time_gate import TimeGate

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# 应用初始化
# ═══════════════════════════════════════════════════════════════

app = FastAPI(title="Stock Agent MCP Host")

# LLM 客户端 — 阿里云百炼 OpenAI Compatible
llm_client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY", ""),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 共享库组件（进程内直接 import，不走 MCP）
memory_manager = MemoryManager(db_path=os.getenv("DB_PATH", "data/stock_agent.db"))
time_gate = TimeGate()
persona_manager = PersonaManager()

# MCP Client 连接池（启动时建立）
mcp_clients: dict[str, ClientSession] = {}


@app.on_event("startup")
async def startup():
    """启动时连接所有 MCP Server"""
    global mcp_clients
    for name, cfg in MCP_SERVERS.items():
        try:
            server_params = StdioServerParameters(
                command=cfg.command.split(),
                cwd=cfg.cwd,
            )
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            mcp_clients[name] = session
            print(f"[MCP] Connected to {name}")
        except Exception as e:
            print(f"[MCP] Failed to connect {name}: {e}")
            continue

    # 初始化编排器
    global orchestrator
    orchestrator = Orchestrator(
        client=llm_client,
        model=os.getenv("LLM_MODEL", "qwen3.7-plus"),
        mcp_clients=mcp_clients,
    )


@app.on_event("shutdown")
async def shutdown():
    """关闭时断开所有 MCP 连接"""
    for name, session in mcp_clients.items():
        try:
            await session.__aexit__(None, None, None)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# REST 端点
# ═══════════════════════════════════════════════════════════════

@app.post("/api/sessions")
async def create_session(user_id: str):
    """创建新会话"""
    session = memory_manager.create_session(user_id)
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "default_persona": session.active_persona.value,
        "persona_config": _persona_config_to_response(
            persona_manager.get_config(session.active_persona)
        ),
    }


@app.post("/api/sessions/{session_id}/persona")
async def switch_persona(session_id: str, persona: str):
    """切换会话人设"""
    try:
        new_persona = PersonaType(persona)
    except ValueError:
        return {"error": f"Invalid persona: {persona}"}, 400

    memory_manager.set_persona(session_id, persona)
    config = persona_manager.switch(new_persona)

    return {
        "session_id": session_id,
        "persona": persona,
        "config": _persona_config_to_response(config),
    }


@app.get("/api/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """获取用户画像"""
    profile = memory_manager.get_user_profile(user_id)
    if profile is None:
        return {"error": "User not found"}, 404
    return {
        "user_id": profile.user_id,
        "holdings": profile.holdings,
        "trading_style": profile.trading_style,
        "risk_tolerance": profile.risk_tolerance,
        "psychological_state": profile.psychological_state,
        "defense_boundary": profile.defense_boundary,
        "consecutive_losses": profile.consecutive_losses,
    }


@app.post("/api/users/{user_id}/profile")
async def update_user_profile(user_id: str, request: dict = Body(...)):
    """更新用户画像（MVP: 用户手动设置）

    可更新字段:
      - holdings: list[str]
      - trading_style: str
      - risk_tolerance: str
      - psychological_state: str
      - defense_boundary: str
      - consecutive_losses: int
    """
    # 确保用户存在
    profile = memory_manager.get_user_profile(user_id)
    if profile is None:
        profile = memory_manager.create_user_profile(user_id)

    updated = memory_manager.update_user_profile(user_id, request)
    return {
        "user_id": updated.user_id,
        "holdings": updated.holdings,
        "trading_style": updated.trading_style,
        "risk_tolerance": updated.risk_tolerance,
        "psychological_state": updated.psychological_state,
        "defense_boundary": updated.defense_boundary,
        "consecutive_losses": updated.consecutive_losses,
    }


# ═══════════════════════════════════════════════════════════════
# WebSocket — 双向流式通信
# ═══════════════════════════════════════════════════════════════

@app.websocket("/api/ws/{session_id}")
async def websocket_handler(ws: WebSocket, session_id: str):
    await ws.accept()

    # 读取会话上下文
    session = memory_manager.get_session(session_id)
    if session is None:
        await ws.send_json({"error": "Session not found"})
        await ws.close()
        return

    # 获取用户画像
    profile = memory_manager.get_user_profile(session.user_id)

    try:
        while True:
            # 接收用户消息
            raw = await ws.receive_text()
            data = json.loads(raw)
            user_input = data.get("content", "")
            if not user_input:
                continue

            # ── 时间特征 ──
            tf = time_gate.get_time_features(datetime_now())
            memory_manager.update_time_context(session_id, tf.time_slot)

            # ── 会话状态 ──
            persona_type = session.active_persona

            # ── 保存用户消息 ──
            memory_manager.append_message(session_id, Message(
                role="user",
                content=user_input,
            ))

            # ── 两阶段编排 ──
            ctx = OrchestratorContext(
                session_id=session_id,
                user_input=user_input,
                persona_type=persona_type,
                time_slot=tf.time_slot,
                conversation_history=session.conversation_history,
                user_profile=_profile_to_dict(profile),
            )

            frame = await orchestrator.process(ctx)

            # ── 保存 Agent 消息 ──
            memory_manager.append_message(session_id, Message(
                role="agent",
                content=frame.text.content,
                emotion_tag=frame.text.emotion_tag,
            ))

            # ── 推送 PlanYFrame ──
            await ws.send_json({
                "type": "plan_y_frame",
                "visual": {
                    "image_url": frame.visual.image_url,
                    "emotion_tag": frame.visual.emotion_tag.value,
                    "style_theme": frame.visual.style_theme,
                },
                "text": {
                    "content": frame.text.content,
                    "emotion_tag": frame.text.emotion_tag.value,
                    "type_speed_ms": frame.text.type_speed_ms,
                },
                "audio": {
                    "audio_url": frame.audio.audio_url,
                    "voice_profile": frame.audio.voice_profile,
                    "duration_ms": frame.audio.duration_ms,
                    "sync_text": frame.audio.sync_text,
                },
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json({"error": str(e)})
    finally:
        # 刷新会话到存储
        memory_manager.close_session(session_id)


# ═══════════════════════════════════════════════════════════════
# 辅助
# ═══════════════════════════════════════════════════════════════

def datetime_now():
    from datetime import datetime
    return datetime.now()


def _persona_config_to_response(config) -> dict:
    """将 PersonaConfig 序列化为 API 响应"""
    return {
        "persona_type": config.persona_type.value,
        "visual_style": {
            "color_palette": config.visual_style.color_palette,
            "ui_theme": config.visual_style.ui_theme,
            "art_style": config.visual_style.art_style,
        } if config.visual_style else None,
        "tts_voice": {
            "voice_id": config.tts_voice.voice_id,
            "profile": config.tts_voice.profile,
            "speed": config.tts_voice.speed,
        } if config.tts_voice else None,
        "system_prompt": config.system_prompt[:100] + "...",
    }


def _profile_to_dict(profile) -> Optional[dict]:
    if profile is None:
        return None
    return {
        "user_id": profile.user_id,
        "holdings": profile.holdings,
        "trading_style": profile.trading_style,
        "risk_tolerance": profile.risk_tolerance,
        "consecutive_losses": profile.consecutive_losses,
        "psychological_state": profile.psychological_state,
    }


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
