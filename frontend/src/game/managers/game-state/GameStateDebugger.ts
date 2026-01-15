/**
 * GameStateDebugger - 游戏状态调试器
 * 职责：提供调试工具和日志功能
 */
import type { GameState } from './types'
import type { LogLevel, DebugInfo } from '@/types'

export class GameStateDebugger {
  private getState: () => GameState

  constructor(getState: () => GameState) {
    this.getState = getState
  }

  getDebugInfo(): DebugInfo {
    const state = this.getState()
    return {
      gameState: state.flowState,
      players: state.lTeamPlayers.length + state.rTeamPlayers.length,
      flags: state.lTeamFlags.length + state.rTeamFlags.length,
      connections: {
        L: state.lTeamConnected,
        R: state.rTeamConnected
      }
    }
  }

  /**
   * 记录调试日志（分级日志系统）
   */
  log(level: LogLevel, message: string, data?: unknown): void {
    const timestamp = new Date().toISOString()
    const prefix = `[WorldManager:${level.toUpperCase()}]`
    
    switch (level) {
      case 'debug':
        // 使用 Vite 的环境变量，更符合项目实践
        if (import.meta.env.DEV) {
          console.debug(`${prefix} ${timestamp}`, message, data || '')
        }
        break
      case 'info':
        console.info(`${prefix} ${timestamp}`, message, data || '')
        break
      case 'warn':
        console.warn(`${prefix} ${timestamp}`, message, data || '')
        break
      case 'error':
        console.error(`${prefix} ${timestamp}`, message, data || '')
        break
    }
  }
}
