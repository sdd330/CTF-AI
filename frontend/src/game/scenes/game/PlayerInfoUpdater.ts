/**
 * PlayerInfoUpdater - 玩家信息更新器
 * 负责处理从服务器接收的玩家动作和路径数据
 */
import type { Team, PlayerActions, Position } from '@/types'
import { Player } from '../../objects/Player'
import { PathVisualizationManager } from '../../managers/PathVisualizationManager'

/**
 * 玩家信息更新器
 */
export class PlayerInfoUpdater {
  private pathVisualizationManager: PathVisualizationManager
  private lteamPlayers: Phaser.GameObjects.Group
  private rteamPlayers: Phaser.GameObjects.Group
  private playerPaths: Map<string, Position[]> = new Map()

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
   * 更新玩家信息（从服务器接收）
   */
  updatePlayerInfo(teamName: Team, data: PlayerActions): void {
    try {
      if (!data || typeof data !== 'object') {
        console.warn(`无效的 actions 对象 from ${teamName} team:`, data)
        return
      }

      if (!data.players || typeof data.players !== 'object' || Array.isArray(data.players)) {
        if (!data.players || Array.isArray(data.players)) {
          console.warn(`无效的 players 字段 from ${teamName} team:`, data.players)
        }
        return
      }

      // 验证玩家名称和方向
      Object.keys(data.players).forEach(playerName => {
        const direction = data.players[playerName]
        if (!playerName.startsWith(teamName)) {
          console.warn(`Invalid operation to control player ${playerName} for team ${teamName}`)
          return
        }
        if (direction !== 'up' && direction !== 'down' && direction !== 'left' && direction !== 'right' && direction !== '') {
          console.warn(`Invalid operation to move player to direction ${direction}`)
          return
        }
      })

      const teamPlayers = teamName === 'L' 
        ? this.lteamPlayers.getChildren() as Player[]
        : this.rteamPlayers.getChildren() as Player[]

      if (!teamPlayers || teamPlayers.length === 0) {
        console.warn(`未找到 ${teamName} 队的玩家`)
        return
      }

      // 设置玩家动作和路径
      console.log(`[PlayerInfoUpdater] ${teamName}队 🎮 处理 ${teamPlayers.length} 个玩家`)
      teamPlayers.forEach(player => {
        const remoteControl = data.players[player.name]
        if (remoteControl !== undefined) {
          const hasPath = data.paths && data.paths[player.name] ? data.paths[player.name].length : 0
          console.log(`[PlayerInfoUpdater]   ${player.name}: 方向=${remoteControl || '无'}, 路径长度=${hasPath}`)
          if (data.paths && data.paths[player.name]) {
            player.setPlannedPath(data.paths[player.name])
          }
          player.setRemoteControl(remoteControl)
        }
      })

      // 处理路径数据
      this.processPaths(teamName, data, teamPlayers)
    } catch (e) {
      console.error(`处理 ${teamName} 队消息时出错:`, e, '原始数据:', data)
    }
  }

  /**
   * 处理路径数据
   */
  private processPaths(teamName: Team, data: PlayerActions, _teamPlayers: Player[]): void {
    if (data.paths && typeof data.paths === 'object' && !Array.isArray(data.paths)) {
      const currentTeamPlayerNames = new Set<string>()
      Object.keys(data.paths).forEach(playerName => {
        const path = data.paths![playerName]
        if (Array.isArray(path) && path.length > 0) {
          const validPath = path.filter((p: any) => p && typeof p.x === 'number' && typeof p.y === 'number')
          if (validPath.length > 0) {
            this.playerPaths.set(playerName, validPath)
            currentTeamPlayerNames.add(playerName)
          }
        }
      })
      
      // 清除当前队伍中不再有路径数据的玩家的路径
      const pathsToRemove: string[] = []
      this.playerPaths.forEach((_path, playerName) => {
        if (playerName.startsWith(teamName) && !currentTeamPlayerNames.has(playerName)) {
          pathsToRemove.push(playerName)
        }
      })
      pathsToRemove.forEach(playerName => {
        this.playerPaths.delete(playerName)
      })
    } else {
      // 如果没有路径数据，只清除当前队伍的路径
      const pathsToRemove: string[] = []
      this.playerPaths.forEach((_path, playerName) => {
        if (playerName.startsWith(teamName)) {
          pathsToRemove.push(playerName)
        }
      })
      pathsToRemove.forEach(playerName => {
        this.playerPaths.delete(playerName)
        if (this.pathVisualizationManager) {
          this.pathVisualizationManager.clearPath(playerName)
        }
      })
    }
  }

  /**
   * 获取玩家路径数据
   */
  getPlayerPaths(): Map<string, Position[]> {
    return this.playerPaths
  }

  /**
   * 清除所有路径
   */
  clearAllPaths(): void {
    this.playerPaths.clear()
  }
}
