/**
 * 状态管理 — 前端全局状态类型定义。
 */

import type { PersonaType, PlanYFrame, RenderState } from '../rendering/types';

/** 应用全局状态 */
export interface AppState {
  // 会话
  sessionId: string | null;
  userId: string | null;

  // 人设
  activePersona: PersonaType;

  // 渲染
  renderState: RenderState;
  currentFrame: PlanYFrame | null;
  frameQueue: PlanYFrame[];

  // 时间感知
  isPostMarket: boolean;   // 是否盘后（影响功能激活）
  timeSlot: string;        // trading / post_market / weekend

  // 连接
  isConnected: boolean;
}

/** 状态操作 */
export type AppAction =
  | { type: 'SESSION_CREATED'; sessionId: string; userId: string }
  | { type: 'PERSONA_SWITCHED'; persona: PersonaType }
  | { type: 'FRAME_RECEIVED'; frame: PlanYFrame }
  | { type: 'FRAME_DONE' }
  | { type: 'RENDER_STATE'; state: RenderState }
  | { type: 'TIME_SLOT'; slot: string; isPostMarket: boolean }
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' };
