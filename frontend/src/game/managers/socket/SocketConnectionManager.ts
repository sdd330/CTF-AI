/**
 * SocketConnectionManager - Socket 连接管理器
 * 负责 WebSocket 连接的建立和断开
 */
import type { Team } from '@/types'
import { TeamSocket } from './TeamSocket'
import { EventEmitter } from './EventEmitter'

/**
 * Socket 连接管理器
 */
export class SocketConnectionManager {
  private sockets: Map<Team, TeamSocket> = new Map()
  private emitter: EventEmitter

  constructor(emitter: EventEmitter) {
    this.emitter = emitter
  }

  /**
   * 连接队伍
   */
  connectTeam(team: Team, url: string): void {
    if (this.sockets.has(team)) {
      this.disconnectTeam(team)
    }

    const socket = new TeamSocket(url, team, this.emitter)
    this.sockets.set(team, socket)
    socket.connect()
  }

  /**
   * 断开连接
   */
  disconnectTeam(team: Team): void {
    const socket = this.sockets.get(team)
    if (socket) {
      socket.disconnect()
      this.sockets.delete(team)
    }
  }

  /**
   * 断开所有连接
   */
  disconnectAll(): void {
    this.sockets.forEach((socket) => {
      socket.disconnect()
    })
    this.sockets.clear()
  }

  /**
   * 检查连接状态
   */
  isConnected(team: Team): boolean {
    const socket = this.sockets.get(team)
    return socket ? socket.isConnected() : false
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus(): Record<Team, boolean> {
    return {
      L: this.isConnected('L'),
      R: this.isConnected('R')
    }
  }

  /**
   * 获取 Socket 实例
   */
  getSocket(team: Team): TeamSocket | undefined {
    return this.sockets.get(team)
  }
}
