/**
 * PlayerAnimation - 玩家动画管理器
 * 负责玩家的动画播放和精灵更新
 */
import Phaser from 'phaser'
import type { Team } from '@/types'

/**
 * 玩家动画管理器
 */
export class PlayerAnimation {
  private player: Phaser.Physics.Arcade.Sprite
  private spriteChoice: number
  private hasFlag: boolean
  private team: Team

  constructor(
    player: Phaser.Physics.Arcade.Sprite,
    spriteChoice: number,
    team: Team
  ) {
    this.player = player
    this.spriteChoice = spriteChoice
    this.team = team
    this.hasFlag = false
  }

  /**
   * 设置是否有旗帜
   */
  setHasFlag(hasFlag: boolean): void {
    this.hasFlag = hasFlag
  }

  /**
   * 更新动画（根据移动方向）
   */
  updateAnimation(targetX: number, targetY: number, currentX: number, currentY: number): void {
    const animationKey = `player${this.spriteChoice}${this.hasFlag ? `-characters_${this.team}_flag-` : '-characters-'}`

    // frontend 使用 if...else if 处理 x 方向，然后独立的 if 处理 y 方向
    if (currentX < targetX) {
      this.player.anims.play(`${animationKey}right`, true)
    } else if (currentX > targetX) {
      this.player.anims.play(`${animationKey}left`, true)
    }
    
    if (currentY < targetY) {
      this.player.anims.play(`${animationKey}down`, true)
    } else if (currentY > targetY) {
      this.player.anims.play(`${animationKey}up`, true)
    }
  }

  /**
   * 显示静态图像（监狱状态）
   */
  showStaticImage(): void {
    const animationKey = `player${this.spriteChoice}-characters-down`
    this.player.anims.play(animationKey, true)
  }
}
