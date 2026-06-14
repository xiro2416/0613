/**
 * PersonaToggle — 人设即时调频滑块。
 *
 * PRD 4.2 约束:
 *   - 非开盘时段界面右上角常驻
 *   - 支持秒级切换，三个人设 GENTLE / RATIONAL / MEME
 *   - 切换时同步更新 Prompt、视觉、TTS 声线、模块路由
 */

import type { ComponentProps } from 'react';
import type { PersonaType } from '../rendering/types';

interface PersonaToggleProps {
  /** 当前活跃人设 */
  active: PersonaType;

  /** 切换回调 — 触发后端人设切换 API */
  onSwitch: (to: PersonaType) => void;

  /** 是否正在切换中 */
  isSwitching?: boolean;

  /** 是否可见（开盘时段隐藏） */
  visible?: boolean;
}

/**
 * 人设调频滑块组件 (接口)
 *
 * 渲染形态:
 *   - 三人设并排，当前选中高亮
 *   - 切换时带过渡动画
 *   - GENTLE 标记为「默认」
 *
 * 用法:
 *   <PersonaToggle
 *     active={persona}
 *     onSwitch={handleSwitch}
 *     visible={isPostMarket}
 *   />
 */
declare function PersonaToggle(props: PersonaToggleProps): JSX.Element;

export type { PersonaToggleProps };
export { PersonaToggle };
