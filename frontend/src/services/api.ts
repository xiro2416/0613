/**
 * API 客户端 — 前端与后端的通信契约。
 *
 * 通信方式:
 *   - REST:  会话管理、人设切换、用户查询
 *   - WebSocket: 消息流式推送（接收 PlanYFrame 序列）
 */

import type { PlanYFrame } from '../rendering/types';
import type { PersonaType } from '../rendering/types';

// ── REST 接口 ────────────────────────────────

export interface SessionAPI {
  /** 创建新会话 */
  createSession(userId: string): Promise<{ sessionId: string; persona: PersonaType }>;

  /** 切换人设 */
  switchPersona(sessionId: string, persona: PersonaType): Promise<void>;

  /** 获取用户画像 */
  getUserProfile(userId: string): Promise<Record<string, unknown>>;
}

// ── WebSocket 接口 ───────────────────────────

export interface AgentSocket {
  /** 建立 WebSocket 连接 */
  connect(sessionId: string): void;

  /** 发送用户消息（上行） */
  send(message: string): void;

  /** 接收 PlanYFrame 流（下行） */
  onFrame: ((frame: PlanYFrame) => void) | null;

  /** 连接关闭回调 */
  onClose: (() => void) | null;

  /** 错误回调 */
  onError: ((error: Error) => void) | null;

  /** 断开连接 */
  disconnect(): void;
}
