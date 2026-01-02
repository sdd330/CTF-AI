import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  InputManager,
  KeyboardInputStrategy,
  RemoteInputStrategy,
  HybridInputStrategy,
  type InputObserver
} from '../InputManager'
import { GameStateManager } from '../GameStateManager'
import type { Direction } from '@/types'

// Mock Phaser Scene
const createMockScene = () => {
  const mockSpaceKey = {
    isDown: false,
    on: vi.fn()
  }
  const mockKeys = {
    left: { isDown: false },
    right: { isDown: false },
    up: { isDown: false },
    down: { isDown: false },
    space: mockSpaceKey
  }

  return {
    input: {
      keyboard: {
        createCursorKeys: vi.fn(() => mockKeys),
        addKeys: vi.fn(() => mockKeys),
        addKey: vi.fn((code: number) => {
          if (code === 32) { // SPACE
            return mockSpaceKey
          }
          return {
            isDown: false,
            on: vi.fn()
          }
        })
      }
    },
    game: {
      canvas: {
        tabIndex: 0,
        style: {
          outline: 'none'
        },
        addEventListener: vi.fn()
      }
    }
  } as unknown as Phaser.Scene
}

describe('InputManager', () => {
  describe('KeyboardInputStrategy', () => {
    it('应该返回正确的方向', () => {
      const mockKeys = {
        left: { isDown: true },
        right: { isDown: false },
        up: { isDown: false },
        down: { isDown: false }
      }
      const strategy = new KeyboardInputStrategy(mockKeys as any)
      expect(strategy.getDirection()).toBe('left')
    })

    it('应该优先返回左方向', () => {
      const mockKeys = {
        left: { isDown: true },
        right: { isDown: true },
        up: { isDown: false },
        down: { isDown: false }
      }
      const strategy = new KeyboardInputStrategy(mockKeys as any)
      expect(strategy.getDirection()).toBe('left')
    })

    it('应该在没有按键时返回空字符串', () => {
      const mockKeys = {
        left: { isDown: false },
        right: { isDown: false },
        up: { isDown: false },
        down: { isDown: false }
      }
      const strategy = new KeyboardInputStrategy(mockKeys as any)
      expect(strategy.getDirection()).toBe('')
    })
  })

  describe('RemoteInputStrategy', () => {
    it('应该返回设置的远程控制方向', () => {
      const strategy = new RemoteInputStrategy()
      strategy.setRemoteControl('right')
      expect(strategy.getDirection()).toBe('right')
    })

    it('应该在未设置时返回空字符串', () => {
      const strategy = new RemoteInputStrategy()
      expect(strategy.getDirection()).toBe('')
    })

    it('应该能够更新远程控制方向', () => {
      const strategy = new RemoteInputStrategy()
      strategy.setRemoteControl('up')
      expect(strategy.getDirection()).toBe('up')
      strategy.setRemoteControl('down')
      expect(strategy.getDirection()).toBe('down')
    })
  })

  describe('HybridInputStrategy', () => {
    it('应该优先返回键盘输入', () => {
      const mockKeys = {
        left: { isDown: true },
        right: { isDown: false },
        up: { isDown: false },
        down: { isDown: false }
      }
      const keyboardStrategy = new KeyboardInputStrategy(mockKeys as any)
      const remoteStrategy = new RemoteInputStrategy()
      remoteStrategy.setRemoteControl('right')
      
      const hybridStrategy = new HybridInputStrategy(keyboardStrategy, remoteStrategy)
      expect(hybridStrategy.getDirection()).toBe('left')
    })

    it('应该在键盘未按下时返回远程控制方向', () => {
      const mockKeys = {
        left: { isDown: false },
        right: { isDown: false },
        up: { isDown: false },
        down: { isDown: false }
      }
      const keyboardStrategy = new KeyboardInputStrategy(mockKeys as any)
      const remoteStrategy = new RemoteInputStrategy()
      remoteStrategy.setRemoteControl('up')
      
      const hybridStrategy = new HybridInputStrategy(keyboardStrategy, remoteStrategy)
      expect(hybridStrategy.getDirection()).toBe('up')
    })
  })

  describe('InputManager', () => {
    let manager: InputManager
    let mockStrategy: RemoteInputStrategy

    beforeEach(() => {
      mockStrategy = new RemoteInputStrategy()
      manager = new InputManager(mockStrategy)
    })

    it('应该能够添加观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      expect(manager['observers'].has(observer)).toBe(true)
    })

    it('应该能够移除观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      manager.unsubscribe(observer)
      expect(manager['observers'].has(observer)).toBe(false)
    })

    it('应该在方向改变时通知观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      
      mockStrategy.setRemoteControl('right')
      manager.update(0, 0)
      
      expect(observer.onInputChange).toHaveBeenCalledWith('right')
    })

    it('应该能够设置远程控制', () => {
      manager.setRemoteControl('left')
      expect(mockStrategy.getDirection()).toBe('left')
    })

    it('应该能够获取当前方向', () => {
      mockStrategy.setRemoteControl('down')
      manager.update(0, 0)
      expect(manager.getCurrentDirection()).toBe('down')
    })

    it('应该能够初始化游戏控制', () => {
      const scene = createMockScene()
      const gameStartCallback = vi.fn()
      
      // 初始化 GameStateManager（InputManager 需要）
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
        },
        canvas: {
          tabIndex: 0
        }
      } as unknown as Phaser.Game
      
      const gsManager = GameStateManager as any
      gsManager.instance = null
      GameStateManager.initialize(mockGame)
      
      manager.initialize(scene, gameStartCallback)
      
      // 验证键盘事件监听器已设置
      const keyboard = scene.input.keyboard
      if (keyboard) {
        // 验证 addKey 被调用（用于空格键）
        expect(keyboard.addKey).toHaveBeenCalledWith(32) // SPACE key code
      } else {
        throw new Error('Keyboard should not be null')
      }
    })
  })
})

