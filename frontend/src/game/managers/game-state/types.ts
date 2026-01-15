/**
 * GameState 类型定义
 */
import type { Team, PlayerStatus, FlagStatus, GameConfig, Position } from '@/types'

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
export const initialState: GameState = {
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
export const REGISTRY_KEYS = {
  GAME_STATE: 'gameState'
} as const
