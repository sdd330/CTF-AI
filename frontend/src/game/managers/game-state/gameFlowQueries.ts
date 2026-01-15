/**
 * 状态查询辅助函数
 */
import type { GameState } from './types'

export const gameFlowQueries = {
  // 检查是否在加载状态
  isLoading: (state: GameState) => {
    return state.flowState === 'loading'
  },
  // 检查是否在游戏中
  isPlaying: (state: GameState) => {
    return state.flowState === 'playing'
  },
  // 检查是否暂停
  isPaused: (state: GameState) => {
    return state.flowState === 'playing' && state.flowSubState === 'paused'
  },
  // 检查是否运行中
  isRunning: (state: GameState) => {
    return state.flowState === 'playing' && state.flowSubState === 'running'
  },
  // 检查是否已结束
  isEnded: (state: GameState) => {
    return state.flowState === 'ended'
  },
  // 检查是否准备就绪
  isReady: (state: GameState) => {
    return state.flowState === 'ready'
  }
}
