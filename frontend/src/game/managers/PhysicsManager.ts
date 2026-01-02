/**
 * PhysicsManager - 物理系统管理器
 * 设计模式：策略模式 + 观察者模式
 * 
 * 职责：
 * - 管理物理世界的配置
 * - 设置碰撞检测
 * - 处理碰撞逻辑（玩家碰撞、旗帜收集、旗帜放置、玩家释放）
 * 
 * 单一职责原则：物理系统相关的逻辑统一管理
 */
import Phaser from 'phaser'
import type { Team, Position } from '@/types'
import { Player } from '../objects/Player'
import { Flag } from '../objects/Flag'
import { GameStateManager } from './GameStateManager'
import { MapManager } from './MapManager'

// 碰撞回调接口（用于需要场景特定操作的回调）
export interface CollisionCallbacks {
  onScoreUpdate?: (team: Team) => void
  onCreateFlag?: (scene: Phaser.Scene, x: number, y: number, team: Team, canPickup: boolean) => Flag
}

// 物理系统管理器
export class PhysicsManager {
  private scene: Phaser.Scene
  private callbacks: CollisionCallbacks
  private mapManager: MapManager | null = null
  private lteamPlayers: Phaser.GameObjects.Group | null = null
  private rteamPlayers: Phaser.GameObjects.Group | null = null
  private lteamFlags: Phaser.GameObjects.Group | null = null
  private rteamFlags: Phaser.GameObjects.Group | null = null

  constructor(scene: Phaser.Scene, callbacks: CollisionCallbacks = {}) {
    this.scene = scene
    this.callbacks = callbacks
  }

  /**
   * 设置地图渲染器和游戏对象组（用于碰撞处理）
   */
  setGameObjects(
    mapManager: MapManager,
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group
  ): void {
    this.mapManager = mapManager
    this.lteamPlayers = lteamPlayers
    this.rteamPlayers = rteamPlayers
    this.lteamFlags = lteamFlags
    this.rteamFlags = rteamFlags
  }

  /**
   * 设置碰撞检测
   * @param lteamPlayers L队玩家组
   * @param rteamPlayers R队玩家组
   * @param lteamFlags L队旗帜组
   * @param rteamFlags R队旗帜组
   * @param lteamTargetZone L队目标区域
   * @param rteamTargetZone R队目标区域
   * @param lteamPrisonZone L队监狱区域
   * @param rteamPrisonZone R队监狱区域
   */
  setupCollisions(
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group,
    lteamTargetZone: Phaser.GameObjects.Zone,
    rteamTargetZone: Phaser.GameObjects.Zone,
    lteamPrisonZone: Phaser.GameObjects.Zone,
    rteamPrisonZone: Phaser.GameObjects.Zone
  ): void {
    // 玩家之间的碰撞
    this.scene.physics.add.overlap(
      lteamPlayers,
      rteamPlayers,
      this.handlePlayerHit.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )

    // 玩家收集旗帜
    this.scene.physics.add.overlap(
      lteamPlayers,
      rteamFlags,
      this.handleFlagCollected.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      lteamFlags,
      this.handleFlagCollected.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )

    // 玩家放置旗帜
    this.scene.physics.add.overlap(
      lteamPlayers,
      lteamTargetZone,
      this.handleFlagDropped.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      rteamTargetZone,
      this.handleFlagDropped.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )

    // 玩家释放队友
    this.scene.physics.add.overlap(
      lteamPlayers,
      lteamPrisonZone,
      this.handlePlayerFreed.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      rteamPrisonZone,
      this.handlePlayerFreed.bind(this) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )
  }

  /**
   * 为物理对象添加物理体
   * @param gameObject 游戏对象
   * @param allowGravity 是否允许重力
   * @param immovable 是否不可移动
   */
  addPhysicsBody(
    gameObject: Phaser.GameObjects.GameObject,
    allowGravity: boolean = false,
    immovable: boolean = true
  ): void {
    this.scene.physics.add.existing(gameObject)
    const sprite = gameObject as Phaser.Physics.Arcade.Sprite
    if (sprite.body && sprite.body instanceof Phaser.Physics.Arcade.Body) {
      sprite.body.setAllowGravity(allowGravity)
      sprite.body.setImmovable(immovable)
    }
  }

  /**
   * 处理玩家碰撞
   */
  private handlePlayerHit(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody | Phaser.Tilemaps.Tile, object2: Phaser.Types.Physics.Arcade.GameObjectWithBody | Phaser.Tilemaps.Tile): void {
    if (!(object1 instanceof Phaser.Physics.Arcade.Sprite) || !(object2 instanceof Phaser.Physics.Arcade.Sprite)) return
    const player1 = object1 as Player
    const player2 = object2 as Player
    if (player1.team === player2.team) return
    if (player1.inPrison || player2.inPrison) return

    const mapManager = MapManager.getInstance()
    const mapParams = mapManager.getMapParams()
    const centerX = mapParams.centerX
    const p1Sprite = player1 as Phaser.Physics.Arcade.Sprite
    const p2Sprite = player2 as Phaser.Physics.Arcade.Sprite
    const playerCenterX = (p1Sprite.x + p2Sprite.x) / 2

    // 获取团队状态（从 GameStateManager）
    const gameState = GameStateManager.getInstance()
    const teamStates = gameState.getTeamStates()

    if (playerCenterX < centerX) {
      // 在左侧，R队玩家被抓
      const caughtPlayer = player1.team === 'R' ? player1 : player2
      const spot = this.findAvailablePrisonTile(
        this.rteamPlayers?.getChildren() as Player[] || [],
        teamStates.rTeamState.prison
      )
      
      // 如果被抓玩家有旗帜，掉落旗帜
      if (caughtPlayer.hasFlag && this.mapManager && this.lteamFlags) {
        const caughtSprite = caughtPlayer as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(caughtSprite.x, caughtSprite.y)
        if (tile) {
          const flag = this.createFlag(tile.x, tile.y, 'L', true)
          if (flag) {
            this.lteamFlags.add(flag)
          }
          caughtPlayer.hasFlag = false
        }
      }
      caughtPlayer.toPrison(spot.x, spot.y)
    } else {
      // 在右侧，L队玩家被抓
      const caughtPlayer = player1.team === 'L' ? player1 : player2
      const spot = this.findAvailablePrisonTile(
        this.lteamPlayers?.getChildren() as Player[] || [],
        teamStates.lTeamState.prison
      )
      
      // 如果被抓玩家有旗帜，掉落旗帜
      if (caughtPlayer.hasFlag && this.mapManager && this.rteamFlags) {
        const caughtSprite = caughtPlayer as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(caughtSprite.x, caughtSprite.y)
        if (tile) {
          const flag = this.createFlag(tile.x, tile.y, 'R', true)
          if (flag) {
            this.rteamFlags.add(flag)
          }
          caughtPlayer.hasFlag = false
        }
      }
      caughtPlayer.toPrison(spot.x, spot.y)
    }
  }

  /**
   * 处理旗帜收集
   */
  private handleFlagCollected(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody, object2: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
    const player = object1 as Player
    const flag = object2 as Flag
    if (player.team === flag.team) return
    if (player.inPrison) return
    if (player.hasFlag) return
    if (!flag.canPickup) return

    flag.collect()
    player.collectFlag()
  }

  /**
   * 处理旗帜放置
   */
  private handleFlagDropped(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
    const player = object1 as Player
    if (!player.hasFlag) return

    player.dropFlag()

    const gameState = GameStateManager.getInstance()
    const state = gameState.getState()

    if (player.team === 'L') {
      const spot = this.findAvailableFlagTile(
        this.rteamFlags?.getChildren() as Flag[] || [],
        state.lTeamState.target
      )
      const flag = this.createFlag(spot.x, spot.y, 'R', false)
      if (flag && this.rteamFlags) {
        this.rteamFlags.add(flag)
      }
      if (this.callbacks.onScoreUpdate) {
        this.callbacks.onScoreUpdate('L')
      }
    } else {
      const spot = this.findAvailableFlagTile(
        this.lteamFlags?.getChildren() as Flag[] || [],
        state.rTeamState.target
      )
      const flag = this.createFlag(spot.x, spot.y, 'L', false)
      if (flag && this.lteamFlags) {
        this.lteamFlags.add(flag)
      }
      if (this.callbacks.onScoreUpdate) {
        this.callbacks.onScoreUpdate('R')
      }
    }
  }

  /**
   * 处理玩家释放
   */
  private handlePlayerFreed(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
    const player = object1 as Player
    if (player.inPrison) return

    const teamPlayers = player.team === 'L' ? this.lteamPlayers : this.rteamPlayers
    if (teamPlayers) {
      (teamPlayers.getChildren() as Player[]).forEach(p => {
        if (p.inPrison) {
          p.inPrison = false
        }
      })
    }
  }

  /**
   * 查找可用的监狱位置
   */
  private findAvailablePrisonTile(players: Player[], prisons: Position[]): Position {
    if (!this.mapManager) {
      return prisons[0] || { x: 0, y: 0 }
    }

    for (const prison of prisons) {
      let isAvailable = true
      for (const player of players) {
        if (!player.inPrison) continue
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(playerSprite.x, playerSprite.y)
        if (tile && tile.x === prison.x && tile.y === prison.y) {
          isAvailable = false
          break
        }
      }
      if (isAvailable) {
        return prison
      }
    }
    return prisons[0] || { x: 0, y: 0 }
  }

  /**
   * 查找可用的旗帜位置
   */
  private findAvailableFlagTile(flags: Flag[], targets: Position[]): Position {
    if (!this.mapManager) {
      return targets[0] || { x: 0, y: 0 }
    }

    for (const target of targets) {
      let isAvailable = true
      for (const flag of flags) {
        if (flag.canPickup) continue
        const flagSprite = flag as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(flagSprite.x, flagSprite.y)
        if (tile && tile.x === target.x && tile.y === target.y) {
          isAvailable = false
          break
        }
      }
      if (isAvailable) {
        return target
      }
    }
    return targets[0] || { x: 0, y: 0 }
  }

  /**
   * 创建旗帜对象
   */
  private createFlag(x: number, y: number, team: Team, canPickup: boolean): Flag | null {
    if (this.callbacks.onCreateFlag) {
      return this.callbacks.onCreateFlag(this.scene, x, y, team, canPickup)
    }
    // 直接创建 Flag 对象
    return new Flag(this.scene, x, y, team, canPickup)
  }
}

