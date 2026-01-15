import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Preloader } from '../Preloader'
import { WorldManager } from '../../managers/WorldManager'

// Mock WorldManager.sendFlowEvent
vi.spyOn(WorldManager, 'sendFlowEvent').mockImplementation(() => {})

// Mock Phaser Scene
const createMockScene = () => {
  const mockLoad = {
    on: vi.fn(),
    image: vi.fn(),
    spritesheet: vi.fn(),
    tilemapTiledJSON: vi.fn()
  }

  return {
    add: {
      rectangle: vi.fn(() => ({
        setStrokeStyle: vi.fn().mockReturnThis()
      }))
    },
    load: mockLoad,
    scene: {
      get: vi.fn(() => ({
        scene: {
          key: 'Game'
        }
      })),
      isActive: vi.fn(() => false),
      launch: vi.fn()
    },
    scale: {
      width: 960,
      height: 960
    }
  } as unknown as Phaser.Scene
}

describe('Preloader', () => {
  let preloader: Preloader

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
    WorldManager.initialize(mockGame)

    preloader = new Preloader()
    const mockScene = createMockScene()
    preloader.scene = { 
      ...mockScene.scene, 
      key: 'Preloader',
      start: vi.fn(),
      launch: vi.fn()
    } as any
    preloader.add = mockScene.add as any
    preloader.load = mockScene.load as any
    preloader.scale = mockScene.scale as any
  })

  describe('初始化', () => {
    it('应该正确创建 Preloader 场景', () => {
      expect(preloader).toBeInstanceOf(Preloader)
      expect(preloader.scene.key).toBe('Preloader')
    })
  })

  describe('init', () => {
    it('应该创建进度条', () => {
      preloader.init()
      expect(preloader.add.rectangle).toHaveBeenCalled()
    })

    it('应该监听加载进度', () => {
      preloader.init()
      expect(preloader.load.on).toHaveBeenCalledWith('progress', expect.any(Function))
    })

    it('应该监听加载完成', () => {
      preloader.init()
      expect(preloader.load.on).toHaveBeenCalledWith('complete', expect.any(Function))
    })

    it('应该监听加载错误', () => {
      preloader.init()
      expect(preloader.load.on).toHaveBeenCalledWith('loaderror', expect.any(Function))
    })
  })

  describe('preload', () => {
    it('应该能够执行 preload 方法', () => {
      expect(() => preloader.preload()).not.toThrow()
    })
  })

  describe('create', () => {
    it('应该启动 Game 场景', () => {
      preloader.create()
      expect(preloader.scene.start).toHaveBeenCalledWith('Game')
    })
  })
})

