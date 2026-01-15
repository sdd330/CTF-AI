import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Flag } from '../Flag'
import { WorldManager } from '../../managers/WorldManager'
import type { Team } from '@/types'

// Mock ASSETS
vi.mock('../../config/assets', () => ({
  default: {
    spritesheet: {
      L_flag: {
        key: 'L_flag'
      },
      R_flag: {
        key: 'R_flag'
      }
    }
  }
}))

// Mock Phaser Scene
const createMockScene = () => {
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

  return {
    add: {
      existing: vi.fn()
    },
    physics: {
      add: {
        existing: vi.fn()
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
    removeFlagItem: vi.fn()
  } as unknown as Phaser.Scene
}

describe('Flag', () => {
  let scene: Phaser.Scene
  let flag: Flag
  let world: WorldManager

  beforeEach(() => {
    // 重置单例并初始化 WorldManager
    (WorldManager as any).instance = null
    const mockGame = {
      registry: {
        set: vi.fn(),
        get: vi.fn(() => ({})),
        has: vi.fn(() => false)
      },
      events: {
        emit: vi.fn(),
        on: vi.fn(),
        off: vi.fn()
      }
    } as unknown as Phaser.Game
    WorldManager.initialize(mockGame)
    world = WorldManager.getInstance()

    scene = createMockScene()
  })

  describe('初始化', () => {
    it('应该正确设置 L 队旗帜', () => {
      flag = new Flag(world, scene, 5, 5, 'L', true)
      expect(flag.team).toBe('L')
      expect(flag.canPickup).toBe(true)
    })

    it('应该正确设置 R 队旗帜', () => {
      flag = new Flag(world, scene, 10, 10, 'R', false)
      expect(flag.team).toBe('R')
      expect(flag.canPickup).toBe(false)
    })

    it('应该正确设置旗帜位置', () => {
      flag = new Flag(world, scene, 5, 5, 'L', true)
      const mapOffset = (scene as any).getMapOffset()
      const expectedX = mapOffset.x + (5 * mapOffset.tileSize)
      const expectedY = mapOffset.y + (5 * mapOffset.tileSize)
      expect(flag.x).toBe(expectedX)
      expect(flag.y).toBe(expectedY)
    })
  })

  describe('collect', () => {
    it('应该能够收集可拾取的旗帜', () => {
      flag = new Flag(world, scene, 5, 5, 'L', true)
      const result = flag.collect()
      expect(result).toBe(true)
      expect((scene as any).removeFlagItem).toHaveBeenCalledWith(flag)
    })

    it('不应该收集不可拾取的旗帜', () => {
      flag = new Flag(world, scene, 5, 5, 'L', false)
      const result = flag.collect()
      expect(result).toBe(false)
      expect((scene as any).removeFlagItem).not.toHaveBeenCalled()
    })
  })

  describe('getStatus', () => {
    it('应该返回正确的旗帜状态', () => {
      flag = new Flag(world, scene, 5, 5, 'L', true)
      const status = flag.getStatus()
      expect(status.canPickup).toBe(true)
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(5)
    })

    it('应该返回正确的不可拾取旗帜状态', () => {
      flag = new Flag(world, scene, 10, 10, 'R', false)
      const status = flag.getStatus()
      expect(status.canPickup).toBe(false)
      expect(status.posX).toBe(10)
      expect(status.posY).toBe(10)
    })
  })
})

