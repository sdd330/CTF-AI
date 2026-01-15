import type { Team } from '@/types'
import { SocketEvent } from '../SocketManager'
import { EventEmitter } from './EventEmitter'

export class TeamSocket {
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
      console.log(`[TeamSocket ${this.team}] ✅ WebSocket 已连接，等待后端消息...`)
      this.reconnectAttempts = 0
      this.emitter.emit(SocketEvent.CONNECT, this.team)
    }

    this.ws.onmessage = (event) => {
      this.emitter.emit(SocketEvent.MESSAGE, this.team, event.data)
    }

    this.ws.onerror = (error) => {
      console.error(`WebSocket error for ${this.team} team:`, error)
      this.emitter.emit(SocketEvent.ERROR, this.team, error)
    }

    this.ws.onclose = () => {
      console.log(`[TeamSocket ${this.team}] ❌ WebSocket 已断开`)
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
      
      if (this.ws.bufferedAmount < 1024 * 1024) {
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

  /**
   * 获取 WebSocket 实例（用于测试）
   */
  getWebSocket(): WebSocket | null {
    return this.ws
  }
}
