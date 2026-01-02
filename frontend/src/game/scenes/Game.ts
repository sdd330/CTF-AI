/**
 * Game Scene - 主游戏场景
 * 整合所有管理器模块
 * 
 * 职责划分：
 * - GameStateManager：管理游戏状态（gameStarted, gamePaused, score等）- 单一数据源
 * - Game Scene：场景初始化、地图生成、游戏对象创建、游戏循环
 * 
 * 状态管理原则：
 * - 所有游戏状态通过 GameStateManager 统一管理（单一数据源）
 * - Game Scene 只负责场景相关的初始化（地图参数、障碍物生成等）
 */
import Phaser from 'phaser'
import type { Team, GameConfig, PlayerActions, Position } from '@/types'
import { InputManager, KeyboardInputStrategy, RemoteInputStrategy, HybridInputStrategy } from '../managers/InputManager'
import { UIManager, UIComponentType } from '../managers/UIManager'
// MapRenderer 已合并到 MapManager
import { SocketManager, SocketEvent } from '../managers/SocketManager'
import { PhysicsManager, type CollisionCallbacks } from '../managers/PhysicsManager'
import { Player } from '../objects/Player'
import { Flag } from '../objects/Flag'
import { GameStateManager } from '../managers/GameStateManager'
import { MapManager } from '../managers/MapManager'
import { PathVisualizationManager } from '../managers/PathVisualizationManager'
import ASSETS from '../config/assets'

export class Game extends Phaser.Scene {
  // 游戏状态（使用 GameStateManager 统一管理，这里只保留场景特定的状态）
  private stageSent = false
  private lastSendTime = 0
  private configLoaded = false
  private wasGameOver = false // 标记之前是否在 GameOver 场景
  
  // 获取 GameStateManager 实例的便捷方法
  private get gameState(): GameStateManager {
    return GameStateManager.getInstance()
  }
  
  // 获取游戏状态的便捷方法
  private get gameStarted(): boolean {
    return this.gameState.getState().gameStarted
  }
  
  private get gamePaused(): boolean {
    return this.gameState.getState().gamePaused
  }

  // 配置（从 GameStateManager 读取，单一数据源）
  private get NUM_FLAGS(): number {
    return this.gameState.getState().numFlags
  }
  
  // 管理器
  private inputManager!: InputManager
  private uiManager!: UIManager
  private mapManager!: MapManager
  private socketManager!: SocketManager
  private physicsManager!: PhysicsManager
  private pathVisualizationManager!: PathVisualizationManager

  // 游戏对象组
  private lteamPlayers!: Phaser.GameObjects.Group
  private rteamPlayers!: Phaser.GameObjects.Group
  private lteamFlags!: Phaser.GameObjects.Group
  private rteamFlags!: Phaser.GameObjects.Group
  private lteamTargetZone!: Phaser.GameObjects.Zone
  private rteamTargetZone!: Phaser.GameObjects.Zone
  private lteamPrisonZone!: Phaser.GameObjects.Zone
  private rteamPrisonZone!: Phaser.GameObjects.Zone

  // 地图和团队状态通过 MapManager 统一访问（移除直接访问 GameStateManager 的 getter）


  constructor() {
    super('Game')
  }

  create(): void {
    console.log('[Game] create() 被调用，configLoaded:', this.configLoaded, 'gameStarted:', this.gameStarted)
    
    // 先设置背景色，确保场景可见
    this.cameras.main.setBackgroundColor('#2d3436')
    
    // 监听场景启动事件（当从其他场景返回到此场景时会触发）
    this.events.on('start', () => {
      console.log('[Game] 场景启动事件触发')
      this.handleSceneStart()
    })
    
    // 如果配置还未加载，则加载配置
    // 配置加载完成后会通知状态机
    if (!this.configLoaded && !this.gameStarted) {
      console.log('[Game] 开始加载配置...')
      this.configLoaded = true
      this.loadGameConfig().catch((error) => {
        console.error('[Game] 配置加载失败:', error)
        GameStateManager.sendFlowEvent({ type: 'ERROR', error: `配置加载失败: ${error}` })
        // 显示错误提示
        this.add.text(
          this.scale.width * 0.5,
          this.scale.height * 0.5,
          '配置加载失败，请检查控制台',
          {
            fontSize: '24px',
            color: '#ff0000',
            align: 'center'
          }
        ).setOrigin(0.5)
      })
    } else {
      console.log('[Game] 配置已加载或游戏已开始，跳过配置加载')
    }
  }

  private handleSceneStart(): void {
    console.log('[Game] handleSceneStart() 被调用')
    
    // 检查 GameStateManager 是否已初始化
    // 如果未初始化，说明这是场景的首次启动，不需要处理重启逻辑
    let gameStateManager: GameStateManager | null = null
    try {
      gameStateManager = GameStateManager.getInstance()
    } catch (error) {
      // GameStateManager 未初始化，这是正常的首次启动场景
      // 不需要处理重启逻辑，直接返回
      console.log('[Game] handleSceneStart: GameStateManager 未初始化，这是首次启动场景，跳过重启检查')
      return
    }
    
    // GameStateManager 已初始化，检查是否是重启场景（从 GameOver 场景返回）
    try {
      // getState() 内部会检查 game 对象是否存在，如果不存在会抛出错误
      const state = gameStateManager.getState()
      
      // 验证状态对象是否有效
      if (!state || typeof state !== 'object') {
        console.warn('[Game] handleSceneStart: 获取的状态无效', state)
        return
      }
      
      if (this.wasGameOver && state.flowState === 'playing' && state.currentScene === 'Game' && !state.gameOver) {
        console.log('[Game] 检测到重启场景，重置游戏')
        this.restartGame()
        this.wasGameOver = false // 重置标志
        return
      }
    } catch (error) {
      // getState() 可能因为 game 对象不存在而抛出错误，这是正常的
      console.log('[Game] handleSceneStart: 获取状态失败（可能是首次启动）', error)
      // 不抛出错误，只是记录日志
    }
  }

  preload(): void {
    // Game 场景不需要在 preload 中加载资源
    // 资源已在 Preloader 场景中加载完成
    // 配置加载在 create 阶段异步进行
  }

  private async loadGameConfig(): Promise<void> {
    // 从 GameStateManager 加载游戏配置
    const config = await this.gameState.loadConfig('game_config.json')

    // 初始化管理器（配置已由 GameStateManager 设置）
    this.initManagers(config)
    this.initVariables()
    this.initGame()
    
    // 通知状态机配置已加载（在初始化完成后）
    GameStateManager.sendFlowEvent({ type: 'CONFIG_LOADED' })
    console.log('[Game] 已发送 CONFIG_LOADED 事件')
  }

  private initManagers(config: GameConfig): void {
    // 初始化 Socket 管理器
    this.socketManager = SocketManager.getInstance()

    // 连接 WebSocket
    config.teams.forEach(team => {
      if (team.name !== 'L' && team.name !== 'R') return

      const wsUrl = team.ws_url || (team.who && config.servers[team.who])
      if (wsUrl) {
        this.socketManager.connectTeam(team.name, wsUrl)
        if (team.name === 'L') {
          this.gameState.setLTeamConnection(true, team.who || '-')
        } else {
          this.gameState.setRTeamConnection(true, team.who || '-')
        }
      }
    })

    // 订阅 Socket 事件
    this.socketManager.on(SocketEvent.ACTIONS_RECEIVED, (...args: unknown[]) => {
      const team = args[0] as Team
      const actions = args[1] as PlayerActions
      this.updatePlayerInfo(team, actions)
    })
  }

  private initVariables(): void {
    // ========== 职责划分 ==========
    // GameStateManager 负责：游戏状态管理（gameStarted, gamePaused, score等）
    // Game 场景负责：场景初始化（地图参数、地图生成、游戏对象位置等）
    
    // 1. 重置游戏状态（由 GameStateManager 负责）
    // 注意：如果是从 restartGame() 调用，状态已经重置过了，这里会再次重置以确保一致性
    this.gameState.resetGameState()
    
    // 2. 重置场景特定的状态（场景内部实现细节）
    this.stageSent = false
    this.lastSendTime = 0
    
    // 3. 先重置团队状态和地图数据（清空旧数据）
    this.gameState.resetTeamStates()
    this.gameState.resetMapState()
    
    // 4. 初始化地图参数（由 MapManager 统一管理）
    // 参考 MapDemo.vue：使用 game_config.json 中的 mapWidth 和 mapHeight
    const centerX = this.scale.width * 0.5
    const centerY = this.scale.height * 0.5
    const tileSize = 32 // 默认 tileSize，MapManager 会自动从配置读取
    
    // 从配置中获取地图尺寸，如果没有则使用动态计算
    const config = this.gameState.getState().config
    const mapWidth = config?.setup?.mapWidth || Math.floor((this.scale.width / tileSize) - 5 * 2)
    const mapHeight = config?.setup?.mapHeight || Math.floor((this.scale.height / tileSize) - 5 * 2)
    const mapX = centerX - (mapWidth * tileSize * 0.5)
    const mapY = centerY - (mapHeight * tileSize * 0.5)
    
    console.log('[Game] 地图参数计算:', {
      scaleWidth: this.scale.width,
      scaleHeight: this.scale.height,
      tileSize,
      mapWidth,
      mapHeight,
      mapX,
      mapY,
      configMapWidth: config?.setup?.mapWidth,
      configMapHeight: config?.setup?.mapHeight
    })
    
    // 5. 生成地图（由 MapManager 统一管理，只生成地图数据：墙壁和障碍物）
    const mapManager = MapManager.getInstance()
    
    // 设置地图参数（由 MapManager 统一管理）
    mapManager.setMapParams({
      centerX,
      centerY,
      mapWidth,
      mapHeight,
      mapX,
      mapY,
      tileSize
    })
    
    mapManager.generateMap()
    
    // 6. 生成 TeamStates（由 GameStateManager 统一管理）
    const obstacles = mapManager.getObstacles()
    this.gameState.generateTeamStates(obstacles, mapManager)
    
    // 地图诊断日志
    mapManager.logMapDiagnostics()
  }



  private initGame(): void {
    // 初始化地图管理器（统一管理地图生成和渲染）
    this.mapManager = MapManager.getInstance()
    
    // 获取地图参数（通过 MapManager）
    const mapParams = this.mapManager.getMapParams()
    
    // 初始化路径可视化管理器
    this.pathVisualizationManager = PathVisualizationManager.getInstance()
    this.pathVisualizationManager.initialize(this)
    this.pathVisualizationManager.setEnabled(true) // 默认启用路径可视化
    
    // 初始化 UI 管理器
    this.uiManager = new UIManager(this)

    // 创建 UI 组件
    this.uiManager.createComponent('lScore', UIComponentType.SCORE_TEXT, 'L', 30, 20)
    this.uiManager.createComponent('rScore', UIComponentType.SCORE_TEXT, 'R', this.scale.width - 450, 20)
    this.uiManager.createComponent('tutorial', UIComponentType.TUTORIAL_TEXT, mapParams.centerX, mapParams.centerY)
    this.uiManager.createComponent('gameOver', UIComponentType.GAME_OVER_TEXT, this.scale.width * 0.5, this.scale.height * 0.5)
    
    const state = this.gameState.getState()
    this.uiManager.createComponent('lTeamWho', UIComponentType.TEAM_NAME_TEXT, 'L', 30, 60)
    this.uiManager.createComponent('rTeamWho', UIComponentType.TEAM_NAME_TEXT, 'R', this.scale.width - 450, 60)
    this.uiManager.updateComponent('lTeamWho', state.lTeamWho)
    this.uiManager.updateComponent('rTeamWho', state.rTeamWho)

    // 初始化动画（必须在创建玩家之前）
    this.uiManager.initAnimations()

    // 初始化物理管理器（需要在创建游戏对象之前初始化）
    const callbacks: CollisionCallbacks = {
      onScoreUpdate: (team: Team) => this.updateTeamScore(team),
      onCreateFlag: (scene: Phaser.Scene, x: number, y: number, team: Team, canPickup: boolean) => {
        return new Flag(scene, x, y, team, canPickup)
      }
    }
    this.physicsManager = new PhysicsManager(this, callbacks)

    // 初始化输入管理器
    console.log('[Game] 开始初始化输入管理器...')
    
    // Phaser 3 的键盘输入应该自动启用，检查是否可用
    if (!this.input.keyboard) {
      console.warn('[Game] 警告：键盘输入不可用，可能影响游戏控制')
      return
    }
    
    console.log('[Game] 键盘输入可用')

    const awsdKeys = this.input.keyboard.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.W,
      left: Phaser.Input.Keyboard.KeyCodes.A,
      down: Phaser.Input.Keyboard.KeyCodes.S,
      right: Phaser.Input.Keyboard.KeyCodes.D
    }) as Phaser.Types.Input.Keyboard.CursorKeys

    const keyboardStrategy = new KeyboardInputStrategy(awsdKeys)
    const remoteStrategy = new RemoteInputStrategy()
    const hybridStrategy = new HybridInputStrategy(keyboardStrategy, remoteStrategy)
    this.inputManager = new InputManager(hybridStrategy)
    
    // 初始化输入管理器（包括游戏控制）
    console.log('[Game] 调用 inputManager.initialize()')
    this.inputManager.initialize(this, () => {
      console.log('[Game] startGame 回调被调用')
      this.startGame()
    })
    console.log('[Game] 输入管理器初始化完成')

    // 记录地图参数（mapManager 已在上面初始化）
    console.log('[Game] 初始化 MapManager，参数:', {
      ...mapParams,
      scaleWidth: this.scale.width,
      scaleHeight: this.scale.height
    })
    
    // 检查资源是否已加载
    const tilemapKey = ASSETS.tilemapTiledJSON?.map.key
    const tilesetKey = ASSETS.spritesheet?.tiles.key
    console.log('[Game] 检查资源加载状态:', {
      tilemapExists: this.cache.tilemap.exists(tilemapKey || ''),
      tilesetExists: this.textures.exists(tilesetKey || ''),
      tilemapKey,
      tilesetKey
    })
    
    // 初始化地图渲染器（地图参数由 MapManager 统一管理）
    this.mapManager.initializeRenderer(this)

    // 创建地图图层
    console.log('[Game] 开始创建地图图层...')
    this.mapManager.createGroundLayer()
    console.log('[Game] 背景图层创建完成')
    this.mapManager.createLevelLayer()
    console.log('[Game] 关卡图层创建完成')
    
    // 获取地图数据（通过 MapManager）
    const walls = this.mapManager.getWalls()
    const obstacles = this.mapManager.getObstacles()
    // TeamStates 由 GameStateManager 统一管理
    const teamStates = this.gameState.getTeamStates()
    
    console.log('[Game] 开始渲染地图元素...', {
      walls: walls.length,
      obstacles1: obstacles.obstacles1.length,
      obstacles2: obstacles.obstacles2.length,
      lteamPrison: teamStates.lTeamState.prison.length,
      rteamPrison: teamStates.rTeamState.prison.length,
      lteamTarget: teamStates.lTeamState.target.length,
      rteamTarget: teamStates.rTeamState.target.length
    })
    
    if (walls.length === 0) {
      console.warn('[Game] 警告：墙壁数据为空！地图可能未正确生成。')
    }
    
    // 统一通过 MapManager 渲染地图
    this.mapManager.renderMap()
    console.log('[Game] 地图元素渲染完成')

    // 创建边界
    const startY = mapParams.centerY - mapParams.mapHeight * mapParams.tileSize / 2
    const endY = mapParams.centerY + mapParams.mapHeight * mapParams.tileSize / 2
    this.mapManager.createBoundaryLayer(startY, endY)
    console.log('[Game] 边界图层创建完成')
    
    console.log('[Game] 地图初始化完成！地图应该可见了。')

    // 初始化队伍（使用 GameStateManager 统一管理）
    const teams = this.gameState.initTeams(this, this.mapManager, this.physicsManager)
    this.lteamFlags = teams.lteamFlags
    this.rteamFlags = teams.rteamFlags
    this.lteamPlayers = teams.lteamPlayers
    this.rteamPlayers = teams.rteamPlayers
    this.lteamTargetZone = teams.lteamTargetZone
    this.rteamTargetZone = teams.rteamTargetZone
    this.lteamPrisonZone = teams.lteamPrisonZone
    this.rteamPrisonZone = teams.rteamPrisonZone

    // 初始化物理
    this.initPhysics()
  }

  private initPhysics(): void {
    // 设置游戏对象组（PhysicsManager 需要这些来处理碰撞）
    this.physicsManager.setGameObjects(
      this.mapManager,
      this.lteamPlayers,
      this.rteamPlayers,
      this.lteamFlags,
      this.rteamFlags
    )

    // 设置碰撞检测（由 PhysicsManager 负责）
    this.physicsManager.setupCollisions(
      this.lteamPlayers,
      this.rteamPlayers,
      this.lteamFlags,
      this.rteamFlags,
      this.lteamTargetZone,
      this.rteamTargetZone,
      this.lteamPrisonZone,
      this.rteamPrisonZone
    )
  }


  update(time: number, delta: number): void {
    // 检查管理器是否已初始化（可能在配置加载完成前就被调用）
    if (!this.inputManager || !this.lteamPlayers || !this.rteamPlayers) {
      return
    }
    
    // 即使游戏未开始，也要更新输入管理器（用于处理空格键开始游戏）
    if (!this.gameStarted) {
      this.inputManager.update(time, delta)
      return
    }
    
    if (this.gamePaused) return

    // 更新输入管理器
    this.inputManager.update(time, delta)

    // 移动玩家
    let playersReady = 0
    let totalPlayers = 0
    const EPSILON = 0.1

    const tick = (canGoNextTile: boolean) => {
      this.lteamPlayers.getChildren().forEach((child: Phaser.GameObjects.GameObject) => {
        const player = child as Player
        totalPlayers++
        player.setCanGoNextTile(canGoNextTile)
        player.update(time, delta)
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const dx = Math.abs(playerSprite.x - player.target.x)
        const dy = Math.abs(playerSprite.y - player.target.y)
        if (dx < EPSILON && dy < EPSILON) {
          playersReady++
        }
      })

      this.rteamPlayers.getChildren().forEach((child: Phaser.GameObjects.GameObject) => {
        const player = child as Player
        totalPlayers++
        player.setCanGoNextTile(canGoNextTile)
        player.update(time, delta)
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const dx = Math.abs(playerSprite.x - player.target.x)
        const dy = Math.abs(playerSprite.y - player.target.y)
        if (dx < EPSILON && dy < EPSILON) {
          playersReady++
        }
      })
    }

    tick(false)

    if (playersReady !== totalPlayers) {
      this.stageSent = false
      return
    }

    tick(true)

    // 发送状态更新
    if (!this.stageSent && time - this.lastSendTime >= 600) {
      this.stageSent = true
      this.lastSendTime = time
      this.sendStatusUpdate(time)
    }
    
    // 🎯 持续更新路径可视化，确保路径始终显示
    this.updatePathVisualization()
  }

  // 存储从后端接收的路径数据
  private playerPaths: Map<string, Position[]> = new Map()

  private updatePathVisualization(): void {
    if (!this.pathVisualizationManager || !this.pathVisualizationManager.isEnabled()) {
      return
    }

    // 🎯 使用从后端接收的路径数据，确保路径持续显示
    const currentPlayerNames = new Set<string>()
    
    // 更新所有有路径数据的玩家
    this.playerPaths.forEach((path, playerName) => {
      currentPlayerNames.add(playerName)
      if (path && path.length > 0) {
        // 获取玩家颜色（L队白色，R队黑色）
        const color = playerName.startsWith('L') ? 0xffffff : 0x000000  // L队白色，R队黑色
        this.pathVisualizationManager.setPath(playerName, path, color)
      } else {
        // 路径为空，清除可视化
        this.pathVisualizationManager.clearPath(playerName)
      }
    })
    
    // 🎯 清除不在当前路径数据中的玩家的路径可视化
    // 但保留有路径数据的玩家的可视化（即使数据暂时没有更新）
    const pathsMap = (this.pathVisualizationManager as any).paths as Map<string, any>
    if (pathsMap) {
      pathsMap.forEach((_visualization, playerName) => {
        // 如果玩家不在当前路径数据中，检查玩家是否还存在
        if (!currentPlayerNames.has(playerName)) {
          // 检查是否有对应的玩家对象（玩家可能已经不存在）
          const lteamPlayers = this.lteamPlayers?.getChildren() as Player[] || []
          const rteamPlayers = this.rteamPlayers?.getChildren() as Player[] || []
          const allPlayers = [...lteamPlayers, ...rteamPlayers]
          const playerExists = allPlayers.some(p => p.name === playerName)
          
          if (!playerExists) {
            // 玩家不存在，清除路径
            this.pathVisualizationManager.clearPath(playerName)
          }
        }
      })
    }
  }

  private sendStatusUpdate(time: number): void {
    // 检查必要的对象是否已初始化
    if (!this.lteamPlayers || !this.rteamPlayers || !this.lteamFlags || !this.rteamFlags || !this.socketManager) {
      return
    }
    
    // 从游戏对象获取最新状态
    const lteamPlayerStatus = (this.lteamPlayers.getChildren() as Player[]).map(p => p.getStatus())
    const lteamFlagStatus = (this.lteamFlags.getChildren() as Flag[]).map(f => f.getStatus())
    const rteamPlayerStatus = (this.rteamPlayers.getChildren() as Player[]).map(p => p.getStatus())
    const rteamFlagStatus = (this.rteamFlags.getChildren() as Flag[]).map(f => f.getStatus())

    // 发送状态更新（由 SocketManager 封装 payload 构建逻辑）
    this.socketManager.sendGameStatus({
      time,
      lteamPlayerStatus,
      lteamFlagStatus,
      rteamPlayerStatus,
      rteamFlagStatus
    })
  }

  private updatePlayerInfo(teamName: Team, data: PlayerActions): void {
    try {
      // 检查数据是否为空
      if (!data || typeof data !== 'object') {
        console.warn(`无效的 actions 对象 from ${teamName} team:`, data)
        return
      }

      // 验证 players 字段
      // 参考 frontend/src/scenes/Game.js updatePlayerInfo() 方法
      // frontend 会检查 players 是否存在且是对象，空对象也会继续处理（只是不会设置动作）
      if (!data.players || typeof data.players !== 'object' || Array.isArray(data.players)) {
        // 空对象是正常情况（服务器可能返回空字典），不输出日志
        // 只有格式错误时才输出警告
        if (!data.players || Array.isArray(data.players)) {
          console.warn(`无效的 players 字段 from ${teamName} team:`, data.players)
        }
        return
      }

      // 验证玩家名称和方向
      Object.keys(data.players).forEach(playerName => {
        const direction = data.players[playerName]
        if (!playerName.startsWith(teamName)) {
          console.warn(`Invalid operation to control player ${playerName} for team ${teamName}`)
          return
        }
        if (direction !== 'up' && direction !== 'down' && direction !== 'left' && direction !== 'right' && direction !== '') {
          console.warn(`Invalid operation to move player to direction ${direction}`)
          return
        }
      })

      const teamPlayers = teamName === 'L' 
        ? this.lteamPlayers.getChildren() as Player[]
        : this.rteamPlayers.getChildren() as Player[]

      if (!teamPlayers || teamPlayers.length === 0) {
        console.warn(`未找到 ${teamName} 队的玩家`)
        return
      }

      // For each team player, we will set its direction.
      teamPlayers.forEach(player => {
        const remoteControl = data.players[player.name]
        // remoteControl 可能是 undefined，这是正常的（如果后端没有为该玩家返回动作）
        if (remoteControl !== undefined) {
          // 先设置路径（用于预判）
          if (data.paths && data.paths[player.name]) {
            player.setPlannedPath(data.paths[player.name])
          }
          // 然后设置指令
          player.setRemoteControl(remoteControl)
          this.inputManager.setRemoteControl(remoteControl)
          // 输出动作信息
          if (remoteControl) {
            console.log(`[Game] ${teamName}队 ${player.name} 动作: ${remoteControl}`)
          }
        }
      })

      // 处理路径数据（如果存在）
      if (data.paths && typeof data.paths === 'object' && !Array.isArray(data.paths)) {
        // 🎯 合并路径数据，而不是清除所有路径（避免L队和R队的路径互相覆盖）
        // 只清除当前队伍的路径，保留其他队伍的路径
        const currentTeamPlayerNames = new Set<string>()
        Object.keys(data.paths).forEach(playerName => {
          const path = data.paths![playerName]
          if (Array.isArray(path) && path.length > 0) {
            // 确保路径格式正确：每个点都有 x 和 y
            const validPath = path.filter((p: any) => p && typeof p.x === 'number' && typeof p.y === 'number')
            if (validPath.length > 0) {
              this.playerPaths.set(playerName, validPath)
              currentTeamPlayerNames.add(playerName)
              
              // 详细日志：路径信息
              const start = validPath[0]
              const end = validPath[validPath.length - 1]
              const action = data.players[playerName] || '无动作'
              
              // 获取玩家当前位置
              const player = teamPlayers.find(p => p.name === playerName)
              let currentPos = ''
              if (player) {
                const playerStatus = player.getStatus()
                currentPos = `当前: (${playerStatus.posX}, ${playerStatus.posY})`
              } else {
                currentPos = '当前: 未知'
              }
              
              // 获取下一步位置（路径的第二个点，如果存在）
              let nextPos = ''
              if (validPath.length >= 2) {
                const next = validPath[1]
                nextPos = ` → 下一步: (${next.x}, ${next.y})`
              } else {
                nextPos = ' → 下一步: 无'
              }
              
              // 耗时信息
              let timingInfo = ''
              if (data.timings && data.timings[playerName]) {
                const timing = data.timings[playerName]
                if (typeof timing === 'object') {
                  const algorithm = timing.algorithm || 'unknown'
                  const total = timing.total || 0
                  const details: string[] = []
                  if (timing.influence_zone) details.push(`影响区域: ${timing.influence_zone.toFixed(2)}ms`)
                  if (timing.weight_map) details.push(`权重地图: ${timing.weight_map.toFixed(2)}ms`)
                  if (timing.pathfinding) details.push(`路径查找: ${timing.pathfinding.toFixed(2)}ms`)
                  if (timing.obstacle_filter) details.push(`障碍过滤: ${timing.obstacle_filter.toFixed(2)}ms`)
                  timingInfo = ` | 算法: ${algorithm}, 总耗时: ${total.toFixed(2)}ms${details.length > 0 ? ` (${details.join(', ')})` : ''}`
                } else {
                  timingInfo = ` | 耗时: ${timing.toFixed(2)}ms`
                }
              }
              
              console.log(
                `[Game] ${teamName}队 ${playerName} | 路径长度: ${validPath.length} | ` +
                `起点: (${start.x}, ${start.y}) → ${currentPos}${nextPos} → 终点: (${end.x}, ${end.y}) | ` +
                `动作: ${action}${timingInfo}`
              )
            }
          }
        })
        
        // 🎯 清除当前队伍中不再有路径数据的玩家的路径（但保留其他队伍的路径）
        const pathsToRemove: string[] = []
        this.playerPaths.forEach((_path, playerName) => {
          // 如果玩家属于当前队伍，但不在新的路径数据中，清除其路径
          if (playerName.startsWith(teamName) && !currentTeamPlayerNames.has(playerName)) {
            pathsToRemove.push(playerName)
          }
        })
        pathsToRemove.forEach(playerName => {
          this.playerPaths.delete(playerName)
          console.log(`[Game] 清除玩家 ${playerName} 的旧路径（当前队伍但无新数据）`)
        })
        
        // 立即更新路径可视化
        this.updatePathVisualization()
      } else {
        // 🎯 如果没有路径数据，只清除当前队伍的路径，保留其他队伍的路径
        const pathsToRemove: string[] = []
        this.playerPaths.forEach((_path, playerName) => {
          if (playerName.startsWith(teamName)) {
            pathsToRemove.push(playerName)
          }
        })
        pathsToRemove.forEach(playerName => {
          this.playerPaths.delete(playerName)
          if (this.pathVisualizationManager) {
            this.pathVisualizationManager.clearPath(playerName)
          }
        })
      }
    } catch (e) {
      console.error(`处理 ${teamName} 队消息时出错:`, e, '原始数据:', data)
    }
  }

  private startGame(): void {
    // 使用 GameStateManager 统一管理状态
    this.gameState.startGame()
    this.uiManager.hideComponent('tutorial')
    
    // 通知状态机游戏开始
    GameStateManager.sendFlowEvent({ type: 'START_GAME' })

    // 获取地图数据（通过 MapManager）
    const mapParams = this.mapManager.getMapParams()
    const walls = this.mapManager.getWalls()
    const obstacles = this.mapManager.getObstacles()

    // 发送游戏初始化消息（由 SocketManager 封装 payload 构建逻辑）
    // TeamStates 由 GameStateManager 统一管理
    const teamStates = this.gameState.getTeamStates()
    this.socketManager.sendGameInit({
      mapWidth: mapParams.mapWidth,
      mapHeight: mapParams.mapHeight,
      walls: walls,
      obstacles1: obstacles.obstacles1,
      obstacles2: obstacles.obstacles2,
      lteamPrison: teamStates.lTeamState.prison,
      lteamTarget: teamStates.lTeamState.target,
      rteamPrison: teamStates.rTeamState.prison,
      rteamTarget: teamStates.rTeamState.target
    })
  }

  removeFlagItem(flag: Flag): void {
    if (flag.team === 'L') {
      this.lteamFlags.remove(flag, true, true)
    } else if (flag.team === 'R') {
      this.rteamFlags.remove(flag, true, true)
    }
  }

  private updateTeamScore(team: Team): void {
    const state = this.gameState.getState()
    
    if (team === 'L') {
      // 更新 GameStateManager（单一数据源，会自动同步到团队状态）
      const newScore = state.lTeamScore + 1
      this.gameState.updateLTeamScore(newScore)
      
      // 更新 UI
      this.uiManager.updateComponent('lScore', newScore)
      
      // 检查游戏结束条件
      if (newScore === this.NUM_FLAGS) {
        this.gameOver(team)
      }
    } else if (team === 'R') {
      // 更新 GameStateManager（单一数据源，会自动同步到团队状态）
      const newScore = state.rTeamScore + 1
      this.gameState.updateRTeamScore(newScore)
      
      // 更新 UI
      this.uiManager.updateComponent('rScore', newScore)
      
      // 检查游戏结束条件
      if (newScore === this.NUM_FLAGS) {
        this.gameOver(team)
      }
    }
  }

  private gameOver(team: Team): void {
    // 使用 GameStateManager 统一管理状态
    this.gameState.endGame(team)
    this.uiManager.updateComponent('gameOver', `${team}Team`)
    this.uiManager.showComponent('gameOver')

    // 标记游戏已结束（用于检测重启）
    this.wasGameOver = true

    // 通知状态机游戏结束（这会切换到 GameOver 场景）
    GameStateManager.sendFlowEvent({ type: 'END_GAME', winner: team })

    // 发送游戏结束消息（由 SocketManager 封装 payload 构建逻辑）
    this.socketManager.sendGameFinished()
  }

  private restartGame(): void {
    console.log('[Game] 开始重置游戏...')
    
    // 1. 检查 GameStateManager 是否已初始化
    let gameStateManager: GameStateManager | null = null
    try {
      gameStateManager = GameStateManager.getInstance()
      // getState() 内部会检查 game 对象是否存在，如果不存在会抛出错误
      // 先尝试获取状态来验证 game 对象是否存在
      gameStateManager.getState()
    } catch (error) {
      console.error('[Game] 无法重置游戏：GameStateManager 未初始化或 game 对象不存在', error)
      return
    }
    
    // 2. 清除所有路径可视化
    try {
      if (this.pathVisualizationManager) {
        this.pathVisualizationManager.clearAllPaths()
      }
      this.playerPaths.clear()
    } catch (error) {
      console.warn('[Game] 清除路径可视化时出错（可忽略）:', error)
    }

    // 3. 安全地清理游戏对象组（避免访问未定义的对象）
    try {
      if (this.lteamPlayers && typeof this.lteamPlayers.clear === 'function') {
        this.lteamPlayers.clear(true, true)
      }
      if (this.rteamPlayers && typeof this.rteamPlayers.clear === 'function') {
        this.rteamPlayers.clear(true, true)
      }
      if (this.lteamFlags && typeof this.lteamFlags.clear === 'function') {
        this.lteamFlags.clear(true, true)
      }
      if (this.rteamFlags && typeof this.rteamFlags.clear === 'function') {
        this.rteamFlags.clear(true, true)
      }
    } catch (error) {
      console.warn('[Game] 清理游戏对象时出错（可忽略）:', error)
    }
    
    // 4. 重置 UI
    try {
      if (this.uiManager) {
        this.uiManager.hideComponent('gameOver')
        this.uiManager.showComponent('tutorial') // 显示教程提示，等待用户按空格开始
        // 重置分数显示
        this.uiManager.updateComponent('lScore', 0)
        this.uiManager.updateComponent('rScore', 0)
      }
    } catch (error) {
      console.warn('[Game] 重置 UI 时出错（可忽略）:', error)
    }
    
    // 5. 重置场景特定的状态
    this.stageSent = false
    this.lastSendTime = 0
    
    // 6. 重置游戏状态（必须在 GameStateManager 已初始化的情况下）
    try {
      if (gameStateManager) {
        gameStateManager.resetGameState()
        gameStateManager.resetTeamStates()
        gameStateManager.resetMapState()
      }
    } catch (error) {
      console.error('[Game] 重置游戏状态时出错:', error)
      return
    }
    
    // 7. 检查配置是否存在
    let config: GameConfig | null = null
    try {
      const state = gameStateManager!.getState()
      config = state?.config || null
    } catch (error) {
      console.error('[Game] 获取配置时出错:', error)
      config = null
    }
    
    if (!config) {
      console.error('[Game] 重启游戏时配置不存在，需要重新加载配置')
      this.configLoaded = false
      this.loadGameConfig().catch((error) => {
        console.error('[Game] 重置游戏时配置加载失败:', error)
      })
      return
    }
    
    // 8. 重新初始化游戏（这会重置所有状态、地图、团队状态等）
    try {
      // 重新初始化变量和游戏对象
      this.initVariables()
      this.initGame()
      console.log('[Game] 游戏重置完成，等待用户按空格键开始新游戏')
    } catch (initError) {
      console.error('[Game] 重新初始化游戏时出错:', initError)
      // 如果初始化失败，尝试重新加载配置
      this.configLoaded = false
      this.loadGameConfig().catch((loadError) => {
        console.error('[Game] 重新加载配置失败:', loadError)
      })
    }
  }

  // 暴露给 Player 和 Flag 使用的方法
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number } {
    return this.mapManager.getMapOffset()
  }

  isWall(x: number, y: number): boolean {
    return this.mapManager.isWall(x, y)
  }
}

