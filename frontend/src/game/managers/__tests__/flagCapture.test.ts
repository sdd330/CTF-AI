/**
 * 抢旗逻辑测试
 * 模拟游戏场景：1 个玩家 + 1 个旗帜
 * 确保抢旗逻辑正确
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { PhysicsManager, type CollisionCallbacks } from '../PhysicsManager'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { MapManager } from '../MapManager'
import { GameStateManager } from '../GameStateManager'

// Mock Phaser Scene
const createMockScene = () => {
  const mockPhysics = {
    add: {
      existing: vi.fn((sprite: any) => {
        sprite.body = {
          setCollideWorldBounds: vi.fn(),
          setSize: vi.fn(),
          setOffset: vi.fn(),
          x: 0,
          y: 0,
          width: 32,
          height: 32
        }
        return sprite
      }),
      overlap: vi.fn()
    },
    world: {
      bounds: {
        x: 0,
        y: 0,
        width: 960,
        height: 960
      }
    }
  }

  const mockDisplayList = {
    queueDepthSort: vi.fn(),
    add: vi.fn(),
    remove: vi.fn()
  }
  const mockUpdateList = {
    add: vi.fn(),
    remove: vi.fn()
  }

  const mockAnims = {
    on: vi.fn(),
    create: vi.fn(),
    exists: vi.fn(() => false),
    generateFrameNumbers: vi.fn(() => []),
    play: vi.fn(),
    stop: vi.fn()
  }

  const mockTextures = {
    get: vi.fn(() => ({
      get: vi.fn(() => ({
        width: 32,
        height: 32,
        source: []
      }))
    })),
    exists: vi.fn(() => true),
    list: {}
  }

  const mockCache = {
    get: vi.fn(),
    exists: vi.fn(() => true)
  }

  const mockKeys = {
    left: { isDown: false },
    right: { isDown: false },
    up: { isDown: false },
    down: { isDown: false },
    W: { isDown: false },
    A: { isDown: false },
    S: { isDown: false },
    D: { isDown: false }
  }

  return {
    physics: mockPhysics,
    add: {
      existing: vi.fn(),
      group: vi.fn(() => ({
        getChildren: vi.fn(() => []),
        add: vi.fn(),
        remove: vi.fn()
      })),
      zone: vi.fn(() => ({
        x: 0,
        y: 0,
        width: 100,
        height: 100
      }))
    },
    input: {
      keyboard: {
        addKeys: vi.fn(() => mockKeys),
        createCursorKeys: vi.fn(() => mockKeys)
      }
    },
    anims: mockAnims,
    textures: mockTextures,
    cache: mockCache,
    sys: {
      displayList: mockDisplayList,
      updateList: mockUpdateList,
      queueDepthSort: vi.fn(),
      anims: mockAnims,
      textures: mockTextures,
      cache: mockCache
    },
    getMapOffset: () => ({
      x: 100,
      y: 100,
      width: 640,
      height: 640,
      tileSize: 32
    }),
    isWall: () => false,
    removeFlagItem: vi.fn()
  } as unknown as Phaser.Scene
}

describe('抢旗逻辑测试 - 1 玩家 + 1 旗帜', () => {
  let scene: Phaser.Scene
  let manager: PhysicsManager
  let mockMapManager: MapManager
  let lteamPlayers: Phaser.GameObjects.Group
  let rteamPlayers: Phaser.GameObjects.Group
  let lteamFlags: Phaser.GameObjects.Group
  let rteamFlags: Phaser.GameObjects.Group

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
    
    const gsManager = GameStateManager as any
    gsManager.instance = null
    GameStateManager.initialize(mockGame)
    
    const gameState = GameStateManager.getInstance()
    gameState.setConfig({
      teams: [],
      setup: {
        numPlayers: 1,
        numFlags: 1,
        useRandomFlags: false,
        mapWidth: 20,
        mapHeight: 20
      },
      servers: {}
    })
    
    scene = createMockScene()
    mockMapManager = MapManager.getInstance()
    mockMapManager.setMapParams({
      mapWidth: 20,
      mapHeight: 20,
      tileSize: 32,
      centerX: 480,
      centerY: 320,
      mapX: 100,
      mapY: 100
    })
    
    manager = new PhysicsManager(scene)
    
    // 创建游戏对象组
    lteamPlayers = scene.add.group()
    rteamPlayers = scene.add.group()
    lteamFlags = scene.add.group()
    rteamFlags = scene.add.group()
    
    manager.setGameObjects(
      mockMapManager,
      lteamPlayers,
      rteamPlayers,
      lteamFlags,
      rteamFlags
    )
  })

  describe('L 队玩家抢 R 队旗帜', () => {
    it('应该成功收集敌方旗帜', () => {
      // 创建 L 队玩家
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = false
      lPlayer.hasFlag = false
      
      // 创建 R 队旗帜（可拾取）
      const rFlag = new Flag(scene, 5, 5, 'R', true)
      
      // 验证初始状态
      expect(lPlayer.hasFlag).toBe(false)
      expect(rFlag.canPickup).toBe(true)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, rFlag)
      
      // 验证玩家已获得旗帜
      expect(lPlayer.hasFlag).toBe(true)
      
      // 验证旗帜已被收集（应该从场景中移除）
      expect(scene.removeFlagItem).toHaveBeenCalled()
    })

    it('不应该让同队玩家收集同队旗帜', () => {
      // 创建 L 队玩家
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = false
      lPlayer.hasFlag = false
      
      // 创建 L 队旗帜（同队）
      const lFlag = new Flag(scene, 5, 5, 'L', true)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, lFlag)
      
      // 验证玩家未获得旗帜（同队不能收集）
      expect(lPlayer.hasFlag).toBe(false)
    })

    it('不应该让监狱中的玩家收集旗帜', () => {
      // 创建 L 队玩家（在监狱中）
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = true
      lPlayer.hasFlag = false
      
      // 创建 R 队旗帜
      const rFlag = new Flag(scene, 5, 5, 'R', true)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, rFlag)
      
      // 验证玩家未获得旗帜（监狱中的玩家不能收集）
      expect(lPlayer.hasFlag).toBe(false)
    })

    it('不应该让已持有旗帜的玩家收集新旗帜', () => {
      // 创建 L 队玩家（已持有旗帜）
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = false
      lPlayer.hasFlag = true // 已持有旗帜
      
      // 创建 R 队旗帜
      const rFlag = new Flag(scene, 5, 5, 'R', true)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, rFlag)
      
      // 验证玩家仍然只持有一个旗帜（hasFlag 保持为 true）
      expect(lPlayer.hasFlag).toBe(true)
    })

    it('不应该收集不可拾取的旗帜', () => {
      // 创建 L 队玩家
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = false
      lPlayer.hasFlag = false
      
      // 创建 R 队旗帜（不可拾取，已放置在目标区域）
      const rFlag = new Flag(scene, 5, 5, 'R', false)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, rFlag)
      
      // 验证玩家未获得旗帜（不可拾取的旗帜不能收集）
      expect(lPlayer.hasFlag).toBe(false)
    })
  })

  describe('R 队玩家抢 L 队旗帜', () => {
    it('应该成功收集敌方旗帜', () => {
      // 创建 R 队玩家
      const rPlayer = new Player(scene, 'R0', 15, 5, 'R', 4, false)
      rPlayer.inPrison = false
      rPlayer.hasFlag = false
      
      // 创建 L 队旗帜（可拾取）
      const lFlag = new Flag(scene, 15, 5, 'L', true)
      
      // 验证初始状态
      expect(rPlayer.hasFlag).toBe(false)
      expect(lFlag.canPickup).toBe(true)
      
      // 调用 handleFlagCollected
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(rPlayer, lFlag)
      
      // 验证玩家已获得旗帜
      expect(rPlayer.hasFlag).toBe(true)
      
      // 验证旗帜已被收集
      expect(scene.removeFlagItem).toHaveBeenCalled()
    })
  })

  describe('完整抢旗流程', () => {
    it('应该完成完整的抢旗流程：收集 -> 返回 -> 放置', () => {
      // 设置回调来验证分数更新
      const onScoreUpdate = vi.fn()
      const onCreateFlag = vi.fn((scene, x, y, team, canPickup) => {
        return new Flag(scene, x, y, team, canPickup)
      })
      
      manager = new PhysicsManager(scene, { onScoreUpdate, onCreateFlag })
      manager.setGameObjects(
        mockMapManager,
        lteamPlayers,
        rteamPlayers,
        lteamFlags,
        rteamFlags
      )
      
      // 1. 创建 L 队玩家
      const lPlayer = new Player(scene, 'L0', 5, 5, 'L', 1, true)
      lPlayer.inPrison = false
      lPlayer.hasFlag = false
      
      // 2. 创建 R 队旗帜（在 R 队区域）
      const rFlag = new Flag(scene, 15, 5, 'R', true)
      
      // 3. 收集旗帜
      const handleFlagCollected = (manager as any).handleFlagCollected.bind(manager)
      handleFlagCollected(lPlayer, rFlag)
      
      // 验证：玩家已获得旗帜
      expect(lPlayer.hasFlag).toBe(true)
      
      // 4. 模拟玩家返回自己的目标区域
      // 设置 L 队目标区域
      const gameState = GameStateManager.getInstance()
      gameState.generateTargetsAndPrisons(20, 20)
      const teamStates = gameState.getTeamStates()
      
      // 设置 flags 组的方法
      rteamFlags.getChildren = vi.fn(() => [])
      rteamFlags.add = vi.fn()
      
      // 5. 放置旗帜（在目标区域）
      const handleFlagDropped = (manager as any).handleFlagDropped.bind(manager)
      
      // 调用放置旗帜
      handleFlagDropped(lPlayer)
      
      // 验证：玩家已放下旗帜
      expect(lPlayer.hasFlag).toBe(false)
      
      // 验证：分数更新回调被调用
      expect(onScoreUpdate).toHaveBeenCalledWith('L')
      
      // 验证：新旗帜被创建并添加到 R 队旗帜组
      expect(onCreateFlag).toHaveBeenCalled()
      expect(rteamFlags.add).toHaveBeenCalled()
    })
  })
})

