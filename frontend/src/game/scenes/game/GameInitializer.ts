/**
 * GameInitializer - 游戏场景初始化器
 * 负责场景初始化、配置加载、管理器初始化
 */
import Phaser from 'phaser'
import type { GameConfig, Team, PlayerActions } from '@/types'
import { InputManager } from '../../managers/InputManager'
import { UIManager } from '../../managers/UIManager'
import { SocketManager } from '../../managers/SocketManager'
import { PhysicsManager } from '../../managers/PhysicsManager'
import { WorldManager } from '../../managers/WorldManager'
import { MapManager } from '../../managers/MapManager'
import { PathVisualizationManager } from '../../managers/PathVisualizationManager'
import { ManagerFactory } from './ManagerFactory'
import { EventSetup } from './EventSetup'

export class GameInitializer {
  private scene: Phaser.Scene
  private world: WorldManager
  private configLoaded: boolean = false
  private managerFactory: ManagerFactory
  private eventSetup!: EventSetup

  public lteamInputManager: InputManager | null = null
  public rteamInputManager: InputManager | null = null
  public uiManager!: UIManager
  public mapManager!: MapManager
  public socketManager!: SocketManager
  public physicsManager!: PhysicsManager
  public pathVisualizationManager!: PathVisualizationManager

  constructor(world: WorldManager, scene: Phaser.Scene) {
    this.world = world
    this.scene = scene
    this.managerFactory = new ManagerFactory(world, scene)
  }

  /**
   * 加载游戏配置
   */
  async loadGameConfig(): Promise<void> {
    await this.world.api.loadConfig('game_config.json')
    this.configLoaded = true
  }

  initManagers(config: GameConfig): void {
    this.socketManager = this.managerFactory.createSocketManager(config)
    this.eventSetup = new EventSetup(this.scene, this.socketManager)
  }

  /**
   * 初始化变量和地图
   */
  initVariables(): void {
    // 重置游戏状态
    this.world.api.resetGameState()
    this.world.api.resetTeamStates()
    this.world.api.resetMapState()

    // 计算地图参数
    const centerX = this.scene.scale.width * 0.5
    const centerY = this.scene.scale.height * 0.5
    const tileSize = 32
    const config = this.world.getState().config
    const mapWidth = config?.setup?.mapWidth || Math.floor((this.scene.scale.width / tileSize) - 5 * 2)
    const mapHeight = config?.setup?.mapHeight || Math.floor((this.scene.scale.height / tileSize) - 5 * 2)
    const mapX = centerX - (mapWidth * tileSize * 0.5)
    const mapY = centerY - (mapHeight * tileSize * 0.5)

    // 设置地图参数并生成地图
    const mapManager = MapManager.getInstance(this.world)
    mapManager.setMapParams({ centerX, centerY, mapWidth, mapHeight, mapX, mapY, tileSize })
    mapManager.generateMap()

    // 生成 TeamStates
    const obstacles = mapManager.getObstacles()
    this.world.api.generateTeamStates(obstacles, mapManager)
    mapManager.logMapDiagnostics()
  }

  initGame(): void {
    this.mapManager = this.managerFactory.createMapManager()
    this.pathVisualizationManager = this.managerFactory.createPathVisualizationManager()
    this.uiManager = this.managerFactory.createUIManager()
    this.physicsManager = this.managerFactory.createPhysicsManager()
    this.managerFactory.initializeMapRenderer()
  }

  /**
   * 初始化物理系统
   */
  initPhysics(
    lteamPlayers: Phaser.GameObjects.Group,
    rteamPlayers: Phaser.GameObjects.Group,
    lteamFlags: Phaser.GameObjects.Group,
    rteamFlags: Phaser.GameObjects.Group,
    lteamTargetZone: Phaser.GameObjects.Zone,
    rteamTargetZone: Phaser.GameObjects.Zone,
    lteamPrisonZone: Phaser.GameObjects.Zone,
    rteamPrisonZone: Phaser.GameObjects.Zone
  ): void {
    this.physicsManager.setGameObjects(
      this.mapManager,
      lteamPlayers,
      rteamPlayers,
      lteamFlags,
      rteamFlags
    )

    this.physicsManager.setupCollisions(
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

  setupSocketListeners(onPlayerInfoUpdate: (team: Team, actions: PlayerActions) => void): void {
    this.eventSetup.setupSocketListeners(onPlayerInfoUpdate)
  }

  setInputManagers(lteamInputManager: InputManager, rteamInputManager: InputManager): void {
    this.lteamInputManager = lteamInputManager
    this.rteamInputManager = rteamInputManager
    this.eventSetup.setupInputManagers(lteamInputManager)
  }

  isConfigLoaded(): boolean {
    return this.configLoaded
  }

  setConfigLoaded(loaded: boolean): void {
    this.configLoaded = loaded
  }
}
