/**
 * SocketManager - 网络通信管理器
 * 设计模式：单例模式 + 发布订阅（EventEmitter）
 */
import type { Team, GameInitPayload, GameStatusPayload, GameFinishedPayload, Position, PlayerStatus, FlagStatus, Direction } from '@/types'
import type { PlayerActions } from '@/types'
import { GameStateManager } from './GameStateManager'

// Init 消息参数接口
export interface GameInitParams {
  mapWidth: number
  mapHeight: number
  walls: Array<Position & { tileId?: number }>
  obstacles1: Position[]
  obstacles2: Position[]
  lteamPrison: Position[]
  lteamTarget: Position[]
  rteamPrison: Position[]
  rteamTarget: Position[]
}

// Status 消息参数接口
export interface GameStatusParams {
  time: number
  lteamPlayerStatus: PlayerStatus[]
  lteamFlagStatus: FlagStatus[]
  rteamPlayerStatus: PlayerStatus[]
  rteamFlagStatus: FlagStatus[]
}

// 事件类型
export enum SocketEvent {
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  MESSAGE = 'message',
  ERROR = 'error',
  ACTIONS_RECEIVED = 'actions_received'
}

// 事件监听器类型
type EventListener = (...args: unknown[]) => void

// 事件发射器（发布订阅模式）
class EventEmitter {
  private events: Map<SocketEvent, Set<EventListener>> = new Map()

  // 订阅事件
  on(event: SocketEvent, listener: EventListener): void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set())
    }
    this.events.get(event)!.add(listener)
  }

  // 取消订阅
  off(event: SocketEvent, listener: EventListener): void {
    const listeners = this.events.get(event)
    if (listeners) {
      listeners.delete(listener)
    }
  }

  // 发布事件
  emit(event: SocketEvent, ...args: unknown[]): void {
    const listeners = this.events.get(event)
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(...args)
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error)
        }
      })
    }
  }

  // 清除所有监听器
  removeAllListeners(event?: SocketEvent): void {
    if (event) {
      this.events.delete(event)
    } else {
      this.events.clear()
    }
  }
}

// WebSocket 连接包装类
class TeamSocket {
  private ws: WebSocket | null = null
  private url: string
  private team: Team
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private emitter: EventEmitter

  constructor(url: string, team: Team, emitter: EventEmitter) {
    this.url = url
    this.team = team
    this.emitter = emitter
  }

  connect(): void {
    try {
      this.ws = new WebSocket(this.url)
      this.setupEventHandlers()
    } catch (error) {
      console.error(`Failed to create WebSocket for ${this.team} team:`, error)
      this.emitter.emit(SocketEvent.ERROR, this.team, error)
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log(`${this.team} team connected`)
      this.reconnectAttempts = 0
      this.emitter.emit(SocketEvent.CONNECT, this.team)
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emitter.emit(SocketEvent.MESSAGE, this.team, data)
        
        // 服务器返回的格式是 { "players": { "L0": "up", "L1": "down", ... }, "paths": { "L0": [{x, y}, ...], ... } }
        // 参考 frontend/src/scenes/Game.js updatePlayerInfo() 方法
        // 只有当 data.players 存在且是对象时才处理
        if (data.players && typeof data.players === 'object' && !Array.isArray(data.players)) {
          const playersObj = data.players as Record<string, Direction>
          const pathsObj = (data.paths && typeof data.paths === 'object' && !Array.isArray(data.paths)) 
            ? data.paths as Record<string, Array<{x: number, y: number}>>
            : {}
          const timingsObj = (data.timings && typeof data.timings === 'object' && !Array.isArray(data.timings))
            ? data.timings as Record<string, Record<string, number> | number>
            : undefined
          
          // 参考 frontend：即使 players 对象为空，也应该处理（只是不会设置任何动作）
          // frontend 会遍历 Object.keys(actions.players)，空对象时循环不执行，这是正常行为
          if (Object.keys(playersObj).length > 0) {
            // 有玩家动作时，发送事件
            const playerActions: PlayerActions = {
              players: playersObj,
              paths: pathsObj,
              timings: timingsObj
            }
            this.emitter.emit(SocketEvent.ACTIONS_RECEIVED, this.team, playerActions)
          }
          // 空对象时不发送事件，也不输出日志（这是正常情况，服务器可能返回空字典）
        } else {
          // data.players 不存在或格式不正确，记录但不报错（可能是其他类型的消息）
          if (data.action !== 'init' && data.action !== 'status' && data.action !== 'finished') {
            console.log(`[SocketManager] ${this.team} 队收到非 actions 消息:`, data)
          }
        }
      } catch (error) {
        console.error(`Failed to parse message from ${this.team} team:`, error)
        this.emitter.emit(SocketEvent.ERROR, this.team, error)
      }
    }

    this.ws.onerror = (error) => {
      console.error(`WebSocket error for ${this.team} team:`, error)
      this.emitter.emit(SocketEvent.ERROR, this.team, error)
    }

    this.ws.onclose = () => {
      console.log(`${this.team} team disconnected`)
      this.emitter.emit(SocketEvent.DISCONNECT, this.team)
      this.attemptReconnect()
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Attempting to reconnect ${this.team} team (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  send(data: string | object): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return false
    }

    try {
      const payload = typeof data === 'string' ? data : JSON.stringify(data)
      
      // 检查缓冲区大小
      if (this.ws.bufferedAmount < 1024 * 1024) { // 小于1MB
        this.ws.send(payload)
        return true
      } else {
        console.warn(`${this.team} team WebSocket buffer is full, skipping send`)
        return false
      }
    } catch (error) {
      console.error(`Failed to send message to ${this.team} team:`, error)
      this.emitter.emit(SocketEvent.ERROR, this.team, error)
      return false
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }
}

// Socket 管理器（单例模式）
export class SocketManager {
  private static instance: SocketManager | null = null
  private sockets: Map<Team, TeamSocket> = new Map()
  private emitter: EventEmitter = new EventEmitter()

  private constructor() {
    // 私有构造函数，防止外部实例化
  }

  // 获取单例实例
  static getInstance(): SocketManager {
    if (!SocketManager.instance) {
      SocketManager.instance = new SocketManager()
    }
    return SocketManager.instance
  }

  // 连接队伍
  connectTeam(team: Team, url: string): void {
    if (this.sockets.has(team)) {
      this.disconnectTeam(team)
    }

    const socket = new TeamSocket(url, team, this.emitter)
    this.sockets.set(team, socket)
    socket.connect()
  }

  // 断开连接
  disconnectTeam(team: Team): void {
    const socket = this.sockets.get(team)
    if (socket) {
      socket.disconnect()
      this.sockets.delete(team)
    }
  }

  // 发送初始化消息（封装 payload 构建逻辑）
  sendGameInit(params: GameInitParams): void {
    const gameState = GameStateManager.getInstance().getState()
    
    // 构建地图 payload
    const mapPayload = {
      width: params.mapWidth,
      height: params.mapHeight,
      walls: params.walls.map(w => ({ x: w.x, y: w.y })),
      obstacles: params.obstacles1.concat(params.obstacles2).concat(
        params.obstacles2.map(w => ({ x: w.x, y: w.y + 1 }))
      )
    }

    // 发送给 L 队
    if (this.isConnected('L')) {
      const payload: GameInitPayload = {
        action: 'init',
        map: mapPayload,
        numPlayers: gameState.numPlayers,
        numFlags: gameState.numFlags,
        myteamName: 'L',
        myteamPrison: params.lteamPrison,
        myteamTarget: params.lteamTarget,
        opponentPrison: params.rteamPrison,
        opponentTarget: params.rteamTarget
      }
      this.sendInit('L', payload)
    }

    // 发送给 R 队
    if (this.isConnected('R')) {
      const payload: GameInitPayload = {
        action: 'init',
        map: mapPayload,
        numPlayers: gameState.numPlayers,
        numFlags: gameState.numFlags,
        myteamName: 'R',
        myteamPrison: params.rteamPrison,
        myteamTarget: params.rteamTarget,
        opponentPrison: params.lteamPrison,
        opponentTarget: params.lteamTarget
      }
      this.sendInit('R', payload)
    }
  }

  /**
   * 发送初始化消息（内部使用）
   */
  private sendInit(team: Team, payload: GameInitPayload): boolean {
    const socket = this.sockets.get(team)
    return socket ? socket.send(payload) : false
  }

  // 发送状态更新（封装 payload 构建逻辑）
  sendGameStatus(params: GameStatusParams): void {
    const gameStateManager = GameStateManager.getInstance()
    const gameState = gameStateManager.getState()

    // 同步状态到 GameStateManager（单一数据源）
    gameStateManager.updateLTeamPlayers(params.lteamPlayerStatus)
    gameStateManager.updateLTeamFlags(params.lteamFlagStatus)
    gameStateManager.updateRTeamPlayers(params.rteamPlayerStatus)
    gameStateManager.updateRTeamFlags(params.rteamFlagStatus)
 
    // 发送给 L 队
    if (this.isConnected('L')) {
      const payload: GameStatusPayload = {
        action: 'status',
        time: params.time,
        myteamName: 'L',
        myteamPlayer: params.lteamPlayerStatus,
        myteamFlag: params.lteamFlagStatus,
        myteamScore: gameState.lTeamScore,
        opponentPlayer: params.rteamPlayerStatus,
        opponentFlag: params.rteamFlagStatus,
        opponentScore: gameState.rTeamScore
      }
      this.sendStatus('L', payload)
    }

    // 发送给 R 队
    if (this.isConnected('R')) {
      const payload: GameStatusPayload = {
        action: 'status',
        time: params.time,
        myteamName: 'R',
        myteamPlayer: params.rteamPlayerStatus,
        myteamFlag: params.rteamFlagStatus,
        myteamScore: gameState.rTeamScore,
        opponentPlayer: params.lteamPlayerStatus,
        opponentFlag: params.lteamFlagStatus,
        opponentScore: gameState.lTeamScore
      }
      this.sendStatus('R', payload)
    }
  }

  /**
   * 发送状态更新（内部使用）
   */
  private sendStatus(team: Team, payload: GameStatusPayload): boolean {
    const socket = this.sockets.get(team)
    return socket ? socket.send(payload) : false
  }

  // 发送游戏结束消息（封装 payload 构建逻辑）
  sendGameFinished(): void {
    const gameState = GameStateManager.getInstance().getState()

    // 发送给 L 队
    if (this.isConnected('L')) {
      const payload: GameFinishedPayload = {
        action: 'finished',
        myteamScore: gameState.lTeamScore,
        opponentScore: gameState.rTeamScore
      }
      this.sendFinished('L', payload)
    }

    // 发送给 R 队
    if (this.isConnected('R')) {
      const payload: GameFinishedPayload = {
        action: 'finished',
        myteamScore: gameState.rTeamScore,
        opponentScore: gameState.lTeamScore
      }
      this.sendFinished('R', payload)
    }
  }

  /**
   * 发送游戏结束消息（内部使用）
   */
  private sendFinished(team: Team, payload: GameFinishedPayload): boolean {
    const socket = this.sockets.get(team)
    return socket ? socket.send(payload) : false
  }

  // 检查连接状态
  isConnected(team: Team): boolean {
    const socket = this.sockets.get(team)
    return socket ? socket.isConnected() : false
  }

  // 订阅事件
  on(event: SocketEvent, listener: EventListener): void {
    this.emitter.on(event, listener)
  }

  // 取消订阅
  off(event: SocketEvent, listener: EventListener): void {
    this.emitter.off(event, listener)
  }

  // 断开所有连接
  disconnectAll(): void {
    this.sockets.forEach((socket) => {
      socket.disconnect()
    })
    this.sockets.clear()
    this.emitter.removeAllListeners()
  }

  // 获取连接状态
  getConnectionStatus(): Record<Team, boolean> {
    return {
      L: this.isConnected('L'),
      R: this.isConnected('R')
    }
  }
}

