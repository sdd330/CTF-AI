/**
 * CollisionDetector - 碰撞检测器
 * 负责设置和管理碰撞检测
 */
import Phaser from 'phaser'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { CollisionHandler } from './CollisionHandler'

/**
 * 碰撞检测器
 */
export class CollisionDetector {
  private scene: Phaser.Scene
  private collisionHandler: CollisionHandler

  constructor(scene: Phaser.Scene, collisionHandler: CollisionHandler) {
    this.scene = scene
    this.collisionHandler = collisionHandler
  }

  /**
   * 设置碰撞检测
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
      this.collisionHandler.handlePlayerHit.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )

    // 玩家收集旗帜
    this.scene.physics.add.overlap(
      lteamPlayers,
      rteamFlags,
      this.collisionHandler.handleFlagCollected.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      lteamFlags,
      this.collisionHandler.handleFlagCollected.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )

    // 玩家放置旗帜
    this.scene.physics.add.overlap(
      lteamPlayers,
      lteamTargetZone,
      this.collisionHandler.handleFlagDropped.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      rteamTargetZone,
      this.collisionHandler.handleFlagDropped.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )

    // 玩家释放队友
    this.scene.physics.add.overlap(
      lteamPlayers,
      lteamPrisonZone,
      this.collisionHandler.handlePlayerFreed.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )
    this.scene.physics.add.overlap(
      rteamPlayers,
      rteamPrisonZone,
      this.collisionHandler.handlePlayerFreed.bind(this.collisionHandler) as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this.collisionHandler
    )
  }
}
