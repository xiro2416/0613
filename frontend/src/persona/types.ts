/**
 * 人设系统 — 前端类型定义
 *
 * 视觉规范 (PRD 4.2):
 *   GENTLE:   暖色调、低饱和度、柔和治愈   → 居家陪伴/托腮聆听/温柔眼神
 *   RATIONAL: 科技蓝、高冷工业风、极简干净 → 职业正装/会议室/专业分析
 *   MEME:     高饱和撞色、年轻化街头风     → 夸张搞笑/自嘲松弛
 */

import type { PersonaType } from '../rendering/types';

/** Instant Toggle 滑块状态 */
export interface PersonaToggleState {
  active: PersonaType;
  available: PersonaType[];
  isSwitching: boolean;  // 切换动画进行中
}

/** 人设切换事件 */
export interface PersonaSwitchEvent {
  previous: PersonaType;
  current: PersonaType;
}
