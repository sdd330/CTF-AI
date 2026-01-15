/**
 * GameStateDomain - 核心游戏状态域
 * 职责：管理核心游戏状态（started, paused, over, winner）
 */
import type { Team, GameState } from './types'

export class GameStateDomain {
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
   * 开始游戏
   */
  startGame(): void {
    this.updateState({
      gameStarted: true,
      gamePaused: false,
      gameOver: false
    })
  }

  /**
   * 暂停/恢复游戏
   */
  pauseGame(): void {
    const state = this.getState()
    this.updateState({
      gamePaused: !state.gamePaused
    })
  }

  /**
   * 结束游戏
   */
  endGame(team: Team): void {
    this.updateState({
      gameOver: true,
      winner: team,
      gameStarted: false
    })
  }

  /**
   * 重置游戏状态
   */
  resetGameState(): void {
    this.updateState({
      gameStarted: false,
      gamePaused: false,
      gameOver: false,
      winner: null
    })
  }

  /**
   * 检查游戏是否活跃
   */
  isGameActive(): boolean {
    const state = this.getState()
    return state.gameStarted && !state.gamePaused && !state.gameOver
  }
}
