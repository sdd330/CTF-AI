import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Player, PlayerDirection } from '../Player'
import { WorldManager } from '../../managers/WorldManager'
import type { Team } from '@/types'

// Mock ASSETS
vi.mock('../../config/assets', () => ({
  default: {
    spritesheet: {
      characters: {
        key: 'characters'
      }
    }
  }
}))

// Mock InputManager
const createMockInputManager = () => ({
  setRemoteControl: vi.fn(),
  getCurrentDirection: vi.fn(() => ''),
  update: vi.fn(),
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  initKeyboard: vi.fn(),
  reset: vi.fn(),
  destroy: vi.fn()
})

// Mock Phaser Scene
const createMockScene = () => {
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

  // Mock physics body（Phaser Arcade Sprite 需要）
  const mockBody = {
    setCollideWorldBounds: vi.fn(),
    setSize: vi.fn(),
    setOffset: vi.fn(),
    x: 0,
    y: 0,
    width: 32,
    height: 32
  }

  return {
    add: {
      existing: vi.fn()
    },
    physics: {
      add: {
        existing: vi.fn((sprite: any) => {
          // 为 sprite 添加 body
          sprite.body = mockBody
          return sprite
        })
      },
      world: {
        bounds: {
          x: 0,
          y: 0,
          width: 960,
          height: 960
        }
      }
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
    isWall: () => false
  } as unknown as Phaser.Scene
}

describe('Player', () => {
  let scene: Phaser.Scene
  let player: Player
  let mockInputManager: any
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
    mockInputManager = createMockInputManager()
    player = new Player(world, scene, 'L0', 5, 5, 'L', 1, mockInputManager)
  })

  describe('初始化', () => {
    it('应该正确设置玩家属性', () => {
      expect(player.name).toBe('L0')
      expect(player.team).toBe('L')
      expect(player.spriteChoice).toBe(1)
      expect(player.hasFlag).toBe(false)
      expect(player.inPrison).toBe(false)
    })

    it('应该正确设置目标位置', () => {
      const mapOffset = (scene as any).getMapOffset()
      const expectedX = mapOffset.x + (5 * mapOffset.tileSize)
      const expectedY = mapOffset.y + (5 * mapOffset.tileSize)
      expect(player.target.x).toBe(expectedX)
      expect(player.target.y).toBe(expectedY)
    })
  })

  describe('旗帜操作', () => {
    it('应该能够收集旗帜', () => {
      player.collectFlag()
      expect(player.hasFlag).toBe(true)
    })

    it('应该能够放下旗帜', () => {
      player.collectFlag()
      player.dropFlag()
      expect(player.hasFlag).toBe(false)
    })
  })

  describe('远程控制', () => {
    it('应该能够设置远程控制方向', () => {
      player.setRemoteControl('right')
      expect(player.remoteControl).toBe('right')
      // 应该同时更新 InputManager
      expect(mockInputManager.setRemoteControl).toHaveBeenCalledWith('right')
    })

    it('应该在方向改变时更新目标位置', () => {
      const originalTargetX = player.target.x
      player.setRemoteControl('right')
      // 方向改变时，目标位置应该被设置为当前位置
      expect(player.target.x).toBe(player.x)
      // 应该同时更新 InputManager
      expect(mockInputManager.setRemoteControl).toHaveBeenCalledWith('right')
    })
  })

  describe('监狱操作', () => {
    it('应该能够将玩家送到监狱', () => {
      player.toPrison(10, 10)
      expect(player.inPrison).toBe(true)
      expect(player.inPrisonTimeLeft).toBe(player.inPrisonDuration)
    })

    it('应该正确设置监狱位置', () => {
      const mapOffset = (scene as any).getMapOffset()
      player.toPrison(10, 10)
      const expectedX = mapOffset.x + (10 * mapOffset.tileSize)
      const expectedY = mapOffset.y + (10 * mapOffset.tileSize)
      expect(player.target.x).toBe(expectedX)
      expect(player.target.y).toBe(expectedY)
    })
  })

  describe('canGoNextTile', () => {
    it('应该能够设置 canGoNextTile', () => {
      player.setCanGoNextTile(true)
      expect((player as any).movement.canGoNextTile).toBe(true)
    })

    it('应该使用位或操作符累积标志', () => {
      player.setCanGoNextTile(true)
      expect((player as any).movement.canGoNextTile).toBe(true)
      player.setCanGoNextTile(false)
      // false 不应该改变值
      expect((player as any).movement.canGoNextTile).toBe(true)
    })
  })

  describe('getStatus', () => {
    it('应该返回正确的玩家状态', () => {
      const status = player.getStatus()
      expect(status.name).toBe('L0')
      expect(status.team).toBe('L')
      expect(status.hasFlag).toBe(false)
      expect(status.inPrison).toBe(false)
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(5)
    })

    it('应该返回目标位置而不是当前位置', () => {
      player.target.x = 200
      player.target.y = 300
      const status = player.getStatus()
      const mapOffset = (scene as any).getMapOffset()
      const expectedX = Math.round((200 - mapOffset.x) / mapOffset.tileSize)
      const expectedY = Math.round((300 - mapOffset.y) / mapOffset.tileSize)
      expect(status.posX).toBe(expectedX)
      expect(status.posY).toBe(expectedY)
    })
  })
})

