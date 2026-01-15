/**
 * ConfigStateDomain - 游戏配置状态域
 * 职责：管理游戏配置状态
 */
import type { GameConfig, GameState } from './types'

export class ConfigStateDomain {
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
   * 加载游戏配置（从 game_config.json）
   * 如果加载失败，使用默认配置
   */
  async loadConfig(configPath: string = 'game_config.json'): Promise<GameConfig> {
    try {
      const resp = await fetch(configPath)
      if (!resp.ok) {
        throw new Error(`无法加载 ${configPath}: HTTP ${resp.status}`)
      }

      const text = await resp.text()
      if (!text || text.trim().length === 0) {
        throw new Error(`${configPath} 返回空内容`)
      }

      const data: GameConfig = JSON.parse(text)

      if (!data.setup) {
        throw new Error(`${configPath} 缺少 'setup' 字段`)
      }

      console.log('[ConfigStateDomain] 配置加载成功:', data)
      
      this.setConfig(data)
      this.updateState({
        configLoaded: true
      })

      return data
    } catch (error) {
      console.error(`[ConfigStateDomain] 加载配置失败，使用默认配置:`, error)
      
      const defaultConfig: GameConfig = {
        teams: [{ name: 'L', who: 'user48-1' }, { name: 'R', who: 'user48-2' }],
        setup: {
          numPlayers: 3,
          numFlags: 9,
          useRandomFlags: true,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {
          "user48-1": "ws://localhost:34712",
          "user48-2": "ws://localhost:34713"
        }
      }
      
      this.setConfig(defaultConfig)
      this.updateState({
        configLoaded: true
      })

      return defaultConfig
    }
  }

  getConfig(): GameConfig | null {
    return this.getState().config
  }

  setConfig(config: GameConfig): void {
    this.updateState({
      config,
      numPlayers: config.setup.numPlayers,
      numFlags: config.setup.numFlags,
      useRandomFlags: config.setup.useRandomFlags
    })
  }
}
