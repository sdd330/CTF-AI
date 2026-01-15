/**
 * Payload 格式测试
 * 确保发送给后端的数据格式正确
 */
import { describe, it, expect } from 'vitest'
import type { GameInitPayload, GameStatusPayload, PlayerStatus, FlagStatus, Position } from '@/types'

/**
 * 创建 3x3 网格位置 (与 fejs 和 TeamStateGenerator 中的实现一致)
 */
function create3x3grid(x: number, y: number): Position[] {
  return [
    { x: x - 1, y: y - 1 }, { x: x, y: y - 1 }, { x: x + 1, y: y - 1 },
    { x: x - 1, y: y }, { x: x, y: y }, { x: x + 1, y: y },
    { x: x - 1, y: y + 1 }, { x: x, y: y + 1 }, { x: x + 1, y: y + 1 }
  ]
}

describe('Payload 格式验证', () => {
  describe('GameInitPayload 格式', () => {
    it('prison 和 target 必须是数组格式', () => {
      const payload: GameInitPayload = {
        action: 'init',
        map: {
          width: 20,
          height: 20,
          walls: [{ x: 0, y: 0 }],
          obstacles: [{ x: 5, y: 5 }]
        },
        numPlayers: 3,
        numFlags: 9,
        myteamName: 'L',
        myteamPrison: create3x3grid(2, 17),
        myteamTarget: create3x3grid(2, 10),
        opponentPrison: create3x3grid(17, 17),
        opponentTarget: create3x3grid(17, 10)
      }

      // 验证 prison 和 target 是数组
      expect(Array.isArray(payload.myteamPrison)).toBe(true)
      expect(Array.isArray(payload.myteamTarget)).toBe(true)
      expect(Array.isArray(payload.opponentPrison)).toBe(true)
      expect(Array.isArray(payload.opponentTarget)).toBe(true)
      
      // 验证可以序列化为 JSON
      const jsonString = JSON.stringify(payload)
      const parsed = JSON.parse(jsonString)
      
      expect(Array.isArray(parsed.myteamPrison)).toBe(true)
      expect(Array.isArray(parsed.myteamTarget)).toBe(true)
    })

    it('prison 和 target 必须是长度为 9 的数组', () => {
      const lPrison = create3x3grid(2, 17)
      const lTarget = create3x3grid(2, 10)

      expect(lPrison).toHaveLength(9)
      expect(lTarget).toHaveLength(9)
    })

    it('每个位置都有 x 和 y 属性', () => {
      const prison = create3x3grid(2, 17)

      prison.forEach(pos => {
        expect(pos).toHaveProperty('x')
        expect(pos).toHaveProperty('y')
        expect(typeof pos.x).toBe('number')
        expect(typeof pos.y).toBe('number')
      })
    })

    it('prison 和 target 应该形成 3x3 网格', () => {
      const prison = create3x3grid(2, 17)

      // 检查是否是 3x3 网格
      const xCoords = new Set(prison.map(p => p.x))
      const yCoords = new Set(prison.map(p => p.y))

      expect(xCoords.size).toBe(3)
      expect(yCoords.size).toBe(3)

      // 验证是连续的坐标
      const xArray = Array.from(xCoords).sort((a, b) => a - b)
      const yArray = Array.from(yCoords).sort((a, b) => a - b)

      expect(xArray[1] - xArray[0]).toBe(1)
      expect(xArray[2] - xArray[1]).toBe(1)
      expect(yArray[1] - yArray[0]).toBe(1)
      expect(yArray[2] - yArray[1]).toBe(1)
    })

    it('3x3 网格应该以中心点为基准', () => {
      const centerX = 10
      const centerY = 15
      const grid = create3x3grid(centerX, centerY)

      // 验证中心点在网格中
      expect(grid).toContainEqual({ x: centerX, y: centerY })

      // 验证所有 9 个位置
      expect(grid).toContainEqual({ x: centerX - 1, y: centerY - 1 })
      expect(grid).toContainEqual({ x: centerX, y: centerY - 1 })
      expect(grid).toContainEqual({ x: centerX + 1, y: centerY - 1 })
      expect(grid).toContainEqual({ x: centerX - 1, y: centerY })
      expect(grid).toContainEqual({ x: centerX, y: centerY })
      expect(grid).toContainEqual({ x: centerX + 1, y: centerY })
      expect(grid).toContainEqual({ x: centerX - 1, y: centerY + 1 })
      expect(grid).toContainEqual({ x: centerX, y: centerY + 1 })
      expect(grid).toContainEqual({ x: centerX + 1, y: centerY + 1 })
    })

    it('完整的 GameInitPayload 应该可以序列化和反序列化', () => {
      const payload: GameInitPayload = {
        action: 'init',
        map: {
          width: 20,
          height: 20,
          walls: [{ x: 0, y: 0 }, { x: 19, y: 0 }],
          obstacles: [{ x: 5, y: 5 }, { x: 10, y: 10 }]
        },
        numPlayers: 3,
        numFlags: 9,
        myteamName: 'L',
        myteamPrison: create3x3grid(2, 17),
        myteamTarget: create3x3grid(2, 10),
        opponentPrison: create3x3grid(17, 17),
        opponentTarget: create3x3grid(17, 10)
      }

      // 序列化
      const jsonString = JSON.stringify(payload)
      
      // 反序列化
      const parsed: GameInitPayload = JSON.parse(jsonString)

      // 验证所有字段
      expect(parsed.action).toBe('init')
      expect(parsed.myteamName).toBe('L')
      expect(parsed.numPlayers).toBe(3)
      expect(parsed.numFlags).toBe(9)
      
      // 验证 map
      expect(parsed.map.width).toBe(20)
      expect(parsed.map.height).toBe(20)
      expect(parsed.map.walls).toHaveLength(2)
      expect(parsed.map.obstacles).toHaveLength(2)
      
      // 验证 prison 和 target
      expect(parsed.myteamPrison).toHaveLength(9)
      expect(parsed.myteamTarget).toHaveLength(9)
      expect(parsed.opponentPrison).toHaveLength(9)
      expect(parsed.opponentTarget).toHaveLength(9)
    })

    it('后端期望的格式：myteamPrison 和 myteamTarget 为数组', () => {
      // 这是后端 backend/lib/map_service/map.py 期望的格式
      const payload: GameInitPayload = {
        action: 'init',
        map: {
          width: 40,
          height: 20,
          walls: [],
          obstacles: []
        },
        numPlayers: 2,
        numFlags: 1,
        myteamName: 'L',
        myteamPrison: [
          { x: 1, y: 16 }, { x: 2, y: 16 }, { x: 3, y: 16 },
          { x: 1, y: 17 }, { x: 2, y: 17 }, { x: 3, y: 17 },
          { x: 1, y: 18 }, { x: 2, y: 18 }, { x: 3, y: 18 }
        ],
        myteamTarget: [
          { x: 1, y: 9 }, { x: 2, y: 9 }, { x: 3, y: 9 },
          { x: 1, y: 10 }, { x: 2, y: 10 }, { x: 3, y: 10 },
          { x: 1, y: 11 }, { x: 2, y: 11 }, { x: 3, y: 11 }
        ],
        opponentPrison: [
          { x: 36, y: 16 }, { x: 37, y: 16 }, { x: 38, y: 16 },
          { x: 36, y: 17 }, { x: 37, y: 17 }, { x: 38, y: 17 },
          { x: 36, y: 18 }, { x: 37, y: 18 }, { x: 38, y: 18 }
        ],
        opponentTarget: [
          { x: 36, y: 9 }, { x: 37, y: 9 }, { x: 38, y: 9 },
          { x: 36, y: 10 }, { x: 37, y: 10 }, { x: 38, y: 10 },
          { x: 36, y: 11 }, { x: 37, y: 11 }, { x: 38, y: 11 }
        ]
      }

      // 验证格式
      expect(Array.isArray(payload.myteamPrison)).toBe(true)
      expect(Array.isArray(payload.myteamTarget)).toBe(true)
      
      // 后端会这样访问：
      // for t in my_target:
      //     Position(t["x"], t["y"])
      payload.myteamTarget.forEach(t => {
        expect(t['x']).toBeDefined()
        expect(t['y']).toBeDefined()
        expect(typeof t['x']).toBe('number')
        expect(typeof t['y']).toBe('number')
      })

      payload.myteamPrison.forEach(t => {
        expect(t['x']).toBeDefined()
        expect(t['y']).toBeDefined()
        expect(typeof t['x']).toBe('number')
        expect(typeof t['y']).toBe('number')
      })
    })
  })

  describe('GameStatusPayload 格式', () => {
    it('PlayerStatus 必须包含所有必需字段', () => {
      const playerStatus: PlayerStatus = {
        name: 'L0',
        team: 'L',
        posX: 5,
        posY: 10,
        hasFlag: false,
        inPrison: false,
        inPrisonTimeLeft: 0,
        inPrisonDuration: 0
      }

      // 验证所有字段存在
      expect(playerStatus).toHaveProperty('name')
      expect(playerStatus).toHaveProperty('team')
      expect(playerStatus).toHaveProperty('posX')
      expect(playerStatus).toHaveProperty('posY')
      expect(playerStatus).toHaveProperty('hasFlag')
      expect(playerStatus).toHaveProperty('inPrison')
      expect(playerStatus).toHaveProperty('inPrisonTimeLeft')
      expect(playerStatus).toHaveProperty('inPrisonDuration')

      // 验证类型
      expect(typeof playerStatus.name).toBe('string')
      expect(typeof playerStatus.team).toBe('string')
      expect(typeof playerStatus.posX).toBe('number')
      expect(typeof playerStatus.posY).toBe('number')
      expect(typeof playerStatus.hasFlag).toBe('boolean')
      expect(typeof playerStatus.inPrison).toBe('boolean')
      expect(typeof playerStatus.inPrisonTimeLeft).toBe('number')
      expect(typeof playerStatus.inPrisonDuration).toBe('number')
    })

    it('FlagStatus 必须包含所有必需字段', () => {
      const flagStatus: FlagStatus = {
        canPickup: true,
        posX: 3,
        posY: 5
      }

      // 验证所有字段存在
      expect(flagStatus).toHaveProperty('canPickup')
      expect(flagStatus).toHaveProperty('posX')
      expect(flagStatus).toHaveProperty('posY')

      // 验证类型
      expect(typeof flagStatus.canPickup).toBe('boolean')
      expect(typeof flagStatus.posX).toBe('number')
      expect(typeof flagStatus.posY).toBe('number')
    })

    it('GameStatusPayload 必须包含所有必需字段', () => {
      const payload: GameStatusPayload = {
        action: 'status',
        time: 5000,
        myteamName: 'L',
        myteamPlayer: [
          {
            name: 'L0',
            team: 'L',
            posX: 2,
            posY: 1,
            hasFlag: false,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          },
          {
            name: 'L1',
            team: 'L',
            posX: 2,
            posY: 2,
            hasFlag: true,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          }
        ],
        myteamFlag: [
          { canPickup: true, posX: 1, posY: 1 },
          { canPickup: false, posX: 1, posY: 2 }
        ],
        myteamScore: 2,
        opponentPlayer: [
          {
            name: 'R0',
            team: 'R',
            posX: 37,
            posY: 1,
            hasFlag: false,
            inPrison: true,
            inPrisonTimeLeft: 3.5,
            inPrisonDuration: 5
          }
        ],
        opponentFlag: [
          { canPickup: true, posX: 38, posY: 1 }
        ],
        opponentScore: 1
      }

      // 验证所有字段存在
      expect(payload).toHaveProperty('action')
      expect(payload).toHaveProperty('time')
      expect(payload).toHaveProperty('myteamName')
      expect(payload).toHaveProperty('myteamPlayer')
      expect(payload).toHaveProperty('myteamFlag')
      expect(payload).toHaveProperty('myteamScore')
      expect(payload).toHaveProperty('opponentPlayer')
      expect(payload).toHaveProperty('opponentFlag')
      expect(payload).toHaveProperty('opponentScore')

      // 验证类型
      expect(payload.action).toBe('status')
      expect(typeof payload.time).toBe('number')
      expect(typeof payload.myteamName).toBe('string')
      expect(Array.isArray(payload.myteamPlayer)).toBe(true)
      expect(Array.isArray(payload.myteamFlag)).toBe(true)
      expect(typeof payload.myteamScore).toBe('number')
      expect(Array.isArray(payload.opponentPlayer)).toBe(true)
      expect(Array.isArray(payload.opponentFlag)).toBe(true)
      expect(typeof payload.opponentScore).toBe('number')
    })

    it('myteamPlayer 和 opponentPlayer 必须是数组', () => {
      const payload: GameStatusPayload = {
        action: 'status',
        time: 0,
        myteamName: 'L',
        myteamPlayer: [],
        myteamFlag: [],
        myteamScore: 0,
        opponentPlayer: [],
        opponentFlag: [],
        opponentScore: 0
      }

      expect(Array.isArray(payload.myteamPlayer)).toBe(true)
      expect(Array.isArray(payload.opponentPlayer)).toBe(true)
    })

    it('myteamFlag 和 opponentFlag 必须是数组', () => {
      const payload: GameStatusPayload = {
        action: 'status',
        time: 0,
        myteamName: 'L',
        myteamPlayer: [],
        myteamFlag: [],
        myteamScore: 0,
        opponentPlayer: [],
        opponentFlag: [],
        opponentScore: 0
      }

      expect(Array.isArray(payload.myteamFlag)).toBe(true)
      expect(Array.isArray(payload.opponentFlag)).toBe(true)
    })

    it('完整的 GameStatusPayload 应该可以序列化和反序列化', () => {
      const payload: GameStatusPayload = {
        action: 'status',
        time: 12345,
        myteamName: 'R',
        myteamPlayer: [
          {
            name: 'R0',
            team: 'R',
            posX: 37,
            posY: 1,
            hasFlag: false,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          },
          {
            name: 'R1',
            team: 'R',
            posX: 37,
            posY: 2,
            hasFlag: true,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          },
          {
            name: 'R2',
            team: 'R',
            posX: 38,
            posY: 17,
            hasFlag: false,
            inPrison: true,
            inPrisonTimeLeft: 2.5,
            inPrisonDuration: 5
          }
        ],
        myteamFlag: [
          { canPickup: true, posX: 38, posY: 1 },
          { canPickup: true, posX: 38, posY: 2 },
          { canPickup: false, posX: 15, posY: 10 }
        ],
        myteamScore: 3,
        opponentPlayer: [
          {
            name: 'L0',
            team: 'L',
            posX: 2,
            posY: 1,
            hasFlag: false,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          }
        ],
        opponentFlag: [
          { canPickup: true, posX: 1, posY: 1 }
        ],
        opponentScore: 1
      }

      // 序列化
      const jsonString = JSON.stringify(payload)

      // 反序列化
      const parsed: GameStatusPayload = JSON.parse(jsonString)

      // 验证所有字段
      expect(parsed.action).toBe('status')
      expect(parsed.time).toBe(12345)
      expect(parsed.myteamName).toBe('R')
      expect(parsed.myteamScore).toBe(3)
      expect(parsed.opponentScore).toBe(1)

      // 验证数组
      expect(parsed.myteamPlayer).toHaveLength(3)
      expect(parsed.myteamFlag).toHaveLength(3)
      expect(parsed.opponentPlayer).toHaveLength(1)
      expect(parsed.opponentFlag).toHaveLength(1)

      // 验证 PlayerStatus 字段
      expect(parsed.myteamPlayer[0].name).toBe('R0')
      expect(parsed.myteamPlayer[0].team).toBe('R')
      expect(parsed.myteamPlayer[0].posX).toBe(37)
      expect(parsed.myteamPlayer[0].posY).toBe(1)
      expect(parsed.myteamPlayer[0].hasFlag).toBe(false)
      expect(parsed.myteamPlayer[0].inPrison).toBe(false)

      // 验证监狱中的玩家
      expect(parsed.myteamPlayer[2].inPrison).toBe(true)
      expect(parsed.myteamPlayer[2].inPrisonTimeLeft).toBe(2.5)
      expect(parsed.myteamPlayer[2].inPrisonDuration).toBe(5)

      // 验证 FlagStatus 字段
      expect(parsed.myteamFlag[0].canPickup).toBe(true)
      expect(parsed.myteamFlag[0].posX).toBe(38)
      expect(parsed.myteamFlag[0].posY).toBe(1)
    })

    it('后端期望的格式：遍历数组访问字段', () => {
      const payload: GameStatusPayload = {
        action: 'status',
        time: 10000,
        myteamName: 'L',
        myteamPlayer: [
          {
            name: 'L0',
            team: 'L',
            posX: 5,
            posY: 10,
            hasFlag: true,
            inPrison: false,
            inPrisonTimeLeft: 0,
            inPrisonDuration: 0
          }
        ],
        myteamFlag: [
          { canPickup: false, posX: 5, posY: 10 }
        ],
        myteamScore: 1,
        opponentPlayer: [
          {
            name: 'R0',
            team: 'R',
            posX: 35,
            posY: 10,
            hasFlag: false,
            inPrison: true,
            inPrisonTimeLeft: 4.2,
            inPrisonDuration: 5
          }
        ],
        opponentFlag: [
          { canPickup: true, posX: 38, posY: 3 }
        ],
        opponentScore: 0
      }

      // 后端会这样访问 PlayerStatus
      payload.myteamPlayer.forEach(player => {
        expect(player['name']).toBeDefined()
        expect(player['team']).toBeDefined()
        expect(player['posX']).toBeDefined()
        expect(player['posY']).toBeDefined()
        expect(player['hasFlag']).toBeDefined()
        expect(player['inPrison']).toBeDefined()
        expect(player['inPrisonTimeLeft']).toBeDefined()
        expect(player['inPrisonDuration']).toBeDefined()
      })

      // 后端会这样访问 FlagStatus
      payload.myteamFlag.forEach(flag => {
        expect(flag['canPickup']).toBeDefined()
        expect(flag['posX']).toBeDefined()
        expect(flag['posY']).toBeDefined()
      })
    })

    it('time 应该是相对游戏开始时间的毫秒数', () => {
      // 游戏开始 5 秒后的状态
      const payload: GameStatusPayload = {
        action: 'status',
        time: 5000,
        myteamName: 'L',
        myteamPlayer: [],
        myteamFlag: [],
        myteamScore: 0,
        opponentPlayer: [],
        opponentFlag: [],
        opponentScore: 0
      }

      expect(payload.time).toBeGreaterThanOrEqual(0)
      expect(typeof payload.time).toBe('number')
    })
  })
})
