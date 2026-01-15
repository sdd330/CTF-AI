/**
 * GameLoop - 游戏循环管理器
 * 负责游戏更新循环、tick 处理和状态更新
 */
import Phaser from 'phaser'
import type { Team, PlayerActions } from '@/types'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { SocketManager } from '../../managers/SocketManager'
import { PathVisualizationManager } from '../../managers/PathVisualizationManager'
import { WorldManager } from '../../managers/WorldManager'
import { InputManager } from '../../managers/InputManager'
import { PlayerInfoUpdater } from './PlayerInfoUpdater'
import { PathVisualizationUpdater } from './PathVisualizationUpdater'

/**
 * 游戏循环管理器
 */
export class GameLoop {
  private socketManager: SocketManager
  private pathVisualizationManager: PathVisualizationManager
  private lteamInputManager: InputManager | null
  private rteamInputManager: InputManager | null
  private world: WorldManager
  private lteamPlayers: Phaser.GameObjects.Group
  private rteamPlayers: Phaser.GameObjects.Group
  private lteamFlags: Phaser.GameObjects.Group
  private rteamFlags: Phaser.GameObjects.Group
  private playerInfoUpdater: PlayerInfoUpdater
  private pathVisualizationUpdater: PathVisualizationUpdater
  
  // 状态跟踪
  private stageSent = false
  private lastSendTime = 0
  private gameStartTime = 0 // 游戏开始的时间点

  constructor(
    world: WorldManager,
    socketManager: SocketManager,
    pathVisualizationManager: PathVisualizationManager,
    lteamInputManager: InputManager | null,
    rteamInputManager: InputManager | null,
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group
  ) {
    this.world = world
    this.socketManager = socketManager
    this.pathVisualizationManager = pathVisualizationManager
    this.lteamInputManager = lteamInputManager
    this.rteamInputManager = rteamInputManager
    this.lteamPlayers = lteamPlayers
    this.rteamPlayers = rteamPlayers
    this.lteamFlags = lteamFlags
    this.rteamFlags = rteamFlags
    this.playerInfoUpdater = new PlayerInfoUpdater(pathVisualizationManager, lteamPlayers, rteamPlayers)
    this.pathVisualizationUpdater = new PathVisualizationUpdater(pathVisualizationManager, lteamPlayers, rteamPlayers)
  }

  /**
   * 更新游戏循环
   */
  update(time: number, delta: number): boolean {
    // 更新输入管理器（处理键盘和远程控制）
    if (this.lteamInputManager) {
      this.lteamInputManager.update()
    }
    if (this.rteamInputManager) {
      this.rteamInputManager.update()
    }
    
    // 检查游戏是否已开始
    const gameStarted = this.world.getState().gameStarted
    if (!gameStarted) {
      this.gameStartTime = 0 // 重置游戏开始时间
      return false
    }
    
    // 记录游戏开始时间（只记录一次）
    if (this.gameStartTime === 0) {
      this.gameStartTime = time
    }

    const gamePaused = this.world.getState().gamePaused
    if (gamePaused) {
      return false
    }

    // 处理游戏 tick
    const canSendStatus = this.handleGameTick(time, delta)
    
    // 发送状态更新
    if (canSendStatus && !this.stageSent && time - this.lastSendTime >= 600) {
      this.stageSent = true
      this.lastSendTime = time
      // 发送相对时间（从游戏开始算起）
      const relativeTime = time - this.gameStartTime
      this.sendStatusUpdate(relativeTime)
    }
    
    // 更新路径可视化
    this.updatePathVisualization()
    
    return true
  }

  /**
   * 处理游戏 tick（玩家移动）
   */
  private handleGameTick(time: number, delta: number): boolean {
    let playersReady = 0
    let totalPlayers = 0
    const EPSILON = 0.1

    const tick = (canGoNextTile: boolean) => {
      this.lteamPlayers.getChildren().forEach((child: Phaser.GameObjects.GameObject) => {
        const player = child as Player
        totalPlayers++
        player.setCanGoNextTile(canGoNextTile)
        player.update(time, delta)
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const dx = Math.abs(playerSprite.x - player.target.x)
        const dy = Math.abs(playerSprite.y - player.target.y)
        if (dx < EPSILON && dy < EPSILON) {
          playersReady++
        }
      })

      this.rteamPlayers.getChildren().forEach((child: Phaser.GameObjects.GameObject) => {
        const player = child as Player
        totalPlayers++
        player.setCanGoNextTile(canGoNextTile)
        player.update(time, delta)
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const dx = Math.abs(playerSprite.x - player.target.x)
        const dy = Math.abs(playerSprite.y - player.target.y)
        if (dx < EPSILON && dy < EPSILON) {
          playersReady++
        }
      })
    }

    tick(false)

    if (playersReady !== totalPlayers) {
      this.stageSent = false
      return false
    }

    tick(true)
    return true
  }

  /**
   * 更新路径可视化
   */
  private updatePathVisualization(): void {
    const playerPaths = this.playerInfoUpdater.getPlayerPaths()
    this.pathVisualizationUpdater.updatePathVisualization(playerPaths)
  }

  /**
   * 发送状态更新
   */
  private sendStatusUpdate(time: number): void {
    if (!this.lteamPlayers || !this.rteamPlayers || !this.lteamFlags || !this.rteamFlags || !this.socketManager) {
      return
    }
    
    const lteamPlayerStatus = (this.lteamPlayers.getChildren() as Player[]).map(p => p.getStatus())
    const lteamFlagStatus = (this.lteamFlags.getChildren() as Flag[]).map(f => f.getStatus())
    const rteamPlayerStatus = (this.rteamPlayers.getChildren() as Player[]).map(p => p.getStatus())
    const rteamFlagStatus = (this.rteamFlags.getChildren() as Flag[]).map(f => f.getStatus())

    this.socketManager.sendGameStatus({
      time,
      lteamPlayerStatus,
      lteamFlagStatus,
      rteamPlayerStatus,
      rteamFlagStatus
    })
  }

  /**
   * 更新玩家信息（从服务器接收）
   */
  updatePlayerInfo(teamName: Team, data: PlayerActions): void {
    this.playerInfoUpdater.updatePlayerInfo(teamName, data)
  }

  /**
   * 重置状态
   */
  reset(): void {
    this.stageSent = false
    this.lastSendTime = 0
    this.gameStartTime = 0 // 重置游戏开始时间
    this.playerInfoUpdater.clearAllPaths()
  }

  /**
   * 清除所有路径
   */
  clearAllPaths(): void {
    this.playerInfoUpdater.clearAllPaths()
    if (this.pathVisualizationManager) {
      this.pathVisualizationManager.clearAllPaths()
    }
  }
}
