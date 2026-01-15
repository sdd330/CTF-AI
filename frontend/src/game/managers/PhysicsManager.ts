import Phaser from 'phaser'
import type { Team } from '@/types'
import { WorldManager } from './WorldManager'
import { MapManager } from './MapManager'
import { CollisionDetector } from './physics/CollisionDetector'
import { CollisionHandler } from './physics/CollisionHandler'
import { CollisionCallbackManager, CollisionCallbacks } from './physics/CollisionCallbackManager'
import { PhysicsBodyManager } from './physics/PhysicsBodyManager'

export type { CollisionCallbacks } from './physics/CollisionCallbackManager'

export class PhysicsManager {
  private collisionDetector: CollisionDetector
  private collisionHandler: CollisionHandler
  private callbackManager: CollisionCallbackManager
  private bodyManager: PhysicsBodyManager

  constructor(world: WorldManager, scene: Phaser.Scene, callbacks: CollisionCallbacks = {}) {
    this.callbackManager = new CollisionCallbackManager(world, scene, callbacks)
    this.collisionHandler = new CollisionHandler(world, this.callbackManager)
    this.collisionDetector = new CollisionDetector(scene, this.collisionHandler)
    this.bodyManager = new PhysicsBodyManager(scene)
  }

  setGameObjects(
    mapManager: MapManager,
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group
  ): void {
    this.collisionHandler.setGameObjects(mapManager, lteamPlayers, rteamPlayers, lteamFlags, rteamFlags)
  }

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
    this.collisionDetector.setupCollisions(
      lteamPlayers,
      rteamPlayers,
      lteamFlags,
      rteamFlags,
      lteamTargetZone,
      rteamTargetZone,
      lteamPrisonZone,
      rteamPrisonZone
    )
  }

  addPhysicsBody(
    gameObject: Phaser.GameObjects.GameObject,
    allowGravity: boolean = false,
    immovable: boolean = true
  ): void {
    this.bodyManager.addPhysicsBody(gameObject, allowGravity, immovable)
  }

  /**
   * 获取碰撞处理器（用于测试）
   */
  getCollisionHandler(): CollisionHandler {
    return this.collisionHandler
  }
}

