import { describe, it, expect, beforeEach, vi } from 'vitest'
import { PhysicsManager, type CollisionCallbacks } from '../PhysicsManager'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { MapManager } from '../MapManager'
import { WorldManager } from '../WorldManager'
import type { Position, Team } from '@/types'

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

  // Mock displayList 和 updateList（Phaser GameObject 需要）
  const mockDisplayList = {
    queueDepthSort: vi.fn(),
    add: vi.fn(),
    remove: vi.fn()
  }
  const mockUpdateList = {
    add: vi.fn(),
    remove: vi.fn()
  }

  // Mock anims（Phaser Sprite AnimationState 需要）
  const mockAnims = {
    on: vi.fn(),
    create: vi.fn(),
    exists: vi.fn(() => false),
    generateFrameNumbers: vi.fn(() => []),
    play: vi.fn(),
    stop: vi.fn()
  }

  // Mock textures（Phaser Sprite setTexture 需要）
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

  // Mock cache（Phaser 可能需要）
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
        getChildren: vi.fn(() => [])
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

describe('PhysicsManager', () => {
  let scene: Phaser.Scene
  let callbacks: CollisionCallbacks
  let manager: PhysicsManager
  let mockMapManager: MapManager
  let world: WorldManager

  beforeEach(() => {
    // 重置单例
    (WorldManager as any).instance = null;
    (MapManager as any).instance = null

    // 初始化 WorldManager
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
    
    WorldManager.initialize(mockGame)
    world = WorldManager.getInstance()
    world.api.setConfig({
      teams: [],
      setup: {
        numPlayers: 2,
        numFlags: 3,
        useRandomFlags: false,
        mapWidth: 20,
        mapHeight: 20
      },
      servers: {}
    })
    
    scene = createMockScene()
    mockMapManager = MapManager.getInstance(world)
    mockMapManager.setMapParams({
      mapWidth: 20,
      mapHeight: 20,
      tileSize: 32,
      centerX: 480,
      centerY: 320,
      mapX: 100,
      mapY: 100
    })
    callbacks = {
      onScoreUpdate: vi.fn(),
      onCreateFlag: vi.fn((world, scene, x, y, team, canPickup) => {
        return new Flag(world, scene, x, y, team, canPickup)
      })
    }
    manager = new PhysicsManager(world, scene, callbacks)
  })

  describe('初始化', () => {
    it('应该正确创建 PhysicsManager', () => {
      expect(manager).toBeInstanceOf(PhysicsManager)
    })

    it('应该能够设置游戏对象', () => {
      const lteamPlayers = scene.add.group()
      const rteamPlayers = scene.add.group()
      const lteamFlags = scene.add.group()
      const rteamFlags = scene.add.group()

      manager.setGameObjects(
        mockMapManager,
        lteamPlayers,
        rteamPlayers,
        lteamFlags,
        rteamFlags
      )

      // 验证设置成功（setGameObjects 不调用 overlap，只是存储引用）
      expect(manager).toBeInstanceOf(PhysicsManager)
    })
  })

  describe('addPhysicsBody', () => {
    it('应该为游戏对象添加物理体', () => {
      const mockBody = {
        setAllowGravity: vi.fn(),
        setImmovable: vi.fn()
      }
      const mockGameObject = {
        body: mockBody
      } as unknown as Phaser.GameObjects.GameObject

      manager.addPhysicsBody(mockGameObject, false, true)
      expect(scene.physics.add.existing).toHaveBeenCalledWith(mockGameObject)
    })
  })

  describe('setupCollisions', () => {
    let lteamPlayers: Phaser.GameObjects.Group
    let rteamPlayers: Phaser.GameObjects.Group
    let lteamFlags: Phaser.GameObjects.Group
    let rteamFlags: Phaser.GameObjects.Group
    let lteamTargetZone: Phaser.GameObjects.Zone
    let rteamTargetZone: Phaser.GameObjects.Zone
    let lteamPrisonZone: Phaser.GameObjects.Zone
    let rteamPrisonZone: Phaser.GameObjects.Zone

    beforeEach(() => {
      lteamPlayers = scene.add.group()
      rteamPlayers = scene.add.group()
      lteamFlags = scene.add.group()
      rteamFlags = scene.add.group()
      lteamTargetZone = scene.add.zone(0, 0, 100, 100) as Phaser.GameObjects.Zone
      rteamTargetZone = scene.add.zone(0, 0, 100, 100) as Phaser.GameObjects.Zone
      lteamPrisonZone = scene.add.zone(0, 0, 100, 100) as Phaser.GameObjects.Zone
      rteamPrisonZone = scene.add.zone(0, 0, 100, 100) as Phaser.GameObjects.Zone

      manager.setGameObjects(
        mockMapManager,
        lteamPlayers,
        rteamPlayers,
        lteamFlags,
        rteamFlags
      )
    })

    it('应该设置所有碰撞检测', () => {
      manager.setupCollisions(
        lteamPlayers,
        rteamPlayers,
        lteamFlags,
        rteamFlags,
        lteamTargetZone,
        rteamTargetZone,
        lteamPrisonZone,
        rteamPrisonZone
      )

      // 验证设置了多种碰撞检测（7次：玩家碰撞、2次旗帜收集、2次旗帜放置、2次玩家释放）
      expect(scene.physics.add.overlap).toHaveBeenCalledTimes(7)
    })
  })

  describe('碰撞处理', () => {
    let lteamPlayers: Phaser.GameObjects.Group
    let rteamPlayers: Phaser.GameObjects.Group
    let lteamFlags: Phaser.GameObjects.Group
    let rteamFlags: Phaser.GameObjects.Group

    beforeEach(() => {
      // 初始化 WorldManager
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
      
      // 重置单例实例
      const gsManager = WorldManager as any
      gsManager.instance = null
      WorldManager.initialize(mockGame)
      
      world.api.setConfig({
        teams: [],
        setup: {
          numPlayers: 2,
          numFlags: 3,
          useRandomFlags: false,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {}
      })
      const mapManager = MapManager.getInstance(world)
      mapManager.setMapParams({
        centerX: 480,
        centerY: 480,
        mapWidth: 20,
        mapHeight: 20,
        mapX: 100,
        mapY: 100,
        tileSize: 32
      })

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

    describe('handleFlagCollected', () => {
      it('应该处理玩家收集旗帜', () => {
        const player = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const flag = new Flag(world, scene, 5, 5, 'R', true)
        player.inPrison = false
        player.hasFlag = false

        // 通过反射调用私有方法
        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handleFlagCollected(player, flag)

        expect(player.hasFlag).toBe(true)
      })

      it('不应该让同队玩家收集同队旗帜', () => {
        const player = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const flag = new Flag(world, scene, 5, 5, 'L', true)
        player.hasFlag = false

        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handleFlagCollected(player, flag)

        expect(player.hasFlag).toBe(false)
      })

      it('不应该让监狱中的玩家收集旗帜', () => {
        const player = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const flag = new Flag(world, scene, 5, 5, 'R', true)
        player.inPrison = true
        player.hasFlag = false

        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handleFlagCollected(player, flag)

        expect(player.hasFlag).toBe(false)
      })

      it('不应该让已持有旗帜的玩家收集旗帜', () => {
        const player = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const flag = new Flag(world, scene, 5, 5, 'R', true)
        player.hasFlag = true

        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handleFlagCollected(player, flag)

        // hasFlag 应该保持为 true
        expect(player.hasFlag).toBe(true)
      })
    })

    describe('handlePlayerFreed', () => {
      it('应该释放监狱中的所有队友', () => {
        const player1 = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const player2 = new Player(world, scene, 'L1', 5, 6, 'L', 1, true)
        player1.inPrison = false
        player2.inPrison = true

        lteamPlayers.getChildren = vi.fn(() => [player1, player2])

        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handlePlayerFreed(player1)

        expect(player2.inPrison).toBe(false)
      })

      it('不应该让监狱中的玩家释放队友', () => {
        const player1 = new Player(world, scene, 'L0', 5, 5, 'L', 1, true)
        const player2 = new Player(world, scene, 'L1', 5, 6, 'L', 1, true)
        player1.inPrison = true
        player2.inPrison = true

        lteamPlayers.getChildren = vi.fn(() => [player1, player2])

        const collisionHandler = manager.getCollisionHandler()
        collisionHandler.handlePlayerFreed(player1)

        // player1 在监狱中，不应该释放队友
        expect(player2.inPrison).toBe(true)
      })
    })

    describe('handlePlayerHit - 防止未定义变量错误', () => {
      beforeEach(() => {
        // 设置团队状态（关键：防止 state 未定义错误）
        // 通过 generateTargetsAndPrisons 来设置监狱位置
        const mapManager = MapManager.getInstance(world)
        const mapParams = mapManager.getMapParams()
        
        // 生成目标和监狱位置（这会设置 lTeamState 和 rTeamState）
        world.api.generateTargetsAndPrisons(mapParams.mapWidth, mapParams.mapHeight)
        
        // 验证团队状态已正确设置
        const teamStates = world.api.getTeamStates()
        expect(teamStates.lTeamState.prison).toBeDefined()
        expect(teamStates.rTeamState.prison).toBeDefined()
        expect(teamStates.lTeamState.prison.length).toBeGreaterThan(0)
        expect(teamStates.rTeamState.prison.length).toBeGreaterThan(0)
      })

      it('应该正确处理左侧碰撞（R队被抓）- 确保从 WorldManager 获取状态', () => {
        const lPlayer = new Player(world, scene, 'L0', 200, 300, 'L', 1, true) // 左侧 (centerX=480, 200<480)
        const rPlayer = new Player(world, scene, 'R0', 250, 300, 'R', 4, false) // 左侧 (centerX=480, 250<480)
        lPlayer.inPrison = false
        rPlayer.inPrison = false
        rPlayer.hasFlag = true

        // 设置玩家组和 flags 组
        lteamPlayers.getChildren = vi.fn(() => [lPlayer])
        rteamPlayers.getChildren = vi.fn(() => [rPlayer])
        lteamFlags.add = vi.fn()
        rteamFlags.add = vi.fn()

        // Mock getTileAt
        const getTileAtSpy = vi.spyOn(mockMapManager, 'getTileAt').mockReturnValue({
          x: 6,
          y: 9
        } as any)

        // Mock toPrison 方法
        const toPrisonSpy = vi.spyOn(rPlayer, 'toPrison').mockImplementation(() => {})

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 关键测试：不应该抛出未定义变量错误（确保 state 已定义）
        // 这是最重要的测试 - 防止 "state is not defined" 错误
        expect(() => {
          handlePlayerHit(lPlayer as any, rPlayer as any)
        }).not.toThrow()

        // 验证团队状态已正确获取（不会出现未定义错误）
        const teamStates = world.api.getTeamStates()
        expect(teamStates.rTeamState.prison).toBeDefined()
        expect(Array.isArray(teamStates.rTeamState.prison)).toBe(true)
      })

      it('应该正确处理右侧碰撞（L队被抓）- 确保从 WorldManager 获取状态', () => {
        const lPlayer = new Player(world, scene, 'L0', 700, 300, 'L', 1, true) // 右侧 (centerX=480, 700>480)
        const rPlayer = new Player(world, scene, 'R0', 750, 300, 'R', 4, false) // 右侧 (centerX=480, 750>480)
        lPlayer.inPrison = false
        rPlayer.inPrison = false
        lPlayer.hasFlag = true

        // 设置玩家组和 flags 组
        lteamPlayers.getChildren = vi.fn(() => [lPlayer])
        rteamPlayers.getChildren = vi.fn(() => [rPlayer])
        lteamFlags.add = vi.fn()
        rteamFlags.add = vi.fn()

        // Mock getTileAt
        const getTileAtSpy = vi.spyOn(mockMapManager, 'getTileAt').mockReturnValue({
          x: 21,
          y: 9
        } as any)

        // Mock toPrison 方法
        const toPrisonSpy = vi.spyOn(lPlayer, 'toPrison').mockImplementation(() => {})

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 不应该抛出未定义变量错误（关键测试：确保 state 已定义）
        expect(() => {
          handlePlayerHit(lPlayer, rPlayer)
        }).not.toThrow()

        // 验证 L 队玩家被抓（在右侧，L队被抓）
        expect(toPrisonSpy).toHaveBeenCalled()
        expect(lPlayer.hasFlag).toBe(false)
        expect(rteamFlags.add).toHaveBeenCalled()
      })

      it('不应该处理同队玩家碰撞', () => {
        const lPlayer1 = new Player(world, scene, 'L0', 200, 300, 'L', 1, true)
        const lPlayer2 = new Player(world, scene, 'L1', 250, 300, 'L', 1, true)
        lPlayer1.inPrison = false
        lPlayer2.inPrison = false

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 同队玩家碰撞应该直接返回，不处理
        expect(() => {
          handlePlayerHit(lPlayer1, lPlayer2)
        }).not.toThrow()
      })

      it('不应该处理监狱中玩家的碰撞', () => {
        const lPlayer = new Player(world, scene, 'L0', 200, 300, 'L', 1, true)
        const rPlayer = new Player(world, scene, 'R0', 250, 300, 'R', 4, false)
        lPlayer.inPrison = true
        rPlayer.inPrison = false

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 监狱中的玩家碰撞应该直接返回，不处理
        expect(() => {
          handlePlayerHit(lPlayer, rPlayer)
        }).not.toThrow()
      })

      it('应该正确处理没有旗帜的玩家碰撞 - 确保从 WorldManager 获取状态', () => {
        const lPlayer = new Player(world, scene, 'L0', 200, 300, 'L', 1, true) // 左侧
        const rPlayer = new Player(world, scene, 'R0', 250, 300, 'R', 4, false) // 左侧
        lPlayer.inPrison = false
        rPlayer.inPrison = false
        rPlayer.hasFlag = false

        // 设置玩家组和 flags 组
        lteamPlayers.getChildren = vi.fn(() => [lPlayer])
        rteamPlayers.getChildren = vi.fn(() => [rPlayer])
        lteamFlags.add = vi.fn()
        rteamFlags.add = vi.fn()

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 关键测试：不应该抛出未定义变量错误（确保 state 已定义）
        // 这是最重要的测试 - 防止 "state is not defined" 错误
        expect(() => {
          handlePlayerHit(lPlayer as any, rPlayer as any)
        }).not.toThrow()

        // 验证团队状态已正确获取（不会出现未定义错误）
        const teamStates = world.api.getTeamStates()
        expect(teamStates.rTeamState.prison).toBeDefined()
        expect(Array.isArray(teamStates.rTeamState.prison)).toBe(true)
      })

      it('应该正确处理 WorldManager 返回的监狱位置', () => {
        const teamStates = world.api.getTeamStates()
        
        // 验证团队状态已正确设置
        expect(teamStates.lTeamState.prison).toBeDefined()
        expect(teamStates.rTeamState.prison).toBeDefined()
        expect(Array.isArray(teamStates.lTeamState.prison)).toBe(true)
        expect(Array.isArray(teamStates.rTeamState.prison)).toBe(true)
        expect(teamStates.lTeamState.prison.length).toBeGreaterThan(0)
        expect(teamStates.rTeamState.prison.length).toBeGreaterThan(0)

        const lPlayer = new Player(world, scene, 'L0', 200, 300, 'L', 1, true)
        const rPlayer = new Player(world, scene, 'R0', 250, 300, 'R', 4, false)
        lPlayer.inPrison = false
        rPlayer.inPrison = false

        lteamPlayers.getChildren = vi.fn(() => [lPlayer])
        rteamPlayers.getChildren = vi.fn(() => [rPlayer])

        const collisionHandler = manager.getCollisionHandler()
        const handlePlayerHit = collisionHandler.handlePlayerHit.bind(collisionHandler)
        
        // 确保使用 WorldManager 获取的状态，不会出现未定义错误
        expect(() => {
          handlePlayerHit(lPlayer, rPlayer)
        }).not.toThrow()
      })
    })
  })

  describe('辅助方法', () => {
    beforeEach(() => {
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
      
      // 重置单例实例
      const gsManager = WorldManager as any
      gsManager.instance = null
      WorldManager.initialize(mockGame)
      
      world.api.setConfig({
        teams: [],
        setup: {
          numPlayers: 2,
          numFlags: 3,
          useRandomFlags: false,
          mapWidth: 20,
          mapHeight: 20
        },
        servers: {}
      })
      mockMapManager = MapManager.getInstance(world)
      mockMapManager.setMapParams({
        centerX: 480,
        centerY: 480,
        mapWidth: 20,
        mapHeight: 20,
        mapX: 100,
        mapY: 100,
        tileSize: 32
      })
      
      manager.setGameObjects(
        mockMapManager,
        scene.add.group(),
        scene.add.group(),
        scene.add.group(),
        scene.add.group()
      )
    })

    describe('findAvailablePrisonTile', () => {
      it('应该找到可用的监狱位置', () => {
        const prisons: Position[] = [
          { x: 2, y: 17 },
          { x: 3, y: 17 }
        ]
        const players: Player[] = []

        const collisionHandler = manager.getCollisionHandler()
        const positionFinder = collisionHandler.getPositionFinder()
        const result = positionFinder.findAvailablePrisonTile(players, prisons)

        expect(result).toEqual({ x: 2, y: 17 })
      })

      it('应该跳过已被占用的监狱位置', () => {
        const prisons: Position[] = [
          { x: 2, y: 17 },
          { x: 3, y: 17 }
        ]
        const player = new Player(world, scene, 'L0', 2, 17, 'L', 1, true)
        player.inPrison = true
        const players: Player[] = [player]

        // Mock getTileAt 根据世界坐标返回对应的 tile
        // Player 的世界坐标 = mapOffset.x + x * tileSize = 100 + 2 * 32 = 164
        // Player 的世界坐标 = mapOffset.y + y * tileSize = 100 + 17 * 32 = 644
        const getTileAtSpy = vi.spyOn(mockMapManager, 'getTileAt').mockImplementation((x: number, y: number) => {
          // 将世界坐标转换为地图坐标
          const mapX = Math.floor((x - 100) / 32)
          const mapY = Math.floor((y - 100) / 32)
          // 返回 tile 对象，其 x 和 y 是地图坐标
          return { x: mapX, y: mapY } as any
        })

        const collisionHandler = manager.getCollisionHandler()
        const positionFinder = collisionHandler.getPositionFinder()
        const result = positionFinder.findAvailablePrisonTile(players, prisons)

        expect(result).toEqual({ x: 3, y: 17 })
      })
    })

    describe('findAvailableFlagTile', () => {
      it('应该找到可用的旗帜位置', () => {
        const targets: Position[] = [
          { x: 2, y: 10 },
          { x: 3, y: 10 }
        ]
        const flags: Flag[] = []

        const collisionHandler = manager.getCollisionHandler()
        const positionFinder = collisionHandler.getPositionFinder()
        const result = positionFinder.findAvailableFlagTile(flags, targets)

        expect(result).toEqual({ x: 2, y: 10 })
      })

      it('应该跳过已被占用的旗帜位置', () => {
        const targets: Position[] = [
          { x: 2, y: 10 },
          { x: 3, y: 10 }
        ]
        const flag = new Flag(world, scene, 2, 10, 'R', false)
        const flags: Flag[] = [flag]

        // Mock getTileAt 根据世界坐标返回对应的 tile
        // Flag 的世界坐标 = mapOffset.x + x * tileSize = 100 + 2 * 32 = 164
        // Flag 的世界坐标 = mapOffset.y + y * tileSize = 100 + 10 * 32 = 420
        const getTileAtSpy = vi.spyOn(mockMapManager, 'getTileAt').mockImplementation((x: number, y: number) => {
          // 将世界坐标转换为地图坐标
          const mapX = Math.floor((x - 100) / 32)
          const mapY = Math.floor((y - 100) / 32)
          // 返回 tile 对象，其 x 和 y 是地图坐标
          return { x: mapX, y: mapY } as any
        })

        const collisionHandler = manager.getCollisionHandler()
        const positionFinder = collisionHandler.getPositionFinder()
        const result = positionFinder.findAvailableFlagTile(flags, targets)

        expect(result).toEqual({ x: 3, y: 10 })
      })
    })
  })
})

