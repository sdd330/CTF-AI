/**
 * FlowStateDomain - 游戏流程状态域
 * 职责：管理游戏流程状态（loading, ready, playing, ended）
 */
import type { GameFlowEvent, GameFlowState, GameState } from './types'

export class FlowStateDomain {
  private getState: () => GameState
  private updateState: (updates: Partial<GameState>) => void

  constructor(
    getState: () => GameState,
    updateState: (updates: Partial<GameState>) => void
  ) {
    this.getState = getState
    this.updateState = updateState
  }

  /**
   * 发送流程事件
   */
  sendFlowEvent(event: GameFlowEvent): void {
    const state = this.getState()
    
    switch (event.type) {
      case 'ASSETS_LOADED':
        if (state.flowState === 'loading' && state.flowSubState === 'loadingAssets') {
          this.updateState({
            assetsLoaded: true,
            flowSubState: 'loadingConfig'
          })
        }
        break

      case 'CONFIG_LOADED':
        if (state.flowState === 'loading' && state.flowSubState === 'loadingConfig') {
          this.updateState({
            configLoaded: true,
            initialized: true,
            flowState: 'ready',
            flowSubState: null,
            currentScene: 'Game'
          })
        }
        break

      case 'START_GAME':
        if (state.flowState === 'ready' && state.assetsLoaded && state.configLoaded && state.initialized) {
          this.updateState({
            flowState: 'playing',
            flowSubState: 'running',
            currentScene: 'Game'
          })
        }
        break

      case 'PAUSE_GAME':
        if (state.flowState === 'playing' && state.flowSubState === 'running') {
          this.updateState({
            flowSubState: 'paused'
          })
        }
        break

      case 'RESUME_GAME':
        if (state.flowState === 'playing' && state.flowSubState === 'paused') {
          this.updateState({
            flowSubState: 'running'
          })
        }
        break

      case 'END_GAME':
        this.updateState({
          flowState: 'ended',
          flowSubState: null,
          winner: event.winner,
          currentScene: 'GameOver'
        })
        break

      case 'RESTART':
        this.updateState({
          flowState: 'playing',
          flowSubState: 'running',
          currentScene: 'Game',
          gameOver: false,
          winner: null,
          error: null
        })
        break

      case 'RESTART_LOADING':
        this.updateState({
          flowState: 'loading',
          flowSubState: 'loadingAssets',
          currentScene: 'Preloader',
          initialized: false,
          assetsLoaded: false,
          configLoaded: false,
          winner: null,
          error: null
        })
        break

      case 'ERROR':
        this.updateState({
          error: event.error,
          flowState: 'loading',
          flowSubState: 'loadingAssets',
          currentScene: 'Preloader'
        })
        break
    }
  }

  /**
   * 设置流程状态
   */
  setFlowState(state: GameFlowState): void {
    this.updateState({ flowState: state })
  }
}
