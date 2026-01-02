import Phaser from 'phaser'
import ASSETS from '../config/assets'
import { GameStateManager } from '../managers/GameStateManager'

export class Preloader extends Phaser.Scene {
  private progressBar!: Phaser.GameObjects.Rectangle

  constructor() {
    super('Preloader')
  }

  init() {
    const centreX = this.scale.width * 0.5
    const centreY = this.scale.height * 0.5

    const barWidth = 468
    const barHeight = 32
    const barMargin = 4

    // 进度条外框
    this.add.rectangle(centreX, centreY, barWidth, barHeight).setStrokeStyle(1, 0xffffff)

    // 进度条本身
    this.progressBar = this.add.rectangle(
      centreX - (barWidth * 0.5) + barMargin,
      centreY,
      barMargin,
      barHeight - barMargin,
      0xffffff
    )

    // 监听加载进度
    this.load.on('progress', (progress: number) => {
      const barWidth = 468
      const barMargin = 4
      this.progressBar.width = barMargin + ((barWidth - (barMargin * 2)) * progress)
    })

    // 监听加载完成
    this.load.on('complete', () => {
      // 通知状态机资源已加载
      GameStateManager.sendFlowEvent({ type: 'ASSETS_LOADED' })
    })

    // 监听加载错误
    this.load.on('loaderror', () => {
      GameStateManager.sendFlowEvent({ type: 'ERROR', error: '资源加载失败' })
    })
  }

  preload() {
    // 加载游戏资源
    for (const type in ASSETS) {
      const assetType = type as keyof typeof ASSETS
      const assets = ASSETS[assetType]
      if (assets) {
        for (const key in assets) {
          const asset = assets[key]
          const loader = (this.load as any)[assetType]
          if (loader) {
            loader.call(this.load, asset.key, ...asset.args)
          }
        }
      }
    }
  }

  create() {
    console.log('[Preloader] 资源加载完成，准备切换到 Game 场景')
    // 资源加载完成后，切换到 Game 场景
    // Game 场景会在 create 阶段加载配置，然后通知状态机
    // 使用 start 停止 Preloader 场景并启动 Game 场景
    this.scene.start('Game')
    console.log('[Preloader] 已切换到 Game 场景')
  }
}

