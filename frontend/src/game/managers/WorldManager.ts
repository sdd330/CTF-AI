import Phaser from 'phaser'
import { GameStateAPI } from './game-state/GameStateAPI'
import { initialState, REGISTRY_KEYS, type GameState, type GameFlowEvent } from './game-state/types'

export class WorldManager {
  private static instance: WorldManager | null = null
  private game: Phaser.Game | null = null
  readonly api: GameStateAPI

  private constructor() {
    this.api = new GameStateAPI(
      () => this.getState(),
      (updates) => this.updateState(updates)
    )
  }

  static initialize(game: Phaser.Game): WorldManager {
    if (!WorldManager.instance) {
      WorldManager.instance = new WorldManager()
    }
    WorldManager.instance.game = game
    
    if (!game.registry.has(REGISTRY_KEYS.GAME_STATE)) {
      game.registry.set(REGISTRY_KEYS.GAME_STATE, { ...initialState })
    }
    
    return WorldManager.instance
  }

  static getInstance(): WorldManager {
    if (!WorldManager.instance) {
      throw new Error('WorldManager 未初始化，请先调用 initialize(game)')
    }
    return WorldManager.instance
  }

  getState(): GameState {
    if (!this.game) {
      throw new Error('WorldManager 未初始化')
    }
    return this.game.registry.get(REGISTRY_KEYS.GAME_STATE) as GameState
  }

  private updateState(updates: Partial<GameState>): void {
    if (!this.game) {
      throw new Error('WorldManager 未初始化')
    }
    const currentState = this.getState()
    const newState = { ...currentState, ...updates }
    this.game.registry.set(REGISTRY_KEYS.GAME_STATE, newState)
    this.game.events.emit('gameStateChanged', newState)
  }

  onStateChange(callback: (state: GameState) => void): () => void {
    if (!this.game) {
      throw new Error('WorldManager 未初始化')
    }
    this.game.events.on('gameStateChanged', callback)
    return () => {
      if (this.game) {
        this.game.events.off('gameStateChanged', callback)
      }
    }
  }

  reset(): void {
    const state = this.getState()
    this.updateState({
      ...initialState,
      config: state.config
    })
  }

  static sendFlowEvent(event: GameFlowEvent): void {
    try {
      const manager = WorldManager.getInstance()
      manager.api.sendFlowEvent(event)
    } catch (error) {
      console.warn('[WorldManager] 发送流程事件失败，WorldManager 未初始化:', error)
    }
  }
}

