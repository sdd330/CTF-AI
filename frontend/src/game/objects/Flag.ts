import Phaser from 'phaser'
import type { Team, FlagStatus } from '@/types'
import type { WorldManager } from '../managers/WorldManager'
import ASSETS from '../config/assets'

// 场景接口（用于类型安全地访问场景方法）
export interface ISceneWithMapMethods {
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number }
  removeFlagItem(flag: Flag): void
}

export class Flag extends Phaser.Physics.Arcade.Sprite {
  private world: WorldManager
  public team: Team
  public posX: number
  public posY: number
  public canPickup: boolean

  private mapOffset: { x: number; y: number; tileSize: number } | null = null

  constructor(
    world: WorldManager,
    scene: Phaser.Scene,
    x: number,
    y: number,
    team: Team,
    canPickup: boolean
  ) {
    const spriteKey = team === 'L' 
      ? ASSETS.spritesheet!.L_flag.key 
      : ASSETS.spritesheet!.R_flag.key

    super(scene, 0, 0, spriteKey)

    this.world = world
    scene.add.existing(this)
    scene.physics.add.existing(this)

    this.team = team
    this.posX = x
    this.posY = y
    this.canPickup = canPickup

    // 获取地图偏移量
    const sceneWithMap = scene as Phaser.Scene & ISceneWithMapMethods
    if (sceneWithMap.getMapOffset) {
      this.mapOffset = sceneWithMap.getMapOffset()
      this.setPosition(
        this.mapOffset.x + (x * this.mapOffset.tileSize),
        this.mapOffset.y + (y * this.mapOffset.tileSize)
      )
    }

    this.setDepth(90)
  }

  collect(): boolean {
    if (!this.canPickup) {
      return false
    }
    const sceneWithMap = this.scene as Phaser.Scene & ISceneWithMapMethods
    if (sceneWithMap.removeFlagItem) {
      sceneWithMap.removeFlagItem(this)
    }
    return true
  }

  getStatus(): FlagStatus {
    return {
      canPickup: this.canPickup,
      posX: this.posX,
      posY: this.posY
    }
  }
}

