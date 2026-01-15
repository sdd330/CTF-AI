import { describe, it, expect, beforeEach, vi } from 'vitest'
import { GameOver } from '../GameOver'
import { WorldManager } from '../../managers/WorldManager'

// Mock WorldManager.sendFlowEvent
vi.spyOn(WorldManager, 'sendFlowEvent').mockImplementation(() => {})

// Mock Phaser Scene
const createMockScene = () => {
  const mockRKey = {
    on: vi.fn()
  }
  const mockLKey = {
    on: vi.fn()
  }

  return {
    add: {
      text: vi.fn(() => ({
        setOrigin: vi.fn().mockReturnThis()
      }))
    },
    input: {
      keyboard: {
        addKey: vi.fn((code: number) => {
          if (code === Phaser.Input.Keyboard.KeyCodes.R) {
            return mockRKey
          }
          return mockLKey
        })
      }
    },
    scale: {
      width: 960,
      height: 960
    }
  } as unknown as Phaser.Scene
}

describe('GameOver', () => {
  let gameOver: GameOver

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
    const world = WorldManager.getInstance()
    world.api.setConfig({
      teams: [],
      setup: {
        numPlayers: 2,
        numFlags: 3,
        useRandomFlags: false
      },
      servers: {}
    })

    gameOver = new GameOver()
    const mockScene = createMockScene()
    gameOver.scene = { key: 'GameOver' } as any
    gameOver.add = mockScene.add as any
    gameOver.input = mockScene.input as any
    gameOver.scale = mockScene.scale as any
  })

  describe('初始化', () => {
    it('应该正确创建 GameOver 场景', () => {
      expect(gameOver).toBeInstanceOf(GameOver)
      expect(gameOver.scene.key).toBe('GameOver')
    })
  })

  describe('create', () => {
    it('应该显示游戏结束文本', () => {
      gameOver.create()
      expect(gameOver.add.text).toHaveBeenCalled()
    })

    it('应该显示重新开始提示', () => {
      gameOver.create()
      // 验证添加了重新开始提示文本
      expect(gameOver.add.text).toHaveBeenCalledTimes(2)
    })

    it('应该设置键盘控制', () => {
      gameOver.create()
      expect(gameOver.input.keyboard!.addKey).toHaveBeenCalledWith(
        Phaser.Input.Keyboard.KeyCodes.R
      )
      expect(gameOver.input.keyboard!.addKey).toHaveBeenCalledWith(
        Phaser.Input.Keyboard.KeyCodes.L
      )
    })

    it('应该在按下 R 键时发送重启事件', () => {
      const mockRKey = {
        on: vi.fn((event: string, callback: () => void) => {
          if (event === 'down') {
            callback()
          }
        })
      }
      gameOver.input.keyboard!.addKey = vi.fn((code: number) => {
        if (code === Phaser.Input.Keyboard.KeyCodes.R) {
          return mockRKey
        }
        return { on: vi.fn() }
      })

      gameOver.create()
      expect(WorldManager.sendFlowEvent).toHaveBeenCalledWith({ type: 'RESTART' })
    })

    it('应该在按下 L 键时发送重新加载事件', () => {
      const mockLKey = {
        on: vi.fn((event: string, callback: () => void) => {
          if (event === 'down') {
            callback()
          }
        })
      }
      gameOver.input.keyboard!.addKey = vi.fn((code: number) => {
        if (code === Phaser.Input.Keyboard.KeyCodes.L) {
          return mockLKey
        }
        return { on: vi.fn() }
      })

      gameOver.create()
      expect(WorldManager.sendFlowEvent).toHaveBeenCalledWith({ type: 'RESTART_LOADING' })
    })
  })
})

