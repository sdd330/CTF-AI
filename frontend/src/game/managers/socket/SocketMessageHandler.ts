/**
 * SocketMessageHandler - Socket 消息处理器
 * 负责消息的解析和路由
 */
import type { Team, Direction, PlayerActions } from '@/types'
import { SocketEvent } from '../SocketManager'
import { EventEmitter } from './EventEmitter'

/**
 * Socket 消息处理器
 */
export class SocketMessageHandler {
  private emitter: EventEmitter

  constructor(emitter: EventEmitter) {
    this.emitter = emitter
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(team: Team, data: unknown): void {
    try {
      const parsedData = typeof data === 'string' ? JSON.parse(data) : data
      
      // 服务器返回的格式是 { "players": { "L0": "up", "L1": "down", ... }, "paths": { "L0": [{x, y}, ...], ... } }
      if (parsedData.players && typeof parsedData.players === 'object' && !Array.isArray(parsedData.players)) {
        const playersObj = parsedData.players as Record<string, Direction>
        const pathsObj = (parsedData.paths && typeof parsedData.paths === 'object' && !Array.isArray(parsedData.paths)) 
          ? parsedData.paths as Record<string, Array<{x: number, y: number}>>
          : {}
        const timingsObj = (parsedData.timings && typeof parsedData.timings === 'object' && !Array.isArray(parsedData.timings))
          ? parsedData.timings as Record<string, Record<string, number> | number>
          : undefined
        
        // 只有当有玩家动作时才发送事件
        if (Object.keys(playersObj).length > 0) {
          console.log(`[SocketMessageHandler] ${team}队 📋 解析动作:`, {
            玩家数量: Object.keys(playersObj).length,
            玩家动作: playersObj,
            路径数量: Object.keys(pathsObj).length,
            有计时: timingsObj !== undefined
          })
          const playerActions: PlayerActions = {
            players: playersObj,
            paths: pathsObj,
            timings: timingsObj
          }
          this.emitter.emit(SocketEvent.ACTIONS_RECEIVED, team, playerActions)
        }
      } else {
        // data.players 不存在或格式不正确，记录但不报错（可能是其他类型的消息）
        if (parsedData.action !== 'init' && parsedData.action !== 'status' && parsedData.action !== 'finished') {
          console.log(`[SocketMessageHandler] ${team} 队收到非 actions 消息:`, parsedData)
        }
      }
    } catch (error) {
      console.error(`Failed to parse message from ${team} team:`, error)
      this.emitter.emit(SocketEvent.ERROR, team, error)
    }
  }
}
