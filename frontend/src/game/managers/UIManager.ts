/**
 * UIManager - UI 管理器
 * 设计模式：工厂模式 + 组件化
 */
import Phaser from 'phaser'

// UI 组件接口
export interface UIComponent {
  show(): void
  hide(): void
  update(data?: unknown): void
  destroy(): void
}

// UI 组件类型
export enum UIComponentType {
  SCORE_TEXT = 'score_text',
  TUTORIAL_TEXT = 'tutorial_text',
  GAME_OVER_TEXT = 'game_over_text',
  TEAM_NAME_TEXT = 'team_name_text'
}

// 分数文本组件
export class ScoreTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text
  private team: 'L' | 'R'

  constructor(scene: Phaser.Scene, team: 'L' | 'R', x: number, y: number) {
    this.team = team
    this.text = scene.add.text(x, y, `${team}Team #Flags: 0`, {
      fontFamily: 'Arial Black',
      fontSize: 36,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: team === 'L' ? 'left' : 'right'
    }).setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(score: number): void {
    this.text.setText(`${this.team}Team #Flags: ${score}`)
  }

  destroy(): void {
    this.text.destroy()
  }
}

// 教程文本组件
export class TutorialTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, 'Arrow keys to move!\nPress Spacebar to Start', {
      fontFamily: 'Arial Black',
      fontSize: 48,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: 'center'
    })
      .setOrigin(0.5)
      .setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(): void {
    // 教程文本不需要更新
  }

  destroy(): void {
    this.text.destroy()
  }
}

// 游戏结束文本组件
export class GameOverTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, 'Game Over', {
      fontFamily: 'Arial Black',
      fontSize: 64,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: 'center'
    })
      .setOrigin(0.5)
      .setDepth(100)
      .setVisible(false)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(winner?: string): void {
    if (winner) {
      this.text.setText(`${winner}Team Won!`)
    }
  }

  destroy(): void {
    this.text.destroy()
  }
}

// 队伍名称文本组件
export class TeamNameTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, team: 'L' | 'R', x: number, y: number) {
    this.text = scene.add.text(x, y, '-', {
      fontFamily: 'Arial Black',
      fontSize: 36,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: team === 'L' ? 'left' : 'right'
    }).setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(who: string): void {
    this.text.setText(who)
  }

  destroy(): void {
    this.text.destroy()
  }
}

// UI 组件工厂
export class UIComponentFactory {
  static create(
    type: UIComponentType,
    scene: Phaser.Scene,
    ...args: unknown[]
  ): UIComponent {
    switch (type) {
      case UIComponentType.SCORE_TEXT:
        return new ScoreTextComponent(scene, args[0] as 'L' | 'R', args[1] as number, args[2] as number)
      case UIComponentType.TUTORIAL_TEXT:
        return new TutorialTextComponent(scene, args[0] as number, args[1] as number)
      case UIComponentType.GAME_OVER_TEXT:
        return new GameOverTextComponent(scene, args[0] as number, args[1] as number)
      case UIComponentType.TEAM_NAME_TEXT:
        return new TeamNameTextComponent(scene, args[0] as 'L' | 'R', args[1] as number, args[2] as number)
      default:
        throw new Error(`Unknown UI component type: ${type}`)
    }
  }
}

// UI 管理器主类
export class UIManager {
  private components: Map<string, UIComponent> = new Map()
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
      console.log('[UIManager] 动画已初始化，跳过')
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
        console.error(`[UIManager] 精灵表不存在: ${spriteKey}`)
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
            console.error(`[UIManager] 创建动画失败 ${key}:`, error)
          }
        }
      }
    }

    this.animationsInitialized = true
    console.log(`[UIManager] 动画初始化完成，共创建 ${animationCount} 个动画`)
    
    if (missingTextures.length > 0) {
      console.warn(`[UIManager] 缺失的精灵表:`, missingTextures)
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
        console.log(`[UIManager] ✓ 动画存在: ${key}`)
      } else {
        console.warn(`[UIManager] ✗ 动画不存在: ${key}`)
      }
    })
  }

  /**
   * 检查动画是否已初始化
   */
  isAnimationsInitialized(): boolean {
    return this.animationsInitialized
  }

  // 创建并注册 UI 组件
  createComponent(id: string, type: UIComponentType, ...args: unknown[]): UIComponent {
    const component = UIComponentFactory.create(type, this.scene, ...args)
    this.components.set(id, component)
    return component
  }

  // 获取组件
  getComponent(id: string): UIComponent | undefined {
    return this.components.get(id)
  }

  // 更新组件
  updateComponent(id: string, data?: unknown): void {
    const component = this.components.get(id)
    if (component) {
      component.update(data)
    }
  }

  // 显示组件
  showComponent(id: string): void {
    const component = this.components.get(id)
    if (component) {
      component.show()
    }
  }

  // 隐藏组件
  hideComponent(id: string): void {
    const component = this.components.get(id)
    if (component) {
      component.hide()
    }
  }

  // 销毁所有组件
  destroyAll(): void {
    this.components.forEach(component => component.destroy())
    this.components.clear()
  }

  // 销毁指定组件
  destroyComponent(id: string): void {
    const component = this.components.get(id)
    if (component) {
      component.destroy()
      this.components.delete(id)
    }
  }
}

