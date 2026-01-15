import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { WorldManager } from '../WorldManager'
import type { Team, GameConfig } from '@/types'

// Mock Phaser Math.RND before importing WorldManager
vi.mock('phaser', () => {
  const mockRND = {
    integerInRange: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
    pick: <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)]
  }
  return {
    default: {
      Math: {
        RND: mockRND
      }
    },
    Math: {
      RND: mockRND
    }
  }
})

// Mock Player and Flag classes
vi.mock('../../objects/Player', () => ({
  Player: class MockPlayer {
    constructor() {}
  }
}))

vi.mock('../../objects/Flag', () => ({
  Flag: class MockFlag {
    constructor() {}
  }
}))

// Mock Phaser Game
const createMockGame = () => {
  const registryData: Record<string, any> = {}
  return {
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
}

describe('WorldManager', () => {
  beforeEach(() => {
    // 重置单例实例（通过反射访问私有属性）
    const manager = WorldManager as any
    manager.instance = null
    // 清除所有 mock
    vi.clearAllMocks()
  })

  describe('单例模式', () => {
    it('应该返回同一个实例', () => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
      const instance1 = WorldManager.getInstance()
      const instance2 = WorldManager.getInstance()
      expect(instance1).toBe(instance2)
    })
  })

  describe('初始化', () => {
    it('应该正确初始化游戏状态', () => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
      const manager = WorldManager.getInstance()
      const state = manager.getState()

      expect(state.gameStarted).toBe(false)
      expect(state.gamePaused).toBe(false)
      expect(state.gameOver).toBe(false)
      expect(state.winner).toBeNull()
      expect(state.lTeamScore).toBe(0)
      expect(state.rTeamScore).toBe(0)
    })
  })

  describe('游戏流程控制', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
    })

    it('应该能够开始游戏', () => {
      const manager = WorldManager.getInstance()
      manager.api.startGame()
      const state = manager.getState()
      expect(state.gameStarted).toBe(true)
    })

    it('应该能够暂停游戏', () => {
      const manager = WorldManager.getInstance()
      manager.api.startGame()
      manager.api.pauseGame()
      const state = manager.getState()
      expect(state.gamePaused).toBe(true)
    })

    it('应该能够恢复游戏', () => {
      const manager = WorldManager.getInstance()
      manager.api.startGame()
      manager.api.pauseGame() // 暂停
      manager.api.pauseGame() // 再次调用 pauseGame 恢复
      const state = manager.getState()
      expect(state.gamePaused).toBe(false)
    })

    it('应该能够结束游戏', () => {
      const manager = WorldManager.getInstance()
      manager.api.startGame()
      manager.api.endGame('L')
      const state = manager.getState()
      expect(state.gameOver).toBe(true)
      expect(state.winner).toBe('L')
      expect(state.gameStarted).toBe(false)
    })
  })

  describe('分数管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
    })

    it('应该能够更新 L 队分数', () => {
      const manager = WorldManager.getInstance()
      manager.api.updateLTeamScore(5)
      const state = manager.getState()
      expect(state.lTeamScore).toBe(5)
      expect(state.lTeamState.score).toBe(5)
    })

    it('应该能够更新 R 队分数', () => {
      const manager = WorldManager.getInstance()
      manager.api.updateRTeamScore(3)
      const state = manager.getState()
      expect(state.rTeamScore).toBe(3)
      expect(state.rTeamState.score).toBe(3)
    })
  })

  describe('团队状态管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
    })

    it('应该能够设置 L 队状态', () => {
      const manager = WorldManager.getInstance()
      const newState = {
        score: 10,
        flags: [{ x: 1, y: 1 }],
        players: [{ x: 2, y: 2, name: 'L0' }],
        target: [{ x: 3, y: 3 }],
        prison: [{ x: 4, y: 4 }],
        playerSpriteChoice: 1
      }
      manager.api.setLTeamState(newState)
      const state = manager.getState()
      expect(state.lTeamState.score).toBe(10)
      expect(state.lTeamState.flags).toEqual([{ x: 1, y: 1 }])
    })

    it('应该能够设置 R 队状态', () => {
      const manager = WorldManager.getInstance()
      const newState = {
        score: 5,
        flags: [{ x: 10, y: 10 }],
        players: [{ x: 11, y: 11, name: 'R0' }],
        target: [{ x: 12, y: 12 }],
        prison: [{ x: 13, y: 13 }],
        playerSpriteChoice: 4
      }
      manager.api.setRTeamState(newState)
      const state = manager.getState()
      expect(state.rTeamState.score).toBe(5)
      expect(state.rTeamState.flags).toEqual([{ x: 10, y: 10 }])
    })
  })

  describe('配置管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
      // Mock fetch
      global.fetch = vi.fn()
    })

    afterEach(() => {
      vi.restoreAllMocks()
    })

    it('应该能够设置游戏配置', () => {
      const manager = WorldManager.getInstance()
      const config: GameConfig = {
        teams: [
          { name: 'L', who: 'user1' },
          { name: 'R', who: 'user2' }
        ],
        setup: {
          numPlayers: 3,
          numFlags: 5,
          useRandomFlags: true
        },
        servers: {
          user1: 'ws://localhost:8080',
          user2: 'ws://localhost:8081'
        }
      }
      manager.api.setConfig(config)
      const state = manager.getState()
      expect(state.config).toEqual(config)
      expect(state.numPlayers).toBe(3)
      expect(state.numFlags).toBe(5)
      expect(state.useRandomFlags).toBe(true)
    })

    it('应该能够获取游戏配置', () => {
      const manager = WorldManager.getInstance()
      const config: GameConfig = {
        teams: [
          { name: 'L', who: 'user1' },
          { name: 'R', who: 'user2' }
        ],
        setup: {
          numPlayers: 3,
          numFlags: 5,
          useRandomFlags: true
        },
        servers: {
          user1: 'ws://localhost:8080',
          user2: 'ws://localhost:8081'
        }
      }
      manager.api.setConfig(config)
      const retrievedConfig = manager.api.getConfig()
      expect(retrievedConfig).toEqual(config)
    })

    it('应该能够加载游戏配置（成功）', async () => {
      const manager = WorldManager.getInstance()
      const mockConfig: GameConfig = {
        teams: [
          { name: 'L', who: 'user1' },
          { name: 'R', who: 'user2' }
        ],
        setup: {
          numPlayers: 3,
          numFlags: 5,
          useRandomFlags: true,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {
          user1: 'ws://localhost:8080',
          user2: 'ws://localhost:8081'
        }
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify(mockConfig)
      })

      const config = await manager.api.loadConfig('game_config.json')
      expect(config).toEqual(mockConfig)
      expect(manager.api.getConfig()).toEqual(mockConfig)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })

    it('应该能够加载游戏配置（失败时使用默认配置）', async () => {
      const manager = WorldManager.getInstance()

      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const config = await manager.api.loadConfig('game_config.json')
      expect(config.setup.numPlayers).toBe(3)
      expect(config.setup.numFlags).toBe(9)
      expect(config.setup.useRandomFlags).toBe(true)
      expect(manager.api.getConfig()).toEqual(config)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })

    it('应该能够加载游戏配置（HTTP 错误时使用默认配置）', async () => {
      const manager = WorldManager.getInstance()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      })

      const config = await manager.api.loadConfig('game_config.json')
      expect(config.setup.numPlayers).toBe(3)
      expect(config.setup.numFlags).toBe(9)
      expect(manager.api.getConfig()).toEqual(config)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })
  })

  describe('WebSocket 连接状态', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
    })

    it('应该能够设置 L 队连接状态', () => {
      const manager = WorldManager.getInstance()
      manager.api.setLTeamConnection(true, 'user1')
      const state = manager.getState()
      expect(state.lTeamConnected).toBe(true)
      expect(state.lTeamWho).toBe('user1')
    })

    it('应该能够设置 R 队连接状态', () => {
      const manager = WorldManager.getInstance()
      manager.api.setRTeamConnection(true, 'user2')
      const state = manager.getState()
      expect(state.rTeamConnected).toBe(true)
      expect(state.rTeamWho).toBe('user2')
    })
  })

  describe('队伍初始化', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      WorldManager.initialize(mockGame)
    })

    it('应该能够初始化队伍并存储游戏对象组', () => {
      const manager = WorldManager.getInstance()
      
      // 设置配置
      manager.api.setConfig({
        teams: [],
        setup: {
          numPlayers: 2,
          numFlags: 2,
          useRandomFlags: false,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {}
      })

      // 生成团队状态
      const mapManager = {
        getMapParams: () => ({
          mapX: 100,
          mapY: 100,
          tileSize: 32
        })
      }
      manager.api.generateTeamStates(
        { obstacles1: [], obstacles2: [] },
        mapManager as any
      )

      // Mock Phaser Scene
      const mockGroup = {
        add: vi.fn(),
        getChildren: vi.fn(() => [])
      }
      const mockScene = {
        add: {
          group: vi.fn(() => mockGroup),
          zone: vi.fn(() => ({
            x: 0,
            y: 0,
            width: 96,
            height: 96
          }))
        }
      } as unknown as Phaser.Scene

      // Mock PhysicsManager
      const mockPhysicsManager = {
        addPhysicsBody: vi.fn()
      }

      // 初始化队伍（禁用键盘输入以简化测试）
      const result = manager.api.initTeams(manager, mockScene, mapManager as any, mockPhysicsManager, false)

      // 验证返回的游戏对象组
      expect(result.lteamFlags).toBeDefined()
      expect(result.rteamFlags).toBeDefined()
      expect(result.lteamPlayers).toBeDefined()
      expect(result.rteamPlayers).toBeDefined()
      expect(result.lteamTargetZone).toBeDefined()
      expect(result.rteamTargetZone).toBeDefined()
      expect(result.lteamPrisonZone).toBeDefined()
      expect(result.rteamPrisonZone).toBeDefined()

      // 验证存储的游戏对象组
      expect(manager.api.getLTeamFlags()).toBe(result.lteamFlags)
      expect(manager.api.getRTeamFlags()).toBe(result.rteamFlags)
      expect(manager.api.getLTeamPlayers()).toBe(result.lteamPlayers)
      expect(manager.api.getRTeamPlayers()).toBe(result.rteamPlayers)
    })

    it('应该能够获取游戏对象组（未初始化时返回 null）', () => {
      const manager = WorldManager.getInstance()
      
      expect(manager.api.getLTeamFlags()).toBeNull()
      expect(manager.api.getRTeamFlags()).toBeNull()
      expect(manager.api.getLTeamPlayers()).toBeNull()
      expect(manager.api.getRTeamPlayers()).toBeNull()
    })
  })
})

