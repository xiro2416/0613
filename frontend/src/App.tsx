/**
 * App — 根组件。
 *
 * 布局结构:
 *   ┌──────────────────────────────────┐
 *   │  [右上] PersonaToggle             │
 *   ├──────────────────────────────────┤
 *   │                                  │
 *   │   PlanY 渲染区                    │
 *   │   - 静态原画背景                  │
 *   │   - 对话框（打字机动效文本）       │
 *   │                                  │
 *   ├──────────────────────────────────┤
 *   │  [底部] 消息输入框                │
 *   └──────────────────────────────────┘
 */

import type { PersonaToggleProps } from './persona/PersonaToggle';
import type { PlanYEngine } from './rendering/PlanYEngine';
import type { AppState } from './stores/types';

export interface AppProps {
  /** 方案Y 渲染引擎实例 */
  engine: PlanYEngine;

  /** 人设切换回调 */
  onPersonaSwitch: PersonaToggleProps['onSwitch'];

  /** 用户发送消息回调 */
  onSendMessage: (text: string) => void;

  /** 全局状态 */
  state: AppState;
}

declare function App(props: AppProps): JSX.Element;
export default App;
