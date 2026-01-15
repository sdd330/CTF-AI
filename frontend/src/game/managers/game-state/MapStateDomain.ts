/**
 * MapStateDomain - 地图状态域
 * 职责：管理地图数据（walls, obstacles）
 */
import type { Position, GameState } from './types'

export class MapStateDomain {
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
   * 设置地图数据
   */
  setMapData(data: {
    walls?: Array<Position & { tileId?: number }>
    obstacles1?: Position[]
    obstacles2?: Position[]
  }): void {
    this.updateState(data)
  }

  /**
   * 重置地图数据（地图参数由 MapManager 管理，不在此重置）
   */
  resetMapState(): void {
    this.updateState({
      walls: [],
      obstacles1: [],
      obstacles2: []
    })
  }
}
