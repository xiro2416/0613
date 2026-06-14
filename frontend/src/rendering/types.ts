/**
 * 方案Y 渲染管线 — 前端类型定义
 *
 * 后端 WebSocket 推送 PlanYFrame，前端三轨同步播放：
 *   1. 视觉轨 — 静态原画作为背景，根据 emotionTag 淡入切换
 *   2. 文本轨 — 在原画对话框区域以打字机动效逐字展示
 *   3. 听觉轨 — 播放 TTS 音频，与打字机速度同步
 */

/** 人设标识 */
export type PersonaType = 'gentle' | 'rational' | 'meme';

/** 情绪标签 */
export type EmotionTag = 'warm' | 'cool' | 'humorous' | 'comforting' | 'serious';

/** 视觉轨 */
export interface VisualTrack {
  imageUrl: string;
  emotionTag: EmotionTag;
  styleTheme: string;
}

/** 动效文本轨 */
export interface TextTrack {
  content: string;
  emotionTag: EmotionTag;
  typeSpeedMs: number;  // 打字速度（毫秒/字）
}

/** 听觉轨 */
export interface AudioTrack {
  audioUrl: string;
  voiceProfile: string;
  durationMs: number;
  syncText: string;     // 同步文本（供字音对齐）
}

/** 方案Y 单帧 — 三轨数据的最小传输单元 */
export interface PlanYFrame {
  visual: VisualTrack;
  text: TextTrack;
  audio: AudioTrack;
}

/** 渲染引擎状态 */
export type RenderState =
  | 'idle'
  | 'loading'     // 视觉轨图片加载中
  | 'playing'     // 三轨播放中
  | 'paused'
  | 'done';
