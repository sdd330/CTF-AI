import { defineComponent, onMounted, onUnmounted, ref } from 'vue'
import Phaser from 'phaser'
import { Boot } from '@/game/scenes/Boot'
import { Preloader } from '@/game/scenes/Preloader'
import { Game } from '@/game/scenes/Game'
import { GameOver } from '@/game/scenes/GameOver'
import { WorldManager } from '@/game/managers/WorldManager'

export default defineComponent({
  name: 'GameContainer',
  setup() {
    const game = ref<Phaser.Game | null>(null)

    onMounted(() => {
      // 创建 Phaser 游戏实例
      const config: Phaser.Types.Core.GameConfig = {
        type: Phaser.AUTO,
        width: (20 + 10) * 32,
        height: (20 + 10) * 32,
        parent: 'game-container',
        backgroundColor: '#2d3436',
        scale: {
          mode: Phaser.Scale.FIT,
          autoCenter: Phaser.Scale.CENTER_BOTH
        },
        physics: {
          default: 'arcade',
          arcade: {
            debug: false,
            gravity: { x: 0, y: 0 }
          }
        },
        scene: [Boot, Preloader, Game, GameOver]
      }

      const phaserGame = new Phaser.Game(config)
      game.value = phaserGame as unknown as Phaser.Game

      // 等待游戏实例创建后再初始化状态管理器
      // 使用 setTimeout 确保 Phaser 游戏完全初始化
      setTimeout(() => {
        if (game.value) {
          // 初始化状态管理器（统一管理游戏状态和流程）
          const world = WorldManager.initialize(phaserGame)

          // 暴露到全局，供其他模块使用
          if (typeof window !== 'undefined') {
            ;(window as any).world = world
          }

          // Phaser 会自动启动场景数组中的第一个场景（Boot）
          // 所以这里不需要手动启动 Boot 场景
          // 只监听状态变化，在需要时切换场景
          let lastScene = 'Boot' // 记录上次的场景，避免重复切换
          
          world.onStateChange((state) => {
            if (game.value) {
              const sceneManager = game.value.scene
              const targetScene = state.currentScene

              // 如果场景没有变化，跳过
              if (targetScene === lastScene) {
                return
              }

              console.log('[GameContainer] 场景切换:', targetScene, '当前活动场景:', sceneManager.getScenes(true).map(s => s.scene.key))

              // 根据目标场景切换（不处理 Boot，因为它是自动启动的）
              if (targetScene === 'Preloader' && sceneManager.getScene('Preloader')) {
                if (!sceneManager.isActive('Preloader')) {
                  sceneManager.start('Preloader')
                  lastScene = 'Preloader'
                }
              } else if (targetScene === 'Game' && sceneManager.getScene('Game')) {
                const gameScene = sceneManager.getScene('Game')
                if (gameScene) {
                  // 停止 Preloader 场景（隐藏进度条）
                  if (sceneManager.isActive('Preloader')) {
                    sceneManager.stop('Preloader')
                    console.log('[GameContainer] 已停止 Preloader 场景')
                  }
                  
                  // 如果从 GameOver 场景返回，需要重新启动 Game 场景以触发重置
                  if (lastScene === 'GameOver') {
                    // 停止 GameOver 场景
                    if (sceneManager.isActive('GameOver')) {
                      sceneManager.stop('GameOver')
                      console.log('[GameContainer] 已停止 GameOver 场景')
                    }
                    // 重新启动 Game 场景以触发重置（stop + start 会触发 start 事件）
                    if (sceneManager.isActive('Game')) {
                      sceneManager.stop('Game')
                    }
                    sceneManager.start('Game')
                    console.log('[GameContainer] 从 GameOver 返回，重新启动 Game 场景以重置游戏')
                  } else if (!sceneManager.isActive('Game')) {
                    // 首次启动 Game 场景
                    sceneManager.start('Game')
                    console.log('[GameContainer] 已启动 Game 场景')
                  } else {
                    // 如果已经在运行，确保它是可见的
                    sceneManager.bringToTop('Game')
                    console.log('[GameContainer] Game 场景已置顶')
                  }
                  lastScene = 'Game'
                }
              } else if (targetScene === 'GameOver' && sceneManager.getScene('GameOver')) {
                if (!sceneManager.isActive('GameOver')) {
                  sceneManager.start('GameOver')
                  lastScene = 'GameOver'
                }
              }
            }
          })
        }
      }, 0)
    })

    onUnmounted(() => {
      if (game.value) {
        game.value.destroy(true)
        game.value = null
      }
      // 清理全局引用
      if (typeof window !== 'undefined') {
        ;(window as any).world = null
      }
    })

    return () => <div id="game-container" class="game-container" />
  }
})
