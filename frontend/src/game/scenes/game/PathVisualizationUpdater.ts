/**
 * PathVisualizationUpdater - 路径可视化更新器
 * 负责更新路径可视化显示
 */
import type { Position } from '@/types'
import { Player } from '../../objects/Player'
import { PathVisualizationManager } from '../../managers/PathVisualizationManager'

/**
 * 路径可视化更新器
 */
export class PathVisualizationUpdater {
  private pathVisualizationManager: PathVisualizationManager
  private lteamPlayers: Phaser.GameObjects.Group
  private rteamPlayers: Phaser.GameObjects.Group

  constructor(
    pathVisualizationManager: PathVisualizationManager,
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group
  ) {
    this.pathVisualizationManager = pathVisualizationManager
    this.lteamPlayers = lteamPlayers
    this.rteamPlayers = rteamPlayers
  }

  /**
   * 更新路径可视化
   */
  updatePathVisualization(playerPaths: Map<string, Position[]>): void {
    if (!this.pathVisualizationManager || !this.pathVisualizationManager.isEnabled()) {
      return
    }

    const currentPlayerNames = new Set<string>()
    
    // 更新所有有路径数据的玩家
    playerPaths.forEach((path, playerName) => {
      currentPlayerNames.add(playerName)
      if (path && path.length > 0) {
        const color = playerName.startsWith('L') ? 0xffffff : 0x000000
        this.pathVisualizationManager.setPath(playerName, path, color)
      } else {
        this.pathVisualizationManager.clearPath(playerName)
      }
    })
    
    // 清除不在当前路径数据中的玩家的路径可视化
    const pathsMap = (this.pathVisualizationManager as any).paths as Map<string, any>
    if (pathsMap) {
      pathsMap.forEach((_visualization, playerName) => {
        if (!currentPlayerNames.has(playerName)) {
          const lteamPlayers = this.lteamPlayers?.getChildren() as Player[] || []
          const rteamPlayers = this.rteamPlayers?.getChildren() as Player[] || []
          const allPlayers = [...lteamPlayers, ...rteamPlayers]
          const playerExists = allPlayers.some(p => p.name === playerName)
          
          if (!playerExists) {
            this.pathVisualizationManager.clearPath(playerName)
          }
        }
      })
    }
  }
}
