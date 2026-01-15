/**
 * PhysicsBodyManager - 物理体管理器
 * 负责管理物理体的创建和配置
 */
import Phaser from 'phaser'

/**
 * 物理体管理器
 */
export class PhysicsBodyManager {
  private scene: Phaser.Scene

  constructor(scene: Phaser.Scene) {
    this.scene = scene
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
}
