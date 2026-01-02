/**
 * GameStateManager - 游戏状态管理器
 * 使用 Phaser Registry 进行状态管理
 * 
 * 职责：
 * - 管理所有游戏状态（gameStarted, gamePaused, gameOver, winner）
 * - 管理队伍分数（lTeamScore, rTeamScore）
 * - 管理玩家和旗帜状态（lTeamPlayers, rTeamPlayers, lTeamFlags, rTeamFlags）
 * - 管理游戏配置（config, numPlayers, numFlags, useRandomFlags）
 * - 管理 WebSocket 连接状态（lTeamConnected, rTeamConnected, lTeamWho, rTeamWho）
 * - 管理游戏流程状态（flowState, flowSubState, currentScene等）
 * - 管理地图数据（walls, obstacles1, obstacles2）- 地图参数由 MapManager 管理
 * 
 * 单一数据源原则：所有游戏状态都由 GameStateManager 统一管理
 */
import Phaser from 'phaser'
import type { Team, PlayerStatus, FlagStatus, GameConfig, Position } from '@/types'
import { Player } from '../objects/Player'
import { Flag } from '../objects/Flag'

// 团队状态接口
export interface TeamState {
  score: number
  playerSpriteChoice: number
  flags: Position[]
  players: Array<Position & { name: string }>
  target: Position[]
  prison: Position[]
}

// 游戏流程状态类型
export type GameFlowState = 'loading' | 'ready' | 'playing' | 'ended'

// 游戏流程子状态
export type GameFlowSubState = 'loadingAssets' | 'loadingConfig' | 'running' | 'paused'

// 游戏流程事件
export type GameFlowEvent =
  | { type: 'ASSETS_LOADED' }
  | { type: 'CONFIG_LOADED' }
  | { type: 'START_GAME' }
  | { type: 'PAUSE_GAME' }
  | { type: 'RESUME_GAME' }
  | { type: 'END_GAME'; winner: Team }
  | { type: 'RESTART' }
  | { type: 'RESTART_LOADING' }
  | { type: 'ERROR'; error: string }

// 游戏状态接口
export interface GameState {
  // 游戏状态
  gameStarted: boolean
  gamePaused: boolean
  gameOver: boolean
  winner: Team | null

  // 队伍状态
  lTeamScore: number
  rTeamScore: number
  lTeamPlayers: PlayerStatus[]
  rTeamPlayers: PlayerStatus[]
  lTeamFlags: FlagStatus[]
  rTeamFlags: FlagStatus[]

  // 配置
  config: GameConfig | null
  numPlayers: number
  numFlags: number
  useRandomFlags: boolean

  // WebSocket 连接状态
  lTeamConnected: boolean
  rTeamConnected: boolean
  lTeamWho: string
  rTeamWho: string

  // 游戏流程状态
  flowState: GameFlowState
  flowSubState: GameFlowSubState | null
  currentScene: string
  initialized: boolean
  assetsLoaded: boolean
  configLoaded: boolean
  error: string | null

  // 团队状态
  lTeamState: TeamState
  rTeamState: TeamState

  // 地图数据（地图参数由 MapManager 管理）
  walls: Array<Position & { tileId?: number }>
  obstacles1: Position[]
  obstacles2: Position[]
  numObstacles1: number
  numObstacles2: number
}

// 初始状态
const initialState: GameState = {
  gameStarted: false,
  gamePaused: false,
  gameOver: false,
  winner: null,
  lTeamScore: 0,
  rTeamScore: 0,
  lTeamPlayers: [],
  rTeamPlayers: [],
  lTeamFlags: [],
  rTeamFlags: [],
  config: null,
  numPlayers: 3,
  numFlags: 9,
  useRandomFlags: true,
  lTeamConnected: false,
  rTeamConnected: false,
  lTeamWho: '-',
  rTeamWho: '-',
  // 流程状态
  flowState: 'loading',
  flowSubState: 'loadingAssets',
  currentScene: 'Boot',
  initialized: false,
  assetsLoaded: false,
  configLoaded: false,
  error: null,
  // 团队状态
  lTeamState: {
    score: 0,
    playerSpriteChoice: 1,
    flags: [],
    players: [],
    target: [],
    prison: []
  },
  rTeamState: {
    score: 0,
    playerSpriteChoice: 4,
    flags: [],
    players: [],
    target: [],
    prison: []
  },
  // 地图数据（地图参数由 MapManager 管理）
  walls: [],
  obstacles1: [],
  obstacles2: [],
  numObstacles1: 8,
  numObstacles2: 4
}

// Registry 键名常量
const REGISTRY_KEYS = {
  GAME_STATE: 'gameState'
} as const

/**
 * GameStateManager 类
 * 使用 Phaser Registry 存储状态
 */
export class GameStateManager {
  private static instance: GameStateManager | null = null
  private game: Phaser.Game | null = null

  // 游戏对象组（由 initTeams 创建）
  private lteamFlags: Phaser.GameObjects.Group | null = null
  private rteamFlags: Phaser.GameObjects.Group | null = null
  private lteamPlayers: Phaser.GameObjects.Group | null = null
  private rteamPlayers: Phaser.GameObjects.Group | null = null

  private constructor() {}

  /**
   * 初始化 GameStateManager（需要在 Phaser 游戏实例创建后调用）
   */
  static initialize(game: Phaser.Game): GameStateManager {
    if (!GameStateManager.instance) {
      GameStateManager.instance = new GameStateManager()
    }
    GameStateManager.instance.game = game
    
    // 初始化 registry 数据
    if (!game.registry.has(REGISTRY_KEYS.GAME_STATE)) {
      game.registry.set(REGISTRY_KEYS.GAME_STATE, { ...initialState })
    }
    
    return GameStateManager.instance
  }

  /**
   * 获取单例实例
   */
  static getInstance(): GameStateManager {
    if (!GameStateManager.instance) {
      throw new Error('GameStateManager 未初始化，请先调用 initialize(game)')
    }
    return GameStateManager.instance
  }

  /**
   * 获取当前状态
   */
  getState(): GameState {
    if (!this.game) {
      throw new Error('GameStateManager 未初始化')
    }
    return this.game.registry.get(REGISTRY_KEYS.GAME_STATE) as GameState
  }

  /**
   * 更新状态（部分更新）
   */
  private updateState(updates: Partial<GameState>): void {
    if (!this.game) {
      throw new Error('GameStateManager 未初始化')
    }
    const currentState = this.getState()
    const newState = { ...currentState, ...updates }
    this.game.registry.set(REGISTRY_KEYS.GAME_STATE, newState)
    
    // 触发事件通知
    this.game.events.emit('gameStateChanged', newState)
  }

  /**
   * 订阅状态变化
   */
  onStateChange(callback: (state: GameState) => void): () => void {
    if (!this.game) {
      throw new Error('GameStateManager 未初始化')
    }
    this.game.events.on('gameStateChanged', callback)
    return () => {
      if (this.game) {
        this.game.events.off('gameStateChanged', callback)
      }
    }
  }


  // ========== 配置相关 ==========

  /**
   * 加载游戏配置（从 game_config.json）
   * 如果加载失败，使用默认配置
   */
  async loadConfig(configPath: string = 'game_config.json'): Promise<GameConfig> {
    try {
      const resp = await fetch(configPath)
      if (!resp.ok) {
        throw new Error(`无法加载 ${configPath}: HTTP ${resp.status}`)
      }

      const text = await resp.text()
      if (!text || text.trim().length === 0) {
        throw new Error(`${configPath} 返回空内容`)
      }

      const data: GameConfig = JSON.parse(text)

      if (!data.setup) {
        throw new Error(`${configPath} 缺少 'setup' 字段`)
      }

      console.log('[GameStateManager] 配置加载成功:', data)
      
      // 设置配置
      this.setConfig(data)
      
      // 更新配置加载状态
      this.updateState({
        configLoaded: true
      })

      return data
    } catch (error) {
      console.error(`[GameStateManager] 加载配置失败，使用默认配置:`, error)
      
      // 使用默认配置
      const defaultConfig: GameConfig = {
        teams: [{ name: 'L', who: 'user48-1' }, { name: 'R', who: 'user48-2' }],
        setup: {
          numPlayers: 3,
          numFlags: 9,
          useRandomFlags: true,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {
          "user48-1": "ws://localhost:34712",
          "user48-2": "ws://localhost:34713"
        }
      }
      
      this.setConfig(defaultConfig)
      
      // 更新配置加载状态（即使使用默认配置）
      this.updateState({
        configLoaded: true
      })

      return defaultConfig
    }
  }

  /**
   * 获取当前配置
   */
  getConfig(): GameConfig | null {
    return this.getState().config
  }

  setConfig(config: GameConfig): void {
    this.updateState({
      config,
      numPlayers: config.setup.numPlayers,
      numFlags: config.setup.numFlags,
      useRandomFlags: config.setup.useRandomFlags
    })
  }

  // ========== 游戏控制 ==========

  startGame(): void {
    this.updateState({
      gameStarted: true,
      gamePaused: false,
      gameOver: false
    })
  }

  pauseGame(): void {
    const state = this.getState()
    this.updateState({
      gamePaused: !state.gamePaused
    })
  }

  endGame(team: Team): void {
    this.updateState({
      gameOver: true,
      winner: team,
      gameStarted: false
    })
  }

  reset(): void {
    const state = this.getState()
    this.updateState({
      ...initialState,
      config: state.config // 保留配置
    })
  }

  resetGameState(): void {
    this.updateState({
      gameStarted: false,
      gamePaused: false,
      gameOver: false,
      winner: null,
      lTeamScore: 0,
      rTeamScore: 0,
      lTeamPlayers: [],
      rTeamPlayers: [],
      lTeamFlags: [],
      rTeamFlags: []
    })
    // 重置团队状态分数
    this.updateLTeamStateScore(0)
    this.updateRTeamStateScore(0)
  }

  // ========== 分数更新 ==========

  updateLTeamScore(score: number): void {
    this.updateLTeamStateScore(score)
  }

  updateRTeamScore(score: number): void {
    this.updateRTeamStateScore(score)
  }

  // ========== 玩家状态更新 ==========

  updateLTeamPlayers(players: PlayerStatus[]): void {
    this.updateState({ lTeamPlayers: players })
  }

  updateRTeamPlayers(players: PlayerStatus[]): void {
    this.updateState({ rTeamPlayers: players })
  }

  // ========== 旗帜状态更新 ==========

  updateLTeamFlags(flags: FlagStatus[]): void {
    this.updateState({ lTeamFlags: flags })
  }

  updateRTeamFlags(flags: FlagStatus[]): void {
    this.updateState({ rTeamFlags: flags })
  }

  // ========== 连接状态更新 ==========

  setLTeamConnection(connected: boolean, who: string = '-'): void {
    this.updateState({
      lTeamConnected: connected,
      lTeamWho: who
    })
  }

  setRTeamConnection(connected: boolean, who: string = '-'): void {
    this.updateState({
      rTeamConnected: connected,
      rTeamWho: who
    })
  }

  // ========== 团队状态管理 ==========

  /**
   * 设置 L 队状态
   */
  setLTeamState(state: Partial<TeamState>): void {
    const currentState = this.getState()
    this.updateState({
      lTeamState: { ...currentState.lTeamState, ...state }
    })
  }

  /**
   * 设置 R 队状态
   */
  setRTeamState(state: Partial<TeamState>): void {
    const currentState = this.getState()
    this.updateState({
      rTeamState: { ...currentState.rTeamState, ...state }
    })
  }

  /**
   * 更新 L 队分数（同步到团队状态）
   */
  updateLTeamStateScore(score: number): void {
    const state = this.getState()
    this.updateState({
      lTeamScore: score,
      lTeamState: { ...state.lTeamState, score }
    })
  }

  /**
   * 更新 R 队分数（同步到团队状态）
   */
  updateRTeamStateScore(score: number): void {
    const state = this.getState()
    this.updateState({
      rTeamScore: score,
      rTeamState: { ...state.rTeamState, score }
    })
  }

  /**
   * 重置团队状态
   */
  resetTeamStates(): void {
    this.updateState({
      lTeamState: {
        score: 0,
        playerSpriteChoice: 1,
        flags: [],
        players: [],
        target: [],
        prison: []
      },
      rTeamState: {
        score: 0,
        playerSpriteChoice: 4,
        flags: [],
        players: [],
        target: [],
        prison: []
      }
    })
  }

  // ========== 地图状态管理 ==========

  /**
   * 设置地图数据
   */
  setMapData(data: {
    walls?: Array<Position & { tileId?: number }>
    obstacles1?: Position[]
    obstacles2?: Position[]
  }): void {
    this.updateState(data)
  }

  /**
   * 重置地图数据（地图参数由 MapManager 管理，不在此重置）
   */
  resetMapState(): void {
    this.updateState({
      walls: [],
      obstacles1: [],
      obstacles2: []
    })
  }

  // ========== 游戏流程管理 ==========

  /**
   * 发送流程事件（静态方法，方便外部调用）
   */
  static sendFlowEvent(event: GameFlowEvent): void {
    try {
      const manager = GameStateManager.getInstance()
      manager.sendFlowEvent(event)
    } catch (error) {
      console.warn('[GameStateManager] 发送流程事件失败，GameStateManager 未初始化:', error)
    }
  }

  /**
   * 发送流程事件（实例方法）
   */
  sendFlowEvent(event: GameFlowEvent): void {
    const state = this.getState()
    
    switch (event.type) {
      case 'ASSETS_LOADED':
        if (state.flowState === 'loading' && state.flowSubState === 'loadingAssets') {
          this.updateState({
            assetsLoaded: true,
            flowSubState: 'loadingConfig'
          })
        }
        break

      case 'CONFIG_LOADED':
        if (state.flowState === 'loading' && state.flowSubState === 'loadingConfig') {
          this.updateState({
            configLoaded: true,
            initialized: true,
            flowState: 'ready',
            flowSubState: null,
            currentScene: 'Game'
          })
        }
        break

      case 'START_GAME':
        if (state.flowState === 'ready' && state.assetsLoaded && state.configLoaded && state.initialized) {
          this.updateState({
            flowState: 'playing',
            flowSubState: 'running',
            currentScene: 'Game'
          })
        }
        break

      case 'PAUSE_GAME':
        if (state.flowState === 'playing' && state.flowSubState === 'running') {
          this.updateState({
            flowSubState: 'paused'
          })
        }
        break

      case 'RESUME_GAME':
        if (state.flowState === 'playing' && state.flowSubState === 'paused') {
          this.updateState({
            flowSubState: 'running'
          })
        }
        break

      case 'END_GAME':
        this.updateState({
          flowState: 'ended',
          flowSubState: null,
          winner: event.winner,
          currentScene: 'GameOver'
        })
        break

      case 'RESTART':
        this.updateState({
          flowState: 'playing',
          flowSubState: 'running',
          currentScene: 'Game',
          gameOver: false,
          winner: null,
          error: null
        })
        break

      case 'RESTART_LOADING':
        this.updateState({
          flowState: 'loading',
          flowSubState: 'loadingAssets',
          currentScene: 'Preloader',
          initialized: false,
          assetsLoaded: false,
          configLoaded: false,
          winner: null,
          error: null
        })
        break

      case 'ERROR':
        this.updateState({
          error: event.error,
          flowState: 'loading',
          flowSubState: 'loadingAssets',
          currentScene: 'Preloader'
        })
        break
    }
  }


  // ========== TeamStates 生成 ==========

  /**
   * 生成旗帜位置
   * 参考 frontend/src/scenes/Game.js 的旗帜生成逻辑
   */
  generateFlags(
    obstacles: { obstacles1: Position[]; obstacles2: Position[] },
    mapWidth: number,
    mapHeight: number
  ): void {
    const state = this.getState()
    const numFlags = state.numFlags
    const useRandomFlags = state.useRandomFlags
    const obstacles1 = obstacles.obstacles1
    const obstacles2 = obstacles.obstacles2

    // 计算中间线（与后端保持一致：middle_line = width / 2.0）
    // L队领地：x < middle_line
    // R队领地：x >= middle_line
    const middleLine = mapWidth / 2.0
    const lMaxX = Math.floor(middleLine - 0.1)  // L队最大x坐标（确保 < middle_line）
    const rMinX = Math.ceil(middleLine)  // R队最小x坐标（确保 >= middle_line）

    let lFlags: Position[] = []
    let rFlags: Position[] = []

    if (useRandomFlags) {
      // 随机模式：在己方半场随机生成旗帜位置
      const notContains = (arr: Position[], x: number, y: number) => {
        return !arr.find(obj => obj.x === x && obj.y === y)
      }

      const MAX_RETRIES = 1000

      // L队旗帜：在左半场随机摆放
      for (let i = 0; i < numFlags; i++) {
        let retries = 0
        let found = false
        while (retries < MAX_RETRIES) {
          const x = Phaser.Math.RND.integerInRange(2, lMaxX)
          const y = Phaser.Math.RND.integerInRange(1, mapHeight - 3)
          if (
            notContains(obstacles1, x, y) &&
            notContains(obstacles2, x, y - 1) &&
            notContains(obstacles2, x, y) &&
            notContains(lFlags, x, y)
          ) {
            lFlags.push({ x, y })
            found = true
            break
          }
          retries++
        }
        if (!found) {
          // 如果找不到合适位置，使用固定位置（确保在左半场）
          const fallbackX = Math.min(1, lMaxX)
          lFlags.push({ x: fallbackX, y: i + 1 })
        }
      }

      // R队旗帜：在右半场随机摆放
      for (let i = 0; i < numFlags; i++) {
        let retries = 0
        let found = false
        while (retries < MAX_RETRIES) {
          const x = Phaser.Math.RND.integerInRange(rMinX, mapWidth - 2)
          const y = Phaser.Math.RND.integerInRange(1, mapHeight - 3)
          if (
            notContains(obstacles1, x, y) &&
            notContains(obstacles2, x, y - 1) &&
            notContains(obstacles2, x, y) &&
            notContains(rFlags, x, y)
          ) {
            rFlags.push({ x, y })
            found = true
            break
          }
          retries++
        }
        if (!found) {
          // 如果找不到合适位置，使用固定位置（确保在右半场）
          const fallbackX = Math.max(rMinX, mapWidth - 2)
          rFlags.push({ x: fallbackX, y: i + 1 })
        }
      }
    } else {
      // 固定模式：使用固定位置（确保在己方半场）
      lFlags = Array.from({ length: numFlags }, (_, i) => ({ 
        x: Math.min(1, lMaxX),  // 使用1或lMaxX中较小的值，确保在左半场
        y: i + 1 
      }))
      rFlags = Array.from({ length: numFlags }, (_, i) => ({ 
        x: Math.max(rMinX, mapWidth - 2),  // 使用rMinX或mapWidth-2中较大的值，确保在右半场
        y: i + 1 
      }))
    }

    // 更新到状态管理器
    this.setLTeamState({ flags: lFlags })
    this.setRTeamState({ flags: rFlags })
  }

  /**
   * 生成玩家位置
   * 参考 frontend/src/scenes/Game.js 的玩家生成逻辑
   */
  generatePlayers(mapWidth: number): void {
    const state = this.getState()
    const numPlayers = state.numPlayers
    const useRandomFlags = state.useRandomFlags

    const lPlayers = useRandomFlags
      ? Array.from({ length: numPlayers }, (_, i) => ({ x: 1, y: i + 1, name: `L${i}` }))
      : Array.from({ length: numPlayers }, (_, i) => ({ x: 2, y: i + 1, name: `L${i}` }))

    const rPlayers = useRandomFlags
      ? Array.from({ length: numPlayers }, (_, i) => ({ x: mapWidth - 2, y: i + 1, name: `R${i}` }))
      : Array.from({ length: numPlayers }, (_, i) => ({ x: mapWidth - 3, y: i + 1, name: `R${i}` }))

    // 更新到状态管理器
    this.setLTeamState({ players: lPlayers })
    this.setRTeamState({ players: rPlayers })
  }

  /**
   * 生成目标区域和监狱位置
   * 参考 frontend/src/scenes/Game.js 的位置计算
   */
  generateTargetsAndPrisons(mapWidth: number, mapHeight: number): void {

    // 参考 frontend/src/scenes/Game.js 的位置计算
    // frontend 使用: this.create3x3grid(2, this.mapHeight / 2)
    // 注意：frontend 中 mapHeight 可能是浮点数，但 create3x3grid 会处理
    // 为了保持一致，我们也使用 mapHeight / 2（不进行 Math.floor）
    const targetY = mapHeight / 2
    const prisonY = mapHeight - 3

    // create3x3grid 会处理浮点数，但我们需要确保坐标是整数
    // 所以使用 Math.floor 来确保坐标是整数
    const lTarget = this.create3x3grid(2, Math.floor(targetY))
    const lPrison = this.create3x3grid(2, Math.floor(prisonY))
    const rTarget = this.create3x3grid(mapWidth - 3, Math.floor(targetY))
    const rPrison = this.create3x3grid(mapWidth - 3, Math.floor(prisonY))

    // 更新到状态管理器
    this.setLTeamState({
      target: lTarget,
      prison: lPrison
    })
    this.setRTeamState({
      target: rTarget,
      prison: rPrison
    })
  }

  /**
   * 创建 3x3 网格位置
   * 参考 frontend/src/scenes/Game.js 的 create3x3grid 方法
   */
  private create3x3grid(x: number, y: number): Position[] {
    return [
      { x: x - 1, y: y - 1 }, { x: x, y: y - 1 }, { x: x + 1, y: y - 1 },
      { x: x - 1, y: y }, { x: x, y: y }, { x: x + 1, y: y },
      { x: x - 1, y: y + 1 }, { x: x, y: y + 1 }, { x: x + 1, y: y + 1 }
    ]
  }

  /**
   * 生成所有 TeamStates（旗帜、玩家、目标区域、监狱）
   * 应该在生成地图数据（墙壁、障碍物）之后调用
   * @param obstacles 障碍物数据
   * @param mapManager MapManager 实例，用于获取地图参数
   */
  generateTeamStates(
    obstacles: { obstacles1: Position[]; obstacles2: Position[] },
    mapManager: { getMapParams: () => { mapWidth: number; mapHeight: number } }
  ): void {
    const mapParams = mapManager.getMapParams()
    this.generateFlags(obstacles, mapParams.mapWidth, mapParams.mapHeight)
    this.generatePlayers(mapParams.mapWidth)
    this.generateTargetsAndPrisons(mapParams.mapWidth, mapParams.mapHeight)
  }

  /**
   * 获取团队状态数据（统一接口）
   */
  getTeamStates(): {
    lTeamState: TeamState
    rTeamState: TeamState
  } {
    const state = this.getState()
    return {
      lTeamState: state.lTeamState,
      rTeamState: state.rTeamState
    }
  }

  // ========== 队伍初始化 ==========

  /**
   * 初始化队伍（创建玩家、旗帜和区域对象）
   * 参考 frontend/src/scenes/Game.js 的 initTeams 方法
   */
  initTeams(
    scene: Phaser.Scene,
    mapManager: { getMapParams: () => { mapX: number; mapY: number; tileSize: number } },
    physicsManager: { addPhysicsBody: (body: Phaser.GameObjects.Zone) => void }
  ): {
    lteamFlags: Phaser.GameObjects.Group
    rteamFlags: Phaser.GameObjects.Group
    lteamPlayers: Phaser.GameObjects.Group
    rteamPlayers: Phaser.GameObjects.Group
    lteamTargetZone: Phaser.GameObjects.Zone
    rteamTargetZone: Phaser.GameObjects.Zone
    lteamPrisonZone: Phaser.GameObjects.Zone
    rteamPrisonZone: Phaser.GameObjects.Zone
  } {
    // 获取团队状态（由 GameStateManager 统一管理）
    const teamStates = this.getTeamStates()
    const mapParams = mapManager.getMapParams()

    // L队
    const lteamFlags = scene.add.group()
    const lteamPlayers = scene.add.group()

    teamStates.lTeamState.flags.forEach(flag => {
      const flagObj = new Flag(scene, flag.x, flag.y, 'L', true)
      lteamFlags.add(flagObj)
    })

    teamStates.lTeamState.players.forEach(player => {
      const playerObj = new Player(scene, player.name, player.x, player.y, 'L', teamStates.lTeamState.playerSpriteChoice, true)
      lteamPlayers.add(playerObj)
    })

    const lteamTargetZone = scene.add.zone(
      mapParams.mapX + (teamStates.lTeamState.target[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.lTeamState.target[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(lteamTargetZone)

    const lteamPrisonZone = scene.add.zone(
      mapParams.mapX + (teamStates.lTeamState.prison[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.lTeamState.prison[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(lteamPrisonZone)

    // R队
    const rteamFlags = scene.add.group()
    const rteamPlayers = scene.add.group()

    teamStates.rTeamState.flags.forEach(flag => {
      const flagObj = new Flag(scene, flag.x, flag.y, 'R', true)
      rteamFlags.add(flagObj)
    })

    teamStates.rTeamState.players.forEach(player => {
      const playerObj = new Player(scene, player.name, player.x, player.y, 'R', teamStates.rTeamState.playerSpriteChoice, false)
      rteamPlayers.add(playerObj)
    })

    const rteamTargetZone = scene.add.zone(
      mapParams.mapX + (teamStates.rTeamState.target[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.rTeamState.target[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(rteamTargetZone)

    const rteamPrisonZone = scene.add.zone(
      mapParams.mapX + (teamStates.rTeamState.prison[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.rTeamState.prison[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(rteamPrisonZone)

    // 存储组以便后续访问
    this.lteamFlags = lteamFlags
    this.rteamFlags = rteamFlags
    this.lteamPlayers = lteamPlayers
    this.rteamPlayers = rteamPlayers

    return {
      lteamFlags,
      rteamFlags,
      lteamPlayers,
      rteamPlayers,
      lteamTargetZone,
      rteamTargetZone,
      lteamPrisonZone,
      rteamPrisonZone
    }
  }

  /**
   * 获取 L 队旗帜组
   */
  getLTeamFlags(): Phaser.GameObjects.Group | null {
    return this.lteamFlags
  }

  /**
   * 获取 R 队旗帜组
   */
  getRTeamFlags(): Phaser.GameObjects.Group | null {
    return this.rteamFlags
  }

  /**
   * 获取 L 队玩家组
   */
  getLTeamPlayers(): Phaser.GameObjects.Group | null {
    return this.lteamPlayers
  }

  /**
   * 获取 R 队玩家组
   */
  getRTeamPlayers(): Phaser.GameObjects.Group | null {
    return this.rteamPlayers
  }

  // ========== 计算属性 ==========

  isGameActive(): boolean {
    const state = this.getState()
    return state.gameStarted && !state.gamePaused && !state.gameOver
  }

  // ========== 调试工具 ==========

  /**
   * 获取调试信息
   */
  getDebugInfo(): import('@/types').DebugInfo {
    const state = this.getState()
    return {
      gameState: state.flowState,
      players: state.lTeamPlayers.length + state.rTeamPlayers.length,
      flags: state.lTeamFlags.length + state.rTeamFlags.length,
      connections: {
        L: state.lTeamConnected,
        R: state.rTeamConnected
      }
    }
  }

  /**
   * 记录调试日志（分级日志系统）
   */
  log(level: import('@/types').LogLevel, message: string, data?: unknown): void {
    const timestamp = new Date().toISOString()
    const prefix = `[GameStateManager:${level.toUpperCase()}]`
    
    switch (level) {
      case 'debug':
        if (process.env.NODE_ENV === 'development') {
          console.debug(`${prefix} ${timestamp}`, message, data || '')
        }
        break
      case 'info':
        console.info(`${prefix} ${timestamp}`, message, data || '')
        break
      case 'warn':
        console.warn(`${prefix} ${timestamp}`, message, data || '')
        break
      case 'error':
        console.error(`${prefix} ${timestamp}`, message, data || '')
        break
    }
  }
}

/**
 * 状态查询辅助函数
 */
export const gameFlowQueries = {
  // 检查是否在加载状态
  isLoading: (state: GameState) => {
    return state.flowState === 'loading'
  },
  // 检查是否在游戏中
  isPlaying: (state: GameState) => {
    return state.flowState === 'playing'
  },
  // 检查是否暂停
  isPaused: (state: GameState) => {
    return state.flowState === 'playing' && state.flowSubState === 'paused'
  },
  // 检查是否运行中
  isRunning: (state: GameState) => {
    return state.flowState === 'playing' && state.flowSubState === 'running'
  },
  // 检查是否已结束
  isEnded: (state: GameState) => {
    return state.flowState === 'ended'
  },
  // 检查是否准备就绪
  isReady: (state: GameState) => {
    return state.flowState === 'ready'
  }
}
