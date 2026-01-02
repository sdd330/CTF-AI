import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Boot } from '../Boot'

// Mock Phaser Scene
const createMockScene = () => {
  return {
    scene: {
      start: vi.fn()
    }
  } as unknown as Phaser.Scene
}

describe('Boot', () => {
  let boot: Boot

  beforeEach(() => {
    boot = new Boot()
    const mockScene = createMockScene()
    boot.scene = { ...mockScene.scene, key: 'Boot' } as any
  })

  describe('初始化', () => {
    it('应该正确创建 Boot 场景', () => {
      expect(boot).toBeInstanceOf(Boot)
      expect(boot.scene.key).toBe('Boot')
    })
  })

  describe('preload', () => {
    it('应该能够执行 preload 方法', () => {
      expect(() => boot.preload()).not.toThrow()
    })
  })

  describe('create', () => {
    it('应该启动 Preloader 场景', () => {
      boot.create()
      expect(boot.scene.start).toHaveBeenCalledWith('Preloader')
    })
  })
})

