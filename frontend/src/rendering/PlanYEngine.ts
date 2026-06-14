/**
 * 方案Y 渲染引擎 — 三轨同步播放控制器。
 *
 * 职责:
 *   - 接收后端 WebSocket 推送的 PlanYFrame 序列
 *   - 协调视觉轨（图片加载/切换）、文本轨（打字机动效）、听觉轨（TTS 播放）
 *   - 三轨同步：打字机速度与 TTS 朗读进度对齐
 *   - 支持中断当前播放，切换到下一帧
 */

import type { PlanYFrame, RenderState } from './types';

export interface PlanYEngine {
  /** 当前渲染状态 */
  readonly state: RenderState;

  /** 播放一帧 */
  play(frame: PlanYFrame): void;

  /** 中断当前播放 */
  interrupt(): void;

  /** 帧播放完成回调 */
  onFrameEnd: (() => void) | null;

  /** 渲染错误回调 */
  onError: ((error: Error) => void) | null;
}
