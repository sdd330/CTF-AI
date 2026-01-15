/**
 * GameFlowController - 游戏流程控制器
 * 负责游戏的启动、暂停、重启和结束流程
 */
import type Phaser from 'phaser'
import type { Team, GameConfig } from '@/types'
import { WorldManager } from '../../managers/WorldManager'
import type { GameInitializer } from './GameInitializer'

export class GameFlowController {
  private wasGameOver = false

  constructor(
    private world: WorldManager,
    private scene: Phaser.Scene,
    private initializer: GameInitializer,
    private onSetGameObjects: () => void
  ) {}

  getWasGameOver(): boolean {
    return this.wasGameOver
  }
  setWasGameOver(value: boolean): void {
    this.wasGameOver = value
  }

  startOrPauseOrContinue(): void {
    const gameStarted = this.world.getState().gameStarted
    if (gameStarted) {
      console.log('[Game] 游戏已经开始，忽略空格键')
      return
    }
    console.log('[Game] 用户按下空格键，开始游戏')
    this.startGame()
  }

  private startGame(): void {
    this.world.api.startGame()
    this.initializer.uiManager.hideComponent('tutorial')
    WorldManager.sendFlowEvent({ type: 'START_GAME' })

    console.log('[GameFlowController] 🎮 游戏开始，准备发送 init 给后端...')

    const mapParams = this.initializer.mapManager.getMapParams()
    const walls = this.initializer.mapManager.getWalls()
    const obstacles = this.initializer.mapManager.getObstacles()
    const teamStates = this.world.api.getTeamStates()
    
    console.log('[GameFlowController] Init 参数:', {
      地图: `${mapParams.mapWidth}x${mapParams.mapHeight}`,
      墙: walls.length,
      L队玩家: teamStates.lTeamState.players.length,
      R队玩家: teamStates.rTeamState.players.length,
      L队prison: teamStates.lTeamState.prison,
      L队target: teamStates.lTeamState.target,
      prison是数组: Array.isArray(teamStates.lTeamState.prison),
      target是数组: Array.isArray(teamStates.lTeamState.target)
    })
    
    this.initializer.socketManager.sendGameInit({
      mapWidth: mapParams.mapWidth,
      mapHeight: mapParams.mapHeight,
      walls: walls,
      obstacles1: obstacles.obstacles1,
      obstacles2: obstacles.obstacles2,
      lteamPrison: teamStates.lTeamState.prison,
      lteamTarget: teamStates.lTeamState.target,
      rteamPrison: teamStates.rTeamState.prison,
      rteamTarget: teamStates.rTeamState.target
    })
    console.log('[Game] 游戏已开始，由服务器完全控制')
  }

  gameOver(team: Team): void {
    this.world.api.endGame(team)
    this.initializer.uiManager.updateComponent('gameOver', `${team}Team`)
    this.initializer.uiManager.showComponent('gameOver')
    this.wasGameOver = true
    WorldManager.sendFlowEvent({ type: 'END_GAME', winner: team })
    this.initializer.socketManager.sendGameFinished()
  }

  restartGame(lteamPlayers: Phaser.GameObjects.Group, rteamPlayers: Phaser.GameObjects.Group, lteamFlags: Phaser.GameObjects.Group, rteamFlags: Phaser.GameObjects.Group, lteamTargetZone: Phaser.GameObjects.Zone, rteamTargetZone: Phaser.GameObjects.Zone, lteamPrisonZone: Phaser.GameObjects.Zone, rteamPrisonZone: Phaser.GameObjects.Zone, gameLoop: any): void {
    console.log('[Game] 开始重置游戏...')
    try {
      this.world.getState()
    } catch (error) {
      console.error('[Game] 无法重置游戏：WorldManager 未初始化或 game 对象不存在', error)
      return
    }
    try {
      if (gameLoop) {
        gameLoop.clearAllPaths()
      }
    } catch (error) {
      console.warn('[Game] 清除路径可视化时出错（可忽略）:', error)
    }
    try {
      if (lteamPlayers && typeof lteamPlayers.clear === 'function') {
        lteamPlayers.clear(true, true)
      }
      if (rteamPlayers && typeof rteamPlayers.clear === 'function') {
        rteamPlayers.clear(true, true)
      }
      if (lteamFlags && typeof lteamFlags.clear === 'function') {
        lteamFlags.clear(true, true)
      }
      if (rteamFlags && typeof rteamFlags.clear === 'function') {
        rteamFlags.clear(true, true)
      }
    } catch (error) {
      console.warn('[Game] 清理游戏对象时出错（可忽略）:', error)
    }
    try {
      if (this.initializer?.uiManager) {
        this.initializer.uiManager.hideComponent('gameOver')
        this.initializer.uiManager.showComponent('tutorial')
        this.initializer.uiManager.updateComponent('lScore', 0)
        this.initializer.uiManager.updateComponent('rScore', 0)
      }
    } catch (error) {
      console.warn('[Game] 重置 UI 时出错（可忽略）:', error)
    }
    if (gameLoop) {
      gameLoop.reset()
    }
    try {
      this.world.api.resetGameState()
      this.world.api.resetTeamStates()
      this.world.api.resetMapState()
    } catch (error) {
      console.error('[Game] 重置游戏状态时出错:', error)
      return
    }
    let config: GameConfig | null = null
    try {
      const state = this.world.getState()
      config = state?.config || null
    } catch (error) {
      console.error('[Game] 获取配置时出错:', error)
      config = null
    }
    if (!config) {
      console.error('[Game] 重启游戏时配置不存在，需要重新加载配置')
      this.initializer.setConfigLoaded(false)
      this.initializer.loadGameConfig().catch((error: Error) => {
        console.error('[Game] 重置游戏时配置加载失败:', error)
      })
      return
    }
    try {
      this.initializer.initVariables()
      this.initializer.initGame()
      this.onSetGameObjects()
      this.initializer.initPhysics(lteamPlayers, rteamPlayers, lteamFlags, rteamFlags, lteamTargetZone, rteamTargetZone, lteamPrisonZone, rteamPrisonZone)
      console.log('[Game] 游戏重置完成，等待用户按空格键开始新游戏')
    } catch (initError) {
      console.error('[Game] 重新初始化游戏时出错:', initError)
      this.initializer.setConfigLoaded(false)
      this.initializer.loadGameConfig().catch((loadError: Error) => {
        console.error('[Game] 重新加载配置失败:', loadError)
      })
    }
  }
}
