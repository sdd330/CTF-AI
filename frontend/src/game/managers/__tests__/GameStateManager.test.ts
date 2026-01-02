import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { GameStateManager } from '../GameStateManager'
import type { Team, GameConfig } from '@/types'

// Mock Phaser Math.RND before importing GameStateManager
vi.mock('phaser', () => {
  const mockRND = {
    integerInRange: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
    pick: <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)]
  }
  return {
    default: {
      Math: {
        RND: mockRND,
        get RND() {
          return mockRND
        }
      }
    },
    Math: {
      RND: mockRND,
      get RND() {
        return mockRND
      }
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

describe('GameStateManager', () => {
  beforeEach(() => {
    // 重置单例实例（通过反射访问私有属性）
    const manager = GameStateManager as any
    manager.instance = null
    // 清除所有 mock
    vi.clearAllMocks()
  })

  describe('单例模式', () => {
    it('应该返回同一个实例', () => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
      const instance1 = GameStateManager.getInstance()
      const instance2 = GameStateManager.getInstance()
      expect(instance1).toBe(instance2)
    })
  })

  describe('初始化', () => {
    it('应该正确初始化游戏状态', () => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
      const manager = GameStateManager.getInstance()
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
      GameStateManager.initialize(mockGame)
    })

    it('应该能够开始游戏', () => {
      const manager = GameStateManager.getInstance()
      manager.startGame()
      const state = manager.getState()
      expect(state.gameStarted).toBe(true)
    })

    it('应该能够暂停游戏', () => {
      const manager = GameStateManager.getInstance()
      manager.startGame()
      manager.pauseGame()
      const state = manager.getState()
      expect(state.gamePaused).toBe(true)
    })

    it('应该能够恢复游戏', () => {
      const manager = GameStateManager.getInstance()
      manager.startGame()
      manager.pauseGame() // 暂停
      manager.pauseGame() // 再次调用 pauseGame 恢复
      const state = manager.getState()
      expect(state.gamePaused).toBe(false)
    })

    it('应该能够结束游戏', () => {
      const manager = GameStateManager.getInstance()
      manager.startGame()
      manager.endGame('L')
      const state = manager.getState()
      expect(state.gameOver).toBe(true)
      expect(state.winner).toBe('L')
      expect(state.gameStarted).toBe(false)
    })
  })

  describe('分数管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
    })

    it('应该能够更新 L 队分数', () => {
      const manager = GameStateManager.getInstance()
      manager.updateLTeamScore(5)
      const state = manager.getState()
      expect(state.lTeamScore).toBe(5)
      expect(state.lTeamState.score).toBe(5)
    })

    it('应该能够更新 R 队分数', () => {
      const manager = GameStateManager.getInstance()
      manager.updateRTeamScore(3)
      const state = manager.getState()
      expect(state.rTeamScore).toBe(3)
      expect(state.rTeamState.score).toBe(3)
    })
  })

  describe('团队状态管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
    })

    it('应该能够设置 L 队状态', () => {
      const manager = GameStateManager.getInstance()
      const newState = {
        score: 10,
        flags: [{ x: 1, y: 1 }],
        players: [{ x: 2, y: 2, name: 'L0' }],
        target: [{ x: 3, y: 3 }],
        prison: [{ x: 4, y: 4 }],
        playerSpriteChoice: 1
      }
      manager.setLTeamState(newState)
      const state = manager.getState()
      expect(state.lTeamState.score).toBe(10)
      expect(state.lTeamState.flags).toEqual([{ x: 1, y: 1 }])
    })

    it('应该能够设置 R 队状态', () => {
      const manager = GameStateManager.getInstance()
      const newState = {
        score: 5,
        flags: [{ x: 10, y: 10 }],
        players: [{ x: 11, y: 11, name: 'R0' }],
        target: [{ x: 12, y: 12 }],
        prison: [{ x: 13, y: 13 }],
        playerSpriteChoice: 4
      }
      manager.setRTeamState(newState)
      const state = manager.getState()
      expect(state.rTeamState.score).toBe(5)
      expect(state.rTeamState.flags).toEqual([{ x: 10, y: 10 }])
    })
  })

  describe('配置管理', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
      // Mock fetch
      global.fetch = vi.fn()
    })

    afterEach(() => {
      vi.restoreAllMocks()
    })

    it('应该能够设置游戏配置', () => {
      const manager = GameStateManager.getInstance()
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
      manager.setConfig(config)
      const state = manager.getState()
      expect(state.config).toEqual(config)
      expect(state.numPlayers).toBe(3)
      expect(state.numFlags).toBe(5)
      expect(state.useRandomFlags).toBe(true)
    })

    it('应该能够获取游戏配置', () => {
      const manager = GameStateManager.getInstance()
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
      manager.setConfig(config)
      const retrievedConfig = manager.getConfig()
      expect(retrievedConfig).toEqual(config)
    })

    it('应该能够加载游戏配置（成功）', async () => {
      const manager = GameStateManager.getInstance()
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

      const config = await manager.loadConfig('game_config.json')
      expect(config).toEqual(mockConfig)
      expect(manager.getConfig()).toEqual(mockConfig)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })

    it('应该能够加载游戏配置（失败时使用默认配置）', async () => {
      const manager = GameStateManager.getInstance()

      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const config = await manager.loadConfig('game_config.json')
      expect(config.setup.numPlayers).toBe(3)
      expect(config.setup.numFlags).toBe(9)
      expect(config.setup.useRandomFlags).toBe(true)
      expect(manager.getConfig()).toEqual(config)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })

    it('应该能够加载游戏配置（HTTP 错误时使用默认配置）', async () => {
      const manager = GameStateManager.getInstance()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      })

      const config = await manager.loadConfig('game_config.json')
      expect(config.setup.numPlayers).toBe(3)
      expect(config.setup.numFlags).toBe(9)
      expect(manager.getConfig()).toEqual(config)
      const state = manager.getState()
      expect(state.configLoaded).toBe(true)
    })
  })

  describe('WebSocket 连接状态', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
    })

    it('应该能够设置 L 队连接状态', () => {
      const manager = GameStateManager.getInstance()
      manager.setLTeamConnection(true, 'user1')
      const state = manager.getState()
      expect(state.lTeamConnected).toBe(true)
      expect(state.lTeamWho).toBe('user1')
    })

    it('应该能够设置 R 队连接状态', () => {
      const manager = GameStateManager.getInstance()
      manager.setRTeamConnection(true, 'user2')
      const state = manager.getState()
      expect(state.rTeamConnected).toBe(true)
      expect(state.rTeamWho).toBe('user2')
    })
  })

  describe('队伍初始化', () => {
    beforeEach(() => {
      const mockGame = createMockGame()
      GameStateManager.initialize(mockGame)
    })

    it('应该能够初始化队伍并存储游戏对象组', () => {
      const manager = GameStateManager.getInstance()
      
      // 设置配置
      manager.setConfig({
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
      manager.generateTeamStates(
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

      // 初始化队伍
      const result = manager.initTeams(mockScene, mapManager as any, mockPhysicsManager)

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
      expect(manager.getLTeamFlags()).toBe(result.lteamFlags)
      expect(manager.getRTeamFlags()).toBe(result.rteamFlags)
      expect(manager.getLTeamPlayers()).toBe(result.lteamPlayers)
      expect(manager.getRTeamPlayers()).toBe(result.rteamPlayers)
    })

    it('应该能够获取游戏对象组（未初始化时返回 null）', () => {
      const manager = GameStateManager.getInstance()
      
      expect(manager.getLTeamFlags()).toBeNull()
      expect(manager.getRTeamFlags()).toBeNull()
      expect(manager.getLTeamPlayers()).toBeNull()
      expect(manager.getRTeamPlayers()).toBeNull()
    })
  })
})

