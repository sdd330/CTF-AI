/**
 * CollisionHandler - 碰撞处理器
 * 负责处理各种碰撞事件
 */
import Phaser from 'phaser'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { WorldManager } from '../WorldManager'
import { MapManager } from '../MapManager'
import { CollisionCallbackManager } from './CollisionCallbackManager'
import { PositionFinder } from './PositionFinder'

/**
 * 碰撞处理器
 */
export class CollisionHandler {
  private lteamPlayers: Phaser.GameObjects.Group | null = null
  private rteamPlayers: Phaser.GameObjects.Group | null = null
  private lteamFlags: Phaser.GameObjects.Group | null = null
  private rteamFlags: Phaser.GameObjects.Group | null = null
  private callbackManager: CollisionCallbackManager
  private positionFinder: PositionFinder

  constructor(
    private world: WorldManager,
    callbackManager: CollisionCallbackManager
  ) {
    this.callbackManager = callbackManager
    this.positionFinder = new PositionFinder()
  }

  /**
   * 设置游戏对象组
   */
  setGameObjects(
    mapManager: MapManager,
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group
  ): void {
    this.positionFinder.setMapManager(mapManager)
    this.lteamPlayers = lteamPlayers
    this.rteamPlayers = rteamPlayers
    this.lteamFlags = lteamFlags
    this.rteamFlags = rteamFlags
  }

  /**
   * 处理玩家碰撞
   */
  handlePlayerHit(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody | Phaser.Tilemaps.Tile, object2: Phaser.Types.Physics.Arcade.GameObjectWithBody | Phaser.Tilemaps.Tile): void {
    if (!(object1 instanceof Phaser.Physics.Arcade.Sprite) || !(object2 instanceof Phaser.Physics.Arcade.Sprite)) return
    const player1 = object1 as Player
    const player2 = object2 as Player
    if (player1.team === player2.team) return
    if (player1.inPrison || player2.inPrison) return

    const mapManager = MapManager.getInstance(this.world)
    const mapParams = mapManager.getMapParams()
    const centerX = mapParams.centerX
    const p1Sprite = player1 as Phaser.Physics.Arcade.Sprite
    const p2Sprite = player2 as Phaser.Physics.Arcade.Sprite
    const playerCenterX = (p1Sprite.x + p2Sprite.x) / 2

    // 获取团队状态（从 WorldManager）
    const teamStates = this.world.api.getTeamStates()

    if (playerCenterX < centerX) {
      // 在左侧，R队玩家被抓
      const caughtPlayer = player1.team === 'R' ? player1 : player2
      const spot = this.positionFinder.findAvailablePrisonTile(
        this.rteamPlayers?.getChildren() as Player[] || [],
        teamStates.rTeamState.prison
      )
      
      // 如果被抓玩家有旗帜，掉落旗帜并添加回旗帜组
      if (caughtPlayer.hasFlag) {
        caughtPlayer.hasFlag = false
        // 旗帜掉落到 L 队目标区域
        const flagSpot = this.positionFinder.findAvailableFlagTile(
          this.lteamFlags?.getChildren() as Flag[] || [],
          teamStates.lTeamState.target
        )
        const flag = this.callbackManager.createFlag(flagSpot.x, flagSpot.y, 'L', false)
        if (flag && this.lteamFlags) {
          this.lteamFlags.add(flag)
        }
      }
      caughtPlayer.toPrison(spot.x, spot.y)
    } else {
      // 在右侧，L队玩家被抓
      const caughtPlayer = player1.team === 'L' ? player1 : player2
      const spot = this.positionFinder.findAvailablePrisonTile(
        this.lteamPlayers?.getChildren() as Player[] || [],
        teamStates.lTeamState.prison
      )
      
      // 如果被抓玩家有旗帜，掉落旗帜并添加回旗帜组
      if (caughtPlayer.hasFlag) {
        caughtPlayer.hasFlag = false
        // 旗帜掉落到 R 队目标区域
        const flagSpot = this.positionFinder.findAvailableFlagTile(
          this.rteamFlags?.getChildren() as Flag[] || [],
          teamStates.rTeamState.target
        )
        const flag = this.callbackManager.createFlag(flagSpot.x, flagSpot.y, 'R', false)
        if (flag && this.rteamFlags) {
          this.rteamFlags.add(flag)
        }
      }
      caughtPlayer.toPrison(spot.x, spot.y)
    }
  }

  /**
   * 处理旗帜收集
   */
  handleFlagCollected(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody, object2: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
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
  handleFlagDropped(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
    const player = object1 as Player
    if (!player.hasFlag) return

    player.dropFlag()

    const state = this.world.getState()

    if (player.team === 'L') {
      const spot = this.positionFinder.findAvailableFlagTile(
        this.rteamFlags?.getChildren() as Flag[] || [],
        state.lTeamState.target
      )
      const flag = this.callbackManager.createFlag(spot.x, spot.y, 'R', false)
      if (flag && this.rteamFlags) {
        this.rteamFlags.add(flag)
      }
      this.callbackManager.onScoreUpdate('L')
    } else {
      const spot = this.positionFinder.findAvailableFlagTile(
        this.lteamFlags?.getChildren() as Flag[] || [],
        state.rTeamState.target
      )
      const flag = this.callbackManager.createFlag(spot.x, spot.y, 'L', false)
      if (flag && this.lteamFlags) {
        this.lteamFlags.add(flag)
      }
      this.callbackManager.onScoreUpdate('R')
    }
  }

  /**
   * 处理玩家释放
   */
  handlePlayerFreed(object1: Phaser.Types.Physics.Arcade.GameObjectWithBody): void {
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
   * 获取位置查找器（用于测试）
   */
  getPositionFinder(): PositionFinder {
    return this.positionFinder
  }

}
