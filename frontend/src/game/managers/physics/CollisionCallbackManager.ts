/**
 * CollisionCallbackManager - 碰撞回调管理器
 * 负责管理碰撞相关的回调函数
 */
import Phaser from 'phaser'
import type { Team } from '@/types'
import type { WorldManager } from '../WorldManager'
import { Flag } from '../../objects/Flag'

/**
 * 碰撞回调接口
 */
export interface CollisionCallbacks {
  onScoreUpdate?: (team: Team) => void
  onCreateFlag?: (world: WorldManager, scene: Phaser.Scene, x: number, y: number, team: Team, canPickup: boolean) => Flag
}

/**
 * 碰撞回调管理器
 */
export class CollisionCallbackManager {
  private callbacks: CollisionCallbacks
  private scene: Phaser.Scene
  private world: WorldManager

  constructor(world: WorldManager, scene: Phaser.Scene, callbacks: CollisionCallbacks = {}) {
    this.world = world
    this.scene = scene
    this.callbacks = callbacks
  }

  /**
   * 触发分数更新回调
   */
  onScoreUpdate(team: Team): void {
    if (this.callbacks.onScoreUpdate) {
      this.callbacks.onScoreUpdate(team)
    }
  }

  /**
   * 创建旗帜对象
   */
  createFlag(x: number, y: number, team: Team, canPickup: boolean): Flag | null {
    if (this.callbacks.onCreateFlag) {
      return this.callbacks.onCreateFlag(this.world, this.scene, x, y, team, canPickup)
    }
    // 直接创建 Flag 对象
    return new Flag(this.world, this.scene, x, y, team, canPickup)
  }
}
