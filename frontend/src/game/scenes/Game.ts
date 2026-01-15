/**
 * Game Scene - 主游戏场景
 * 使用组合模式，将功能委托给专门的模块
 */
import Phaser from 'phaser'
import type { Team } from '@/types'
import { Flag } from '../objects/Flag'
import { WorldManager } from '../managers/WorldManager'
import { GameInitializer } from './game/GameInitializer'
import { GameLoop } from './game/GameLoop'
import { GameObjectManager } from './game/GameObjectManager'
import { GameFlowController } from './game/GameFlowController'
import { ScoreManager } from './game/ScoreManager'

export class Game extends Phaser.Scene {
  private initializer!: GameInitializer
  private gameLoop!: GameLoop
  private objectManager!: GameObjectManager
  private flowController!: GameFlowController
  private scoreManager!: ScoreManager
  
  private lteamPlayers!: Phaser.GameObjects.Group
  private rteamPlayers!: Phaser.GameObjects.Group
  private lteamFlags!: Phaser.GameObjects.Group
  private rteamFlags!: Phaser.GameObjects.Group
  private lteamTargetZone!: Phaser.GameObjects.Zone
  private rteamTargetZone!: Phaser.GameObjects.Zone
  private lteamPrisonZone!: Phaser.GameObjects.Zone
  private rteamPrisonZone!: Phaser.GameObjects.Zone

  private get gameStarted(): boolean {
    return WorldManager.getInstance().getState().gameStarted
  }

  constructor() {
    super('Game')
  }

  create(): void {
    console.log('[Game] create() 被调用')
    this.cameras.main.setBackgroundColor('#2d3436')
    const world = WorldManager.getInstance()
    this.initializer = new GameInitializer(world, this)
    this.objectManager = new GameObjectManager(world, this, this.initializer)
    this.flowController = new GameFlowController(world, this, this.initializer, () => this.setGameObjects())
    this.events.on('start', () => {
      console.log('[Game] 场景启动事件触发')
      this.handleSceneStart()
    })
    if (!this.initializer.isConfigLoaded() && !this.gameStarted) {
      console.log('[Game] 开始加载配置...')
      this.initializer.setConfigLoaded(true)
      this.loadGameConfig().catch((error) => {
        console.error('[Game] 配置加载失败:', error)
        WorldManager.sendFlowEvent({ type: 'ERROR', error: `配置加载失败: ${error}` })
        this.add.text(this.scale.width * 0.5, this.scale.height * 0.5, '配置加载失败，请检查控制台', { fontSize: '24px', color: '#ff0000', align: 'center' }).setOrigin(0.5)
      })
    } else {
      console.log('[Game] 配置已加载或游戏已开始，跳过配置加载')
    }
  }

  private handleSceneStart(): void {
    console.log('[Game] handleSceneStart() 被调用')
    let world: WorldManager | null = null
    try {
      world = WorldManager.getInstance()
    } catch (error) {
      console.log('[Game] handleSceneStart: WorldManager 未初始化，这是首次启动场景，跳过重启检查')
      return
    }
    try {
      const state = world.getState()
      if (!state || typeof state !== 'object') {
        console.warn('[Game] handleSceneStart: 获取的状态无效', state)
        return
      }
      if (this.flowController.getWasGameOver() && state.flowState === 'playing' && state.currentScene === 'Game' && !state.gameOver) {
        console.log('[Game] 检测到重启场景，重置游戏')
        this.restartGame()
        this.flowController.setWasGameOver(false)
        return
      }
    } catch (error) {
      console.log('[Game] handleSceneStart: 获取状态失败（可能是首次启动）', error)
    }
  }

  preload(): void {
    // Game 场景不需要在 preload 中加载资源
    // 资源已在 Preloader 场景中加载完成
    // 配置加载在 create 阶段异步进行
  }

  update(time: number, delta: number): void {
    // 调用游戏循环更新（处理输入、移动和状态同步）
    if (this.gameLoop) {
      const updated = this.gameLoop.update(time, delta)
      // 仅在第一次显示提示
      if (!updated && !this.gameStarted && time > 1000) {
        // 游戏未开始的提示会在 GameLoop 中输出
      }
    }
  }

  private async loadGameConfig(): Promise<void> {
    await this.initializer.loadGameConfig()
    const world = WorldManager.getInstance()
    const config = world.getState().config
    if (!config) {
      throw new Error('配置加载失败')
    }
    this.initializer.initManagers(config)
    this.initializer.initVariables()
    this.initializer.initGame()
    this.setGameObjects()
    this.scoreManager = new ScoreManager(world, this.lteamFlags, this.rteamFlags, this.initializer.uiManager, (team) => this.flowController.gameOver(team))
    this.initializer.initPhysics(this.lteamPlayers, this.rteamPlayers, this.lteamFlags, this.rteamFlags, this.lteamTargetZone, this.rteamTargetZone, this.lteamPrisonZone, this.rteamPrisonZone)
    this.gameLoop = new GameLoop(world, this.initializer.socketManager, this.initializer.pathVisualizationManager, this.initializer.lteamInputManager, this.initializer.rteamInputManager, this.lteamPlayers, this.rteamPlayers, this.lteamFlags, this.rteamFlags)
    this.initializer.setupSocketListeners((team, actions) => {
      this.gameLoop.updatePlayerInfo(team, actions)
    })
    WorldManager.sendFlowEvent({ type: 'CONFIG_LOADED' })
    console.log('[Game] 已发送 CONFIG_LOADED 事件')
    console.log('[Game] ⚠️  游戏准备完成，按 SPACE 空格键开始游戏！ ⚠️')
    console.log('[Game] 控制说明：')
    console.log('[Game]   L队: WASD 键控制')
    console.log('[Game]   R队: 方向键 ←↑↓→ 控制')
    this.initializer.uiManager.showComponent('tutorial')
  }
  
  setGameObjects(): void {
    const objects = this.objectManager.setupGameObjects()
    this.lteamFlags = objects.lteamFlags
    this.rteamFlags = objects.rteamFlags
    this.lteamPlayers = objects.lteamPlayers
    this.rteamPlayers = objects.rteamPlayers
    this.lteamTargetZone = objects.lteamTargetZone
    this.rteamTargetZone = objects.rteamTargetZone
    this.lteamPrisonZone = objects.lteamPrisonZone
    this.rteamPrisonZone = objects.rteamPrisonZone
  }
  startOrPauseOrContinue(): void {
    this.flowController.startOrPauseOrContinue()
  }
  removeFlagItem(flag: Flag): void {
    this.scoreManager.removeFlagItem(flag)
  }
  updateTeamScore(team: Team): void {
    this.scoreManager.updateTeamScore(team)
  }
  private restartGame(): void {
    this.flowController.restartGame(this.lteamPlayers, this.rteamPlayers, this.lteamFlags, this.rteamFlags, this.lteamTargetZone, this.rteamTargetZone, this.lteamPrisonZone, this.rteamPrisonZone, this.gameLoop)
  }

  // 暴露给 Player 和 Flag 使用的方法
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number } {
    return this.initializer.mapManager.getMapOffset()
  }

  isWall(x: number, y: number): boolean {
    return this.initializer.mapManager.isWall(x, y)
  }
}

