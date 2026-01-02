/**
 * Vitest 测试设置文件
 * 用于配置测试环境和全局模拟
 */
import { vi } from 'vitest'
import type Phaser from 'phaser'

// Mock Phaser Math.RND
const mockRND = {
  integerInRange: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
  pick: <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)]
}

// Mock Phaser
globalThis.Phaser = {
  Math: {
    RND: mockRND
  },
  Scale: {
    FIT: 'fit',
    CENTER_BOTH: 'center_both'
  },
  AUTO: 'auto',
  Physics: {
    Arcade: {
      Sprite: class MockSprite {
        x = 0
        y = 0
        constructor() {}
      }
    }
  },
  Scene: class MockScene {
    constructor() {}
  },
  Input: {
    Keyboard: {
      KeyCodes: {
        W: 87,
        A: 65,
        S: 83,
        D: 68,
        R: 82,
        L: 76,
        SPACE: 32
      }
    }
  },
  Game: class MockGame {
    registry = {
      set: vi.fn(),
      get: vi.fn(),
      remove: vi.fn(),
      exists: vi.fn(),
      has: vi.fn(() => false)
    }
  }
} as unknown as typeof Phaser

// Mock WebSocket
globalThis.WebSocket = class MockWebSocket {
  readyState = WebSocket.OPEN
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  bufferedAmount = 0

  send(_data: string) {
    // Mock send
  }

  close() {
    // Mock close
  }
} as unknown as typeof WebSocket

// Mock phaser3spectorjs (Phaser 的可选依赖，用于 WebGL 调试)
// 使用 vi.mock 在模块加载时拦截
vi.mock('phaser3spectorjs', () => ({}))

