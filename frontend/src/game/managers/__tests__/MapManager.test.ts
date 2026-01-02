import { describe, it, expect, beforeEach, vi } from 'vitest'
import { MapManager, TileData } from '../MapManager'
import { GameStateManager } from '../GameStateManager'

// Mock Phaser Math.RND
vi.mock('phaser', () => {
  const mockRND = {
    integerInRange: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
    pick: <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)]
  }
  return {
    default: {
      Math: {
        RND: mockRND
      },
      Physics: {
        Arcade: {
          Sprite: class MockSprite {
            constructor() {}
          }
        }
      },
      Input: {
        Keyboard: {
          KeyCodes: {
            SPACE: 32
          }
        }
      }
    },
    Math: {
      RND: mockRND
    },
    Physics: {
      Arcade: {
        Sprite: class MockSprite {
          constructor() {}
        }
      }
    },
    Input: {
      Keyboard: {
        KeyCodes: {
          SPACE: 32
        }
      }
    }
  }
})

// Mock ASSETS
vi.mock('../../config/assets', () => ({
  default: {
    tilemapTiledJSON: {
      map: { key: 'map' }
    },
    spritesheet: {
      tiles: { key: 'tiles' }
    }
  }
}))

// Mock Phaser Scene for renderer tests
const createMockScene = () => {
  const mockLayer = {
    putTileAt: vi.fn(),
    getTileAt: vi.fn((x: number, y: number) => ({
      x,
      y,
      index: 0,
      setCollision: vi.fn(),
      setDepth: vi.fn().mockReturnThis(),
      setVisible: vi.fn().mockReturnThis(),
      visible: true,
      alpha: 1,
      depth: 0
    })),
    getTileAtWorldXY: vi.fn((x: number, y: number) => ({
      x: Math.floor(x / 32),
      y: Math.floor(y / 32),
      index: 0
    })),
    fill: vi.fn(),
    destroy: vi.fn(),
    setDepth: vi.fn().mockReturnThis(),
    setVisible: vi.fn().mockReturnThis(),
    visible: true,
    alpha: 1,
    depth: 0
  }

  const mockMap = {
    createBlankLayer: vi.fn((_name: string, _tileset: unknown, _x: number, _y: number) => mockLayer),
    addTilesetImage: vi.fn(() => ({})),
    setCollision: vi.fn()
  }

  return {
    make: {
      tilemap: vi.fn(() => mockMap)
    },
    add: {
      line: vi.fn(() => ({
        setOrigin: vi.fn().mockReturnThis(),
        setLineWidth: vi.fn().mockReturnThis()
      }))
    },
    cache: {
      tilemap: {
        exists: vi.fn(() => true),
        entries: {}
      }
    },
    textures: {
      exists: vi.fn(() => true),
      list: {}
    },
    scale: {
      width: 960,
      height: 960
    }
  } as unknown as Phaser.Scene
}

describe('MapManager', () => {
  let registryData: Record<string, any> = {}
  let mockGame: Phaser.Game

  beforeEach(() => {
    // 初始化 GameStateManager
    registryData = {}
    mockGame = {
      registry: {
        set: vi.fn((key: string, value: any) => {
          registryData[key] = value
        }),
        get: vi.fn((key: string) => {
          // 如果 key 不存在，返回初始状态
          if (!(key in registryData)) {
            return undefined
          }
          return registryData[key]
        }),
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
    const manager = GameStateManager as any
    manager.instance = null
    
    GameStateManager.initialize(mockGame)
    const gameState = GameStateManager.getInstance()
    
    // 重置地图状态（清除之前的墙壁和障碍物）
    gameState.resetMapState()
    
    // 设置基本配置
    gameState.setConfig({
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
    
    // 设置地图参数（由 MapManager 管理）
    const mapManager = MapManager.getInstance()
    mapManager.setMapParams({
      mapWidth: 20,
      mapHeight: 20,
      tileSize: 32,
      mapX: 0,
      mapY: 0,
      centerX: 480,
      centerY: 320
    })
  })

  describe('generateWalls', () => {
    it('应该生成正确数量的墙壁', () => {
      const manager = MapManager.getInstance()
      const gameState = GameStateManager.getInstance()
      
      // 重置地图状态
      gameState.resetMapState()
      
      // 确保地图参数已设置
      manager.setMapParams({ 
        mapWidth: 20, 
        mapHeight: 20, 
        tileSize: 32,
        mapX: 0,
        mapY: 0,
        centerX: 480,
        centerY: 320
      })
      
      // 生成墙壁
      manager.generateWalls()
      
      const state = gameState.getState()
      const walls = state.walls
      const mapParams = manager.getMapParams()
      
      // 墙壁数量 = 4个角 + 上下各 (width-2) + 左右各 (height-2)
      const expectedCount = 4 + (mapParams.mapWidth - 2) * 2 + (mapParams.mapHeight - 2) * 2
      expect(walls.length).toBe(expectedCount)
    })

    it('应该包含四个角的墙壁', () => {
      const manager = MapManager.getInstance()
      const gameState = GameStateManager.getInstance()
      
      // 重置地图状态
      gameState.resetMapState()
      
      // 确保地图参数已设置
      manager.setMapParams({ 
        mapWidth: 20, 
        mapHeight: 20, 
        tileSize: 32,
        mapX: 0,
        mapY: 0,
        centerX: 480,
        centerY: 320
      })
      manager.generateWalls()
      
      const state = gameState.getState()
      const walls = state.walls
      const mapParams = manager.getMapParams()
      
      // 确保墙壁已生成
      expect(walls.length).toBeGreaterThan(0)
      
      const corners = [
        { x: 0, y: 0 },
        { x: mapParams.mapWidth - 1, y: 0 },
        { x: 0, y: mapParams.mapHeight - 1 },
        { x: mapParams.mapWidth - 1, y: mapParams.mapHeight - 1 }
      ]
      
      corners.forEach(corner => {
        expect(walls.some(w => w.x === corner.x && w.y === corner.y)).toBe(true)
      })
    })
  })

  describe('generateObstacles', () => {
    it('应该生成正确数量的障碍物1', () => {
      const manager = MapManager.getInstance()
      const gameState = GameStateManager.getInstance()
      
      // 重置地图状态
      gameState.resetMapState()
      
      // 确保地图参数已设置
      manager.setMapParams({ 
        mapWidth: 20, 
        mapHeight: 20, 
        tileSize: 32,
        mapX: 0,
        mapY: 0,
        centerX: 480,
        centerY: 320
      })
      
      // 确保 GameStateManager 有 numObstacles1 和 numObstacles2
      const state = gameState.getState()
      expect(state.numObstacles1).toBeGreaterThan(0)
      expect(state.numObstacles2).toBeGreaterThan(0)
      
      manager.generateObstacles()
      
      const finalState = gameState.getState()
      expect(finalState.obstacles1.length).toBe(finalState.numObstacles1)
    })

    it('应该生成正确数量的障碍物2', () => {
      const manager = MapManager.getInstance()
      const gameState = GameStateManager.getInstance()
      
      // 重置地图状态
      gameState.resetMapState()
      
      // 确保地图参数已设置
      manager.setMapParams({ 
        mapWidth: 20, 
        mapHeight: 20, 
        tileSize: 32,
        mapX: 0,
        mapY: 0,
        centerX: 480,
        centerY: 320
      })
      
      manager.generateObstacles()
      
      const state = gameState.getState()
      expect(state.obstacles2.length).toBe(state.numObstacles2)
    })

    it('障碍物不应该重叠', () => {
      const manager = MapManager.getInstance()
      manager.setMapParams({ mapWidth: 20, mapHeight: 20, tileSize: 32 })
      
      manager.generateObstacles()
      
      const gameState = GameStateManager.getInstance()
      const state = gameState.getState()
      const obstacles1 = state.obstacles1
      const obstacles2 = state.obstacles2
      
      // 检查 obstacles1 内部不重叠
      for (let i = 0; i < obstacles1.length; i++) {
        for (let j = i + 1; j < obstacles1.length; j++) {
          expect(obstacles1[i].x !== obstacles1[j].x || obstacles1[i].y !== obstacles1[j].y).toBe(true)
        }
      }
      
      // 检查 obstacles2 内部不重叠
      for (let i = 0; i < obstacles2.length; i++) {
        for (let j = i + 1; j < obstacles2.length; j++) {
          expect(obstacles2[i].x !== obstacles2[j].x || obstacles2[i].y !== obstacles2[j].y).toBe(true)
        }
      }
    })
  })

  describe('地图渲染器初始化', () => {
    let scene: Phaser.Scene
    let mapManager: MapManager

    beforeEach(() => {
      scene = createMockScene()
      // 先设置 MapManager 的地图参数
      mapManager = MapManager.getInstance()
      mapManager.setMapParams({
        mapX: 100,
        mapY: 100,
        mapWidth: 20,
        mapHeight: 20,
        tileSize: 32,
        centerX: 480,
        centerY: 320
      })
      mapManager.initializeRenderer(scene)
    })

    it('应该正确初始化 MapManager 渲染器并获取地图偏移量', () => {
      expect(mapManager).toBeInstanceOf(MapManager)
      const offset = mapManager.getMapOffset()
      expect(offset.x).toBe(116) // 100 + 32 * 0.5
      expect(offset.y).toBe(116) // 100 + 32 * 0.5
      expect(offset.width).toBe(20)
      expect(offset.height).toBe(20)
      expect(offset.tileSize).toBe(32)
    })
  })

  describe('图层创建', () => {
    let scene: Phaser.Scene
    let mapManager: MapManager

    beforeEach(() => {
      scene = createMockScene()
      // 先设置 MapManager 的地图参数
      mapManager = MapManager.getInstance()
      mapManager.setMapParams({
        mapX: 100,
        mapY: 100,
        mapWidth: 20,
        mapHeight: 20,
        tileSize: 32,
        centerX: 480,
        centerY: 320
      })
      mapManager.initializeRenderer(scene)
    })

    it('应该能够创建背景图层', () => {
      const groundLayer = mapManager.createGroundLayer()
      expect(groundLayer).toBeDefined()
      expect(mapManager.getLevelLayer()).toBeNull()
    })

    it('应该能够创建关卡图层', () => {
      const levelLayer = mapManager.createLevelLayer()
      expect(levelLayer).toBeDefined()
      expect(mapManager.getLevelLayer()).toBe(levelLayer)
    })

    it('应该能够创建边界图层', () => {
      const boundaryLayer = mapManager.createBoundaryLayer(100, 900)
      expect(boundaryLayer).toBeDefined()
    })
  })

  describe('地图查询', () => {
    let scene: Phaser.Scene
    let mapManager: MapManager

    beforeEach(() => {
      scene = createMockScene()
      // 先设置 MapManager 的地图参数
      mapManager = MapManager.getInstance()
      mapManager.setMapParams({
        mapX: 100,
        mapY: 100,
        mapWidth: 20,
        mapHeight: 20,
        tileSize: 32,
        centerX: 480,
        centerY: 320
      })
      mapManager.initializeRenderer(scene)
    })

    it('应该能够检查是否为墙壁', () => {
      mapManager.createLevelLayer()
      const result = mapManager.isWall(160, 160)
      expect(typeof result).toBe('boolean')
    })

    it('应该能够获取世界坐标的图块', () => {
      mapManager.createLevelLayer()
      const result = mapManager.getTileAt(160, 160)
      // getTileAt 可能返回 null 或 Tile 对象
      expect(result === null || typeof result === 'object').toBe(true)
    })
  })
})

describe('TileData', () => {
  describe('享元模式', () => {
    it('应该重用相同的图块数据', () => {
      const tile1 = TileData.getTileData(45, false)
      const tile2 = TileData.getTileData(45, false)
      expect(tile1).toBe(tile2) // 应该是同一个实例
    })

    it('应该为不同的图块 ID 创建不同的实例', () => {
      const tile1 = TileData.getTileData(45, false)
      const tile2 = TileData.getTileData(46, false)
      expect(tile1).not.toBe(tile2)
    })

    it('应该为不同的碰撞属性创建不同的实例', () => {
      const tile1 = TileData.getTileData(45, false)
      const tile2 = TileData.getTileData(45, true)
      expect(tile1).not.toBe(tile2)
    })
  })
})

