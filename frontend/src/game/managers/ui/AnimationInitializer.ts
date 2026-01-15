/**
 * AnimationInitializer - 动画初始化器
 * 负责初始化玩家动画
 */
import Phaser from 'phaser'

/**
 * 动画初始化器
 */
export class AnimationInitializer {
  private scene: Phaser.Scene
  private animationsInitialized = false

  constructor(scene: Phaser.Scene) {
    this.scene = scene
  }

  /**
   * 初始化玩家动画
   * 参考 frontend/src/scenes/Game.js 的 initAnimations 方法
   */
  initAnimations(): void {
    if (this.animationsInitialized) {
      console.log('[AnimationInitializer] 动画已初始化，跳过')
      return
    }

    const flagChoices = ['characters', 'characters_L_flag', 'characters_R_flag']
    const dirChoices = ['left', 'down', 'up', 'right']

    let animationCount = 0
    const missingTextures: string[] = []

    for (let k = 0; k < 3; k++) {
      const spriteKey = flagChoices[k]

      // 检查精灵表是否存在
      if (!this.scene.textures.exists(spriteKey)) {
        missingTextures.push(spriteKey)
        console.error(`[AnimationInitializer] 精灵表不存在: ${spriteKey}`)
        continue
      }

      for (let i = 1; i <= 6; i++) {
        for (let j = 0; j < 4; j++) {
          const key = `player${i}-${flagChoices[k]}-${dirChoices[j]}`
          const config = {
            frames: [(i - 1) * 12 + j, (i - 1) * 12 + j + 4, (i - 1) * 12 + j + 8]
          }

          try {
            this.scene.anims.create({
              key,
              frames: this.scene.anims.generateFrameNumbers(spriteKey, config),
              frameRate: 10,
              repeat: 0 // 与 frontend 保持一致：repeat: 0，每次 move() 都会重新调用 play()
            })
            animationCount++
          } catch (error) {
            console.error(`[AnimationInitializer] 创建动画失败 ${key}:`, error)
          }
        }
      }
    }

    this.animationsInitialized = true
    console.log(`[AnimationInitializer] 动画初始化完成，共创建 ${animationCount} 个动画`)
    
    if (missingTextures.length > 0) {
      console.warn(`[AnimationInitializer] 缺失的精灵表:`, missingTextures)
    }

    // 验证一些关键动画是否存在
    const testKeys = [
      'player1-characters-right',
      'player1-characters-left',
      'player1-characters-down',
      'player1-characters-up'
    ]
    testKeys.forEach(key => {
      if (this.scene.anims.exists(key)) {
        console.log(`[AnimationInitializer] ✓ 动画存在: ${key}`)
      } else {
        console.warn(`[AnimationInitializer] ✗ 动画不存在: ${key}`)
      }
    })
  }

  /**
   * 检查动画是否已初始化
   */
  isAnimationsInitialized(): boolean {
    return this.animationsInitialized
  }
}
