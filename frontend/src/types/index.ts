/**
 * 队伍类型
 */
export type Team = 'L' | 'R'

/**
 * 移动方向类型
 */
export type Direction = 'up' | 'down' | 'left' | 'right' | ''

/**
 * 位置坐标接口
 */
export interface Position {
  x: number
  y: number
}

/**
 * 玩家状态接口
 * 用于 WebSocket 通信和游戏状态同步
 */
export interface PlayerStatus {
  name: string
  team: Team
  posX: number
  posY: number
  hasFlag: boolean
  inPrison: boolean
  inPrisonTimeLeft: number
  inPrisonDuration: number
}

/**
 * 旗帜状态接口
 * 用于 WebSocket 通信和游戏状态同步
 */
export interface FlagStatus {
  canPickup: boolean
  posX: number
  posY: number
}

export interface GameStatusPayload {
  action: 'status'
  time: number
  myteamName: Team
  myteamPlayer: PlayerStatus[]
  myteamFlag: FlagStatus[]
  myteamScore: number
  opponentPlayer: PlayerStatus[]
  opponentFlag: FlagStatus[]
  opponentScore: number
}

export interface GameInitPayload {
  action: 'init'
  map: {
    width: number
    height: number
    walls: Position[]
    obstacles: Position[]
  }
  numPlayers: number
  numFlags: number
  myteamName: Team
  myteamPrison: Position[]
  myteamTarget: Position[]
  opponentPrison: Position[]
  opponentTarget: Position[]
}

export interface GameFinishedPayload {
  action: 'finished'
  myteamScore: number
  opponentScore: number
}

export interface PlayerActions {
  players: Record<string, Direction>
  paths?: Record<string, Position[]>
  timings?: Record<string, Record<string, number> | number>  // 路径计算耗时信息
}

export interface TeamConfig {
  name: Team
  who?: string
  ws_url?: string
}

export interface GameSetup {
  numPlayers: number
  numFlags: number
  useRandomFlags: boolean
  mapWidth?: number
  mapHeight?: number
}

export interface GameConfig {
  teams: TeamConfig[]
  setup: GameSetup
  servers: Record<string, string>
}

/**
 * 游戏模式类型
 */
export type GameMode = 'classic' | 'speed' | 'team_deathmatch'

/**
 * 日志级别
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

/**
 * 性能指标接口
 */
export interface PerformanceMetrics {
  fps: number
  frameTime: number
  renderTime: number
  updateTime: number
  networkLatency?: number
}

/**
 * 调试信息接口
 */
export interface DebugInfo {
  gameState: string
  players: number
  flags: number
  connections: Record<Team, boolean>
  performance?: PerformanceMetrics
}

