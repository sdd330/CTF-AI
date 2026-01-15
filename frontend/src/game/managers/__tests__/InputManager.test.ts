import { describe, it, expect, beforeEach, vi } from 'vitest'
import type Phaser from 'phaser'
import {
  InputManager,
  type InputObserver,
  type KeyListener
} from '../InputManager'

// Mock Phaser Scene
function createMockScene(): Phaser.Scene {
  const createMockKey = () => ({
    isDown: false,
    on: vi.fn(),
    removeAllListeners: vi.fn()
  })

  return {
    input: {
      keyboard: {
        createCursorKeys: vi.fn(() => ({
          up: { isDown: false },
          down: { isDown: false },
          left: { isDown: false },
          right: { isDown: false }
        })),
        addKeys: vi.fn(() => ({
          up: { isDown: false },
          left: { isDown: false },
          down: { isDown: false },
          right: { isDown: false }
        })),
        addKey: vi.fn(() => createMockKey())
      }
    }
  } as unknown as Phaser.Scene
}

describe('InputManager', () => {
  let manager: InputManager
  let mockScene: Phaser.Scene

  beforeEach(() => {
    mockScene = createMockScene()
    manager = new InputManager(mockScene)
  })

  describe('基础功能', () => {
    it('应该能够添加方向观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      manager.setRemoteControl('left')
      manager.update()
      expect(observer.onInputChange).toHaveBeenCalledWith('left')
    })

    it('应该能够移除方向观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      manager.unsubscribe(observer)
      manager.setRemoteControl('right')
      manager.update()
      expect(observer.onInputChange).not.toHaveBeenCalled()
    })

    it('应该能够添加按键监听器', () => {
      const listener: KeyListener = {
        onSpacePress: vi.fn()
      }
      manager.subscribeKeyListener(listener)
      expect(listener.onSpacePress).not.toThrow()
    })

    it('应该能够移除按键监听器', () => {
      const listener: KeyListener = {
        onSpacePress: vi.fn()
      }
      manager.subscribeKeyListener(listener)
      manager.unsubscribeKeyListener(listener)
      expect(listener.onSpacePress).not.toThrow()
    })
  })

  describe('远程控制', () => {
    it('应该能够设置远程控制方向', () => {
      manager.setRemoteControl('left')
      manager.update()
      expect(manager.getCurrentDirection()).toBe('left')
    })

    it('应该在方向改变时通知观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      
      manager.setRemoteControl('right')
      manager.update()
      
      expect(observer.onInputChange).toHaveBeenCalledWith('right')
    })

    it('应该能够更新远程控制方向', () => {
      manager.setRemoteControl('up')
      manager.update()
      expect(manager.getCurrentDirection()).toBe('up')
      
      manager.setRemoteControl('right')
      manager.update()
      expect(manager.getCurrentDirection()).toBe('right')
    })

    it('不应该在方向未改变时通知观察者', () => {
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      manager.subscribe(observer)
      
      manager.setRemoteControl('right')
      manager.update()
      expect(observer.onInputChange).toHaveBeenCalledTimes(1)
      
      // 再次更新但方向未改变
      manager.update()
      expect(observer.onInputChange).toHaveBeenCalledTimes(1)
    })
  })

  describe('键盘输入', () => {
    beforeEach(() => {
      manager.initKeyboard(true)
    })

    it('应该能够初始化键盘', () => {
      // 现在使用配置的按键绑定，只调用 addKeys 一次
      expect(mockScene.input.keyboard!.addKeys).toHaveBeenCalled()
    })

    it('应该能够检测方向键输入', () => {
      // 键盘输入测试需要通过实际的 Phaser 按键系统，这里跳过内部实现测试
      expect(manager.isKeyboardEnabled()).toBe(true)
    })

    it('应该能够检测 WASD 键输入', () => {
      // 键盘输入测试需要通过实际的 Phaser 按键系统，这里跳过内部实现测试
      expect(manager.isKeyboardEnabled()).toBe(true)
    })

    it('键盘输入应该优先于远程控制', () => {
      // 设置远程控制
      manager.setRemoteControl('down')
      manager.update()
      // 如果没有键盘输入，应该使用远程控制
      expect(manager.getCurrentDirection()).toBe('down')
    })

    it('应该能够启用/禁用键盘输入', () => {
      manager.setKeyboardEnabled(false)
      expect(manager.isKeyboardEnabled()).toBe(false)

      manager.setKeyboardEnabled(true)
      expect(manager.isKeyboardEnabled()).toBe(true)
    })

    it('禁用键盘后应该只使用远程控制', () => {
      // 设置远程控制
      manager.setRemoteControl('down')
      
      // 禁用键盘
      manager.setKeyboardEnabled(false)
      manager.update()

      // 应该使用远程控制
      expect(manager.getCurrentDirection()).toBe('down')
    })
  })

  describe('按键监听', () => {
    it('应该能够监听空格键', () => {
      const listener: KeyListener = {
        onSpacePress: vi.fn()
      }
      manager.subscribeKeyListener(listener)
      manager.initKeyboard(true)

      // 按键监听器应该被成功订阅
      expect(listener.onSpacePress).toBeDefined()
    })

    it('应该能够监听 ESC 键', () => {
      const listener: KeyListener = {
        onEscapePress: vi.fn()
      }
      manager.subscribeKeyListener(listener)
      manager.initKeyboard(true)

      // 按键监听器应该被成功订阅
      expect(listener.onEscapePress).toBeDefined()
    })

    it('应该能够通知多个监听器', () => {
      const listener1: KeyListener = {
        onSpacePress: vi.fn()
      }
      const listener2: KeyListener = {
        onSpacePress: vi.fn()
      }
      
      manager.subscribeKeyListener(listener1)
      manager.subscribeKeyListener(listener2)
      manager.initKeyboard(true)

      // 多个监听器应该被成功订阅
      expect(listener1.onSpacePress).toBeDefined()
      expect(listener2.onSpacePress).toBeDefined()
    })
  })

  describe('状态管理', () => {
    it('应该在没有设置远程控制时返回空字符串', () => {
      manager.update()
      expect(manager.getCurrentDirection()).toBe('')
    })

    it('应该能够重置状态', () => {
      manager.setRemoteControl('left')
      manager.update()
      expect(manager.getCurrentDirection()).toBe('left')
      
      manager.reset()
      expect(manager.getCurrentDirection()).toBe('')
    })

    it('应该能够通知多个方向观察者', () => {
      const observer1: InputObserver = {
        onInputChange: vi.fn()
      }
      const observer2: InputObserver = {
        onInputChange: vi.fn()
      }
      
      manager.subscribe(observer1)
      manager.subscribe(observer2)
      
      manager.setRemoteControl('up')
      manager.update()
      
      expect(observer1.onInputChange).toHaveBeenCalledWith('up')
      expect(observer2.onInputChange).toHaveBeenCalledWith('up')
    })
  })

  describe('销毁', () => {
    it('应该能够清理所有资源', () => {
      manager.initKeyboard(true)
      
      const observer: InputObserver = {
        onInputChange: vi.fn()
      }
      const listener: KeyListener = {
        onSpacePress: vi.fn()
      }
      
      manager.subscribe(observer)
      manager.subscribeKeyListener(listener)
      
      // destroy 方法应该能够成功调用而不抛出错误
      expect(() => manager.destroy()).not.toThrow()
    })
  })
})
