/**
 * SocketManager Payload 格式一致性测试
 * 确保新项目 (fets) 的 socket payload 格式与旧项目 (frontend) 完全一致
 * 
 * 参考 frontend/src/scenes/Game.js 中的 payload 格式：
 * - init 消息: startGame() 方法 (738-783行)
 * - status 消息: update() 方法 (102-144行)
 * - finished 消息: GameOver() 方法 (977-993行)
 * - 接收消息: updatePlayerInfo() 方法 (212-263行)
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { SocketManager, SocketEvent } from '../SocketManager'
import { GameStateManager } from '../GameStateManager'
import type { Team, PlayerStatus, FlagStatus } from '@/types'

// Mock WebSocket
class MockWebSocket {
  readyState: number = WebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  bufferedAmount = 0
  private sentMessages: string[] = []

  constructor(public url: string) {
    setTimeout(() => {
      this.readyState = WebSocket.OPEN as number
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }

  send(data: string) {
    this.sentMessages.push(data)
  }

  close() {
    this.readyState = WebSocket.CLOSED as number
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }

  getSentMessages(): string[] {
    return this.sentMessages
  }

  getLastSentMessage(): any {
    const last = this.sentMessages[this.sentMessages.length - 1]
    return last ? JSON.parse(last) : null
  }

  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', {
        data: JSON.stringify(data)
      }))
    }
  }
}

// 替换全局 WebSocket
const originalWebSocket = globalThis.WebSocket
beforeEach(() => {
  globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket
})

afterEach(() => {
  globalThis.WebSocket = originalWebSocket
  SocketManager.getInstance().disconnectAll()
})

describe('SocketManager Payload 格式一致性测试', () => {
  beforeEach(() => {
    // 初始化 GameStateManager
    const registryData: Record<string, any> = {}
    const mockGame = {
      registry: {
        set: vi.fn((key: string, value: any) => {
          registryData[key] = value
        }),
        get: vi.fn((key: string) => registryData[key]),
        remove: vi.fn((key: string) => {
          delete registryData[key]
        }),
        exists: vi.fn((key: string) => key in registryData),
        has: vi.fn((key: string) => key in registryData)
      },
      events: {
        emit: vi.fn()
      }
    } as unknown as Phaser.Game
    
    const manager = GameStateManager as any
    manager.instance = null
    GameStateManager.initialize(mockGame)
    const gameState = GameStateManager.getInstance()
    gameState.setConfig({
      teams: [],
      setup: {
        numPlayers: 3,
        numFlags: 9,
        useRandomFlags: false
      },
      servers: {}
    })
  })

  describe('init 消息格式 (与 frontend startGame() 一致)', () => {
    it('应该发送正确格式的 init 消息给 L 队', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const walls = [
            { x: 0, y: 0, tileId: 45 },
            { x: 19, y: 0, tileId: 47 },
            { x: 0, y: 19, tileId: 69 },
            { x: 19, y: 19, tileId: 71 }
          ]
          const obstacles1 = [{ x: 5, y: 5 }]
          const obstacles2 = [{ x: 10, y: 10 }]
          const lteamPrison = [{ x: 2, y: 17 }]
          const lteamTarget = [{ x: 2, y: 10 }]
          const rteamPrison = [{ x: 17, y: 17 }]
          const rteamTarget = [{ x: 17, y: 10 }]

          manager.sendGameInit({
            mapWidth: 20,
            mapHeight: 20,
            walls,
            obstacles1,
            obstacles2,
            lteamPrison,
            lteamTarget,
            rteamPrison,
            rteamTarget
          })

          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          // 验证 payload 格式与 frontend 一致
          expect(payload).toBeDefined()
          expect(payload.action).toBe('init')
          expect(payload.myteamName).toBe('L')
          expect(payload.numPlayers).toBe(3)
          expect(payload.numFlags).toBe(9)

          // 验证 map 格式
          expect(payload.map).toBeDefined()
          expect(payload.map.width).toBe(20)
          expect(payload.map.height).toBe(20)
          expect(Array.isArray(payload.map.walls)).toBe(true)
          expect(Array.isArray(payload.map.obstacles)).toBe(true)

          // 验证 walls 格式（只包含 x, y，不包含 tileId）
          expect(payload.map.walls[0]).toEqual({ x: 0, y: 0 })
          expect(payload.map.walls[0].tileId).toBeUndefined()

          // 验证 obstacles 格式（包含 obstacles1 + obstacles2 + obstacles2 的 y+1）
          // frontend: obstacles1.concat(obstacles2).concat(obstacles2.map(w => {return {"x": w.x, "y": w.y + 1}}))
          expect(payload.map.obstacles.length).toBe(obstacles1.length + obstacles2.length * 2)
          expect(payload.map.obstacles).toContainEqual({ x: 5, y: 5 })
          expect(payload.map.obstacles).toContainEqual({ x: 10, y: 10 })
          expect(payload.map.obstacles).toContainEqual({ x: 10, y: 11 })

          // 验证队伍相关字段
          expect(Array.isArray(payload.myteamPrison)).toBe(true)
          expect(Array.isArray(payload.myteamTarget)).toBe(true)
          expect(Array.isArray(payload.opponentPrison)).toBe(true)
          expect(Array.isArray(payload.opponentTarget)).toBe(true)
          expect(payload.myteamPrison).toEqual(lteamPrison)
          expect(payload.myteamTarget).toEqual(lteamTarget)
          expect(payload.opponentPrison).toEqual(rteamPrison)
          expect(payload.opponentTarget).toEqual(rteamTarget)

          resolve()
        }, 100)
      })
    })

    it('应该发送正确格式的 init 消息给 R 队', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('R', 'ws://localhost:8081')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          manager.sendGameInit({
            mapWidth: 20,
            mapHeight: 20,
            walls: [{ x: 0, y: 0, tileId: 45 }],
            obstacles1: [{ x: 5, y: 5 }],
            obstacles2: [{ x: 10, y: 10 }],
            lteamPrison: [{ x: 2, y: 17 }],
            lteamTarget: [{ x: 2, y: 10 }],
            rteamPrison: [{ x: 17, y: 17 }],
            rteamTarget: [{ x: 17, y: 10 }]
          })

          const mockSocket = (manager as any).sockets.get('R')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          expect(payload).toBeDefined()
          expect(payload.action).toBe('init')
          expect(payload.myteamName).toBe('R')
          expect(payload.myteamPrison).toEqual([{ x: 17, y: 17 }])
          expect(payload.myteamTarget).toEqual([{ x: 17, y: 10 }])
          expect(payload.opponentPrison).toEqual([{ x: 2, y: 17 }])
          expect(payload.opponentTarget).toEqual([{ x: 2, y: 10 }])

          resolve()
        }, 100)
      })
    })
  })

  describe('status 消息格式 (与 frontend update() 一致)', () => {
    it('应该发送正确格式的 status 消息给 L 队', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const lteamPlayerStatus: PlayerStatus[] = [
            {
              name: 'L0',
              team: 'L',
              posX: 2,
              posY: 1,
              hasFlag: false,
              inPrison: false,
              inPrisonTimeLeft: 0,
              inPrisonDuration: 20000
            }
          ]
          const lteamFlagStatus: FlagStatus[] = [
            { canPickup: true, posX: 3, posY: 2 }
          ]
          const rteamPlayerStatus: PlayerStatus[] = [
            {
              name: 'R0',
              team: 'R',
              posX: 18,
              posY: 1,
              hasFlag: false,
              inPrison: false,
              inPrisonTimeLeft: 0,
              inPrisonDuration: 20000
            }
          ]
          const rteamFlagStatus: FlagStatus[] = [
            { canPickup: true, posX: 17, posY: 2 }
          ]

          manager.sendGameStatus({
            time: 1000,
            lteamPlayerStatus,
            lteamFlagStatus,
            rteamPlayerStatus,
            rteamFlagStatus
          })

          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          // 验证 payload 格式与 frontend 一致
          expect(payload).toBeDefined()
          expect(payload.action).toBe('status')
          expect(payload.time).toBe(1000)
          expect(Array.isArray(payload.myteamPlayer)).toBe(true)
          expect(Array.isArray(payload.myteamFlag)).toBe(true)
          expect(Array.isArray(payload.opponentPlayer)).toBe(true)
          expect(Array.isArray(payload.opponentFlag)).toBe(true)
          expect(typeof payload.myteamScore).toBe('number')
          expect(typeof payload.opponentScore).toBe('number')

          // 验证 L 队的视角
          expect(payload.myteamPlayer).toEqual(lteamPlayerStatus)
          expect(payload.myteamFlag).toEqual(lteamFlagStatus)
          expect(payload.opponentPlayer).toEqual(rteamPlayerStatus)
          expect(payload.opponentFlag).toEqual(rteamFlagStatus)

          resolve()
        }, 100)
      })
    })

    it('应该发送正确格式的 status 消息给 R 队', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('R', 'ws://localhost:8081')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const lteamPlayerStatus: PlayerStatus[] = [
            {
              name: 'L0',
              team: 'L',
              posX: 2,
              posY: 1,
              hasFlag: false,
              inPrison: false,
              inPrisonTimeLeft: 0,
              inPrisonDuration: 20000
            }
          ]
          const rteamPlayerStatus: PlayerStatus[] = [
            {
              name: 'R0',
              team: 'R',
              posX: 18,
              posY: 1,
              hasFlag: false,
              inPrison: false,
              inPrisonTimeLeft: 0,
              inPrisonDuration: 20000
            }
          ]

          manager.sendGameStatus({
            time: 2000,
            lteamPlayerStatus,
            lteamFlagStatus: [],
            rteamPlayerStatus,
            rteamFlagStatus: []
          })

          const mockSocket = (manager as any).sockets.get('R')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          expect(payload).toBeDefined()
          expect(payload.action).toBe('status')
          expect(payload.time).toBe(2000)

          // 验证 R 队的视角（myteam 是 R，opponent 是 L）
          expect(payload.myteamPlayer).toEqual(rteamPlayerStatus)
          expect(payload.opponentPlayer).toEqual(lteamPlayerStatus)

          resolve()
        }, 100)
      })
    })
  })

  describe('finished 消息格式 (与 frontend GameOver() 一致)', () => {
    it('应该发送正确格式的 finished 消息给 L 队', async () => {
      const manager = SocketManager.getInstance()
      const gameState = GameStateManager.getInstance()
      gameState.updateLTeamScore(5)
      gameState.updateRTeamScore(3)
      
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          manager.sendGameFinished()

          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          // 验证 payload 格式与 frontend 一致
          expect(payload).toBeDefined()
          expect(payload.action).toBe('finished')
          expect(payload.myteamScore).toBe(5)
          expect(payload.opponentScore).toBe(3)

          resolve()
        }, 100)
      })
    })

    it('应该发送正确格式的 finished 消息给 R 队', async () => {
      const manager = SocketManager.getInstance()
      const gameState = GameStateManager.getInstance()
      gameState.updateLTeamScore(5)
      gameState.updateRTeamScore(3)
      
      manager.connectTeam('R', 'ws://localhost:8081')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          manager.sendGameFinished()

          const mockSocket = (manager as any).sockets.get('R')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          expect(payload).toBeDefined()
          expect(payload.action).toBe('finished')
          expect(payload.myteamScore).toBe(3)
          expect(payload.opponentScore).toBe(5)

          resolve()
        }, 100)
      })
    })
  })

  describe('接收消息格式 (与 frontend updatePlayerInfo() 一致)', () => {
    it('应该正确处理服务器返回的 players 消息格式', async () => {
      const manager = SocketManager.getInstance()
      const actionsListener = vi.fn()
      
      manager.on(SocketEvent.ACTIONS_RECEIVED, actionsListener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟服务器返回格式：{ "players": { "L0": "up", "L1": "down" } }
          // 参考 frontend/src/scenes/Game.js updatePlayerInfo() 方法
          ws.simulateMessage({
            players: {
              'L0': 'up',
              'L1': 'down',
              'L2': 'left'
            }
          })

          setTimeout(() => {
            expect(actionsListener).toHaveBeenCalled()
            const [team, playerActions] = actionsListener.mock.calls[0]
            expect(team).toBe('L')
            expect(playerActions).toBeDefined()
            expect(playerActions.players).toBeDefined()
            expect(playerActions.players['L0']).toBe('up')
            expect(playerActions.players['L1']).toBe('down')
            expect(playerActions.players['L2']).toBe('left')

            resolve()
          }, 50)
        }, 100)
      })
    })

    it('应该正确处理空的 players 对象（不输出日志）', async () => {
      const manager = SocketManager.getInstance()
      const actionsListener = vi.fn()
      const consoleSpy = vi.spyOn(console, 'log')
      
      manager.on(SocketEvent.ACTIONS_RECEIVED, actionsListener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟服务器返回空字典（正常情况）
          // 参考 frontend：空对象不会设置任何动作，也不会输出日志
          ws.simulateMessage({
            players: {}
          })

          setTimeout(() => {
            // 空的 players 对象不应该触发 ACTIONS_RECEIVED 事件
            expect(actionsListener).not.toHaveBeenCalled()
            // 不应该输出关于空对象的日志（这是正常情况）
            expect(consoleSpy).not.toHaveBeenCalledWith(
              expect.stringContaining('收到空的 players 对象')
            )
            consoleSpy.mockRestore()
            resolve()
          }, 50)
        }, 100)
      })
    })

    it('应该正确处理无效的 players 字段', async () => {
      const manager = SocketManager.getInstance()
      const actionsListener = vi.fn()
      const errorListener = vi.fn()
      
      manager.on(SocketEvent.ACTIONS_RECEIVED, actionsListener)
      manager.on(SocketEvent.ERROR, errorListener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟无效的 players 字段（null）
          ws.simulateMessage({
            players: null
          })

          setTimeout(() => {
            // 无效的 players 字段不应该触发 ACTIONS_RECEIVED 事件
            expect(actionsListener).not.toHaveBeenCalled()
            resolve()
          }, 50)
        }, 100)
      })
    })

    it('应该正确处理数组格式的 players（错误格式）', async () => {
      const manager = SocketManager.getInstance()
      const actionsListener = vi.fn()
      
      manager.on(SocketEvent.ACTIONS_RECEIVED, actionsListener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟错误的数组格式
          ws.simulateMessage({
            players: ['L0', 'L1'] // 错误：应该是对象而不是数组
          })

          setTimeout(() => {
            // 数组格式不应该触发 ACTIONS_RECEIVED 事件
            expect(actionsListener).not.toHaveBeenCalled()
            resolve()
          }, 50)
        }, 100)
      })
    })
  })

  describe('PlayerStatus 格式一致性 (与 frontend Player.getStatus() 一致)', () => {
    it('应该发送正确格式的 PlayerStatus', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          // 参考 frontend/src/gameObjects/Player.js getStatus() 方法
          // 返回格式: { name, team, posX, posY, hasFlag, inPrison, inPrisonTimeLeft, inPrisonDuration }
          const playerStatus: PlayerStatus = {
            name: 'L0',
            team: 'L',
            posX: 2,
            posY: 1,
            hasFlag: true,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 20000
          }

          manager.sendGameStatus({
            time: 1000,
            lteamPlayerStatus: [playerStatus],
            lteamFlagStatus: [],
            rteamPlayerStatus: [],
            rteamFlagStatus: []
          })

          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          expect(payload.myteamPlayer[0]).toEqual(playerStatus)
          expect(payload.myteamPlayer[0].name).toBe('L0')
          expect(payload.myteamPlayer[0].team).toBe('L')
          expect(payload.myteamPlayer[0].posX).toBe(2)
          expect(payload.myteamPlayer[0].posY).toBe(1)
          expect(payload.myteamPlayer[0].hasFlag).toBe(true)
          expect(payload.myteamPlayer[0].inPrison).toBe(false)

          resolve()
        }, 100)
      })
    })
  })

  describe('FlagStatus 格式一致性 (与 frontend Flag.getStatus() 一致)', () => {
    it('应该发送正确格式的 FlagStatus', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          // 参考 frontend/src/gameObjects/Flag.js getStatus() 方法
          // 返回格式: { canPickup, posX, posY }
          const flagStatus: FlagStatus = {
            canPickup: true,
            posX: 3,
            posY: 2
          }

          manager.sendGameStatus({
            time: 1000,
            lteamPlayerStatus: [],
            lteamFlagStatus: [flagStatus],
            rteamPlayerStatus: [],
            rteamFlagStatus: []
          })

          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket
          const payload = ws?.getLastSentMessage()

          expect(payload.myteamFlag[0]).toEqual(flagStatus)
          expect(payload.myteamFlag[0].canPickup).toBe(true)
          expect(payload.myteamFlag[0].posX).toBe(3)
          expect(payload.myteamFlag[0].posY).toBe(2)

          resolve()
        }, 100)
      })
    })
  })

  describe('WebSocket 缓冲区检查 (与 frontend 一致)', () => {
    it('应该在缓冲区满时跳过发送', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟缓冲区满（> 1MB）
          ws.bufferedAmount = 1024 * 1024 + 1

          const initialMessageCount = ws.getSentMessages().length
          manager.sendGameStatus({
            time: 1000,
            lteamPlayerStatus: [],
            lteamFlagStatus: [],
            rteamPlayerStatus: [],
            rteamFlagStatus: []
          })

          // 消息不应该被发送
          expect(ws.getSentMessages().length).toBe(initialMessageCount)

          resolve()
        }, 100)
      })
    })

    it('应该在缓冲区未满时正常发送', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mockSocket = (manager as any).sockets.get('L')
          const ws = mockSocket?.ws as MockWebSocket

          // 模拟缓冲区未满（< 1MB）
          ws.bufferedAmount = 1024 * 1024 - 1

          manager.sendGameStatus({
            time: 1000,
            lteamPlayerStatus: [],
            lteamFlagStatus: [],
            rteamPlayerStatus: [],
            rteamFlagStatus: []
          })

          // 消息应该被发送
          expect(ws.getSentMessages().length).toBeGreaterThan(0)

          resolve()
        }, 100)
      })
    })
  })
})

