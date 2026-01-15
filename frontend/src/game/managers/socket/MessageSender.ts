/**
 * MessageSender - 消息发送器
 * 负责构建和发送各种类型的消息
 */
import type { Team, GameInitPayload, GameStatusPayload, GameFinishedPayload } from '@/types'
import { WorldManager } from '../WorldManager'
import { SocketConnectionManager } from './SocketConnectionManager'
import type { GameInitParams, GameStatusParams } from '../SocketManager'

/**
 * 消息发送器
 */
export class MessageSender {
  constructor(
    private world: WorldManager,
    private connectionManager: SocketConnectionManager
  ) {}

  /**
   * 发送初始化消息
   */
  sendGameInit(params: GameInitParams): void {
    const state = this.world.getState()
    
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
    if (this.connectionManager.isConnected('L')) {
      const payload: GameInitPayload = {
        action: 'init',
        map: mapPayload,
        numPlayers: state.numPlayers,
        numFlags: state.numFlags,
        myteamName: 'L',
        myteamPrison: params.lteamPrison,
        myteamTarget: params.lteamTarget,
        opponentPrison: params.rteamPrison,
        opponentTarget: params.rteamTarget
      }
      this.sendInit('L', payload)
    }

    // 发送给 R 队
    if (this.connectionManager.isConnected('R')) {
      const payload: GameInitPayload = {
        action: 'init',
        map: mapPayload,
        numPlayers: state.numPlayers,
        numFlags: state.numFlags,
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
    console.log(`[MessageSender] 发送 init 给 ${team} 队:`, {
      地图: `${payload.map.width}x${payload.map.height}`,
      玩家数: payload.numPlayers,
      旗帜数: payload.numFlags,
      队伍: payload.myteamName,
      myteamPrison类型: Array.isArray(payload.myteamPrison) ? `数组(${payload.myteamPrison.length})` : typeof payload.myteamPrison,
      myteamTarget类型: Array.isArray(payload.myteamTarget) ? `数组(${payload.myteamTarget.length})` : typeof payload.myteamTarget,
      myteamTarget值: payload.myteamTarget
    })
    const socket = this.connectionManager.getSocket(team)
    const sent = socket ? socket.send(payload) : false
    if (!sent) {
      console.warn(`[MessageSender] ⚠️ ${team} 队 init 消息发送失败`)
    }
    return sent
  }

  /**
   * 发送状态更新
   */
  sendGameStatus(params: GameStatusParams): void {
    const state = this.world.getState()

    // 同步状态到 WorldManager（单一数据源）
    this.world.api.updateLTeamPlayers(params.lteamPlayerStatus)
    this.world.api.updateLTeamFlags(params.lteamFlagStatus)
    this.world.api.updateRTeamPlayers(params.rteamPlayerStatus)
    this.world.api.updateRTeamFlags(params.rteamFlagStatus)
 
    // 发送给 L 队
    if (this.connectionManager.isConnected('L')) {
      const payload: GameStatusPayload = {
        action: 'status',
        time: params.time,
        myteamName: 'L',
        myteamPlayer: params.lteamPlayerStatus,
        myteamFlag: params.lteamFlagStatus,
        myteamScore: state.lTeamScore,
        opponentPlayer: params.rteamPlayerStatus,
        opponentFlag: params.rteamFlagStatus,
        opponentScore: state.rTeamScore
      }
      this.sendStatus('L', payload)
    }

    // 发送给 R 队
    if (this.connectionManager.isConnected('R')) {
      const payload: GameStatusPayload = {
        action: 'status',
        time: params.time,
        myteamName: 'R',
        myteamPlayer: params.rteamPlayerStatus,
        myteamFlag: params.rteamFlagStatus,
        myteamScore: state.rTeamScore,
        opponentPlayer: params.lteamPlayerStatus,
        opponentFlag: params.lteamFlagStatus,
        opponentScore: state.lTeamScore
      }
      this.sendStatus('R', payload)
    }
  }

  /**
   * 发送状态更新（内部使用）
   */
  private sendStatus(team: Team, payload: GameStatusPayload): boolean {
    const timeInSeconds = (payload.time / 1000).toFixed(1)
    console.log(`[MessageSender] 📤 发送 status 给 ${team} 队: time=${timeInSeconds}s, myteam玩家=${payload.myteamPlayer.length}, 分数=${payload.myteamScore}`)
    const socket = this.connectionManager.getSocket(team)
    const sent = socket ? socket.send(payload) : false
    if (!sent) {
      console.error(`[MessageSender] ❌ ${team} 队 status 消息发送失败！`)
    }
    return sent
  }

  /**
   * 发送游戏结束消息
   */
  sendGameFinished(): void {
    const state = this.world.getState()

    // 发送给 L 队
    if (this.connectionManager.isConnected('L')) {
      const payload: GameFinishedPayload = {
        action: 'finished',
        myteamScore: state.lTeamScore,
        opponentScore: state.rTeamScore
      }
      this.sendFinished('L', payload)
    }

    // 发送给 R 队
    if (this.connectionManager.isConnected('R')) {
      const payload: GameFinishedPayload = {
        action: 'finished',
        myteamScore: state.rTeamScore,
        opponentScore: state.lTeamScore
      }
      this.sendFinished('R', payload)
    }
  }

  /**
   * 发送游戏结束消息（内部使用）
   */
  private sendFinished(team: Team, payload: GameFinishedPayload): boolean {
    console.log(`[MessageSender] 发送 finished 给 ${team} 队: 己方分数=${payload.myteamScore}, 对方分数=${payload.opponentScore}`)
    const socket = this.connectionManager.getSocket(team)
    return socket ? socket.send(payload) : false
  }
}
