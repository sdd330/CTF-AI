import type { Team, Position, PlayerStatus, FlagStatus } from '@/types'
import { WorldManager } from './WorldManager'
import { SocketConnectionManager } from './socket/SocketConnectionManager'
import { SocketMessageHandler } from './socket/SocketMessageHandler'
import { MessageSender } from './socket/MessageSender'
import { EventEmitter } from './socket/EventEmitter'

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

export interface GameStatusParams {
  time: number
  lteamPlayerStatus: PlayerStatus[]
  lteamFlagStatus: FlagStatus[]
  rteamPlayerStatus: PlayerStatus[]
  rteamFlagStatus: FlagStatus[]
}

export enum SocketEvent {
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  MESSAGE = 'message',
  ERROR = 'error',
  ACTIONS_RECEIVED = 'actions_received'
}

type EventListener = (...args: unknown[]) => void

export class SocketManager {
  private static instance: SocketManager | null = null
  private connectionManager: SocketConnectionManager
  private messageHandler: SocketMessageHandler
  private messageSender: MessageSender
  private emitter: EventEmitter

  private constructor(world: WorldManager) {
    this.emitter = new EventEmitter()
    this.connectionManager = new SocketConnectionManager(this.emitter)
    this.messageHandler = new SocketMessageHandler(this.emitter)
    this.messageSender = new MessageSender(world, this.connectionManager)

    this.emitter.on(SocketEvent.MESSAGE, (team: Team, data: unknown) => {
      this.messageHandler.handleMessage(team, data)
    })
  }

  static getInstance(world: WorldManager): SocketManager {
    if (!SocketManager.instance) {
      SocketManager.instance = new SocketManager(world)
    }
    return SocketManager.instance
  }

  /**
   * 获取连接管理器（用于测试）
   */
  getConnectionManager(): SocketConnectionManager {
    return this.connectionManager
  }

  connectTeam(team: Team, url: string): void {
    this.connectionManager.connectTeam(team, url)
  }

  disconnectTeam(team: Team): void {
    this.connectionManager.disconnectTeam(team)
  }

  sendGameInit(params: GameInitParams): void {
    this.messageSender.sendGameInit(params)
  }

  sendGameStatus(params: GameStatusParams): void {
    this.messageSender.sendGameStatus(params)
  }

  sendGameFinished(): void {
    this.messageSender.sendGameFinished()
  }

  isConnected(team: Team): boolean {
    return this.connectionManager.isConnected(team)
  }

  on(event: SocketEvent, listener: EventListener): void {
    this.emitter.on(event, listener)
  }

  off(event: SocketEvent, listener: EventListener): void {
    this.emitter.off(event, listener)
  }

  disconnectAll(): void {
    this.connectionManager.disconnectAll()
    this.emitter.removeAllListeners()
  }

  getConnectionStatus(): Record<Team, boolean> {
    return this.connectionManager.getConnectionStatus()
  }
}

