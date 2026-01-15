/**
 * SocketManager 单元测试
 * 
 * 测试策略：
 * - 单元测试：只测试基本功能（连接、断开、事件订阅）
 * - E2E 测试：测试复杂场景（消息流、重连、超时、完整游戏流程）
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { SocketManager, SocketEvent } from '../SocketManager'

// Mock WebSocket - 简单同步版本
class MockWebSocket {
  readyState: number = WebSocket.OPEN as number
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  bufferedAmount = 0

  constructor(public url: string) {
    queueMicrotask(() => {
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    })
  }

  send(data: string) {
    // Mock send
  }

  close() {
    this.readyState = WebSocket.CLOSED as number
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }
}

// 替换全局 WebSocket
const originalWebSocket = globalThis.WebSocket
beforeEach(() => {
  globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket
})

afterEach(() => {
  globalThis.WebSocket = originalWebSocket
  SocketManager.getInstance().disconnectAll()
})

describe('SocketManager - 基本功能', () => {
  describe('单例模式', () => {
    it('应该返回同一个实例', () => {
      const instance1 = SocketManager.getInstance()
      const instance2 = SocketManager.getInstance()
      expect(instance1).toBe(instance2)
    })
  })

  describe('连接管理', () => {
    it('应该能够连接队伍', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      expect(manager.isConnected('L')).toBe(true)
    })

    it('应该能够断开连接', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      manager.disconnectTeam('L')
      expect(manager.isConnected('L')).toBe(false)
    })

    it('应该能够同时管理多个连接', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      manager.connectTeam('R', 'ws://localhost:8081')
      
      await Promise.resolve()
      expect(manager.isConnected('L')).toBe(true)
      expect(manager.isConnected('R')).toBe(true)
    })

    it('应该能够断开所有连接', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      manager.connectTeam('R', 'ws://localhost:8081')
      
      await Promise.resolve()
      manager.disconnectAll()
      expect(manager.isConnected('L')).toBe(false)
      expect(manager.isConnected('R')).toBe(false)
    })
  })

  describe('事件订阅', () => {
    it('应该能够订阅连接事件', async () => {
      const manager = SocketManager.getInstance()
      const listener = vi.fn()
      
      manager.on(SocketEvent.CONNECT, listener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      expect(listener).toHaveBeenCalledWith('L')
    })

    it('应该能够取消订阅事件', async () => {
      const manager = SocketManager.getInstance()
      const listener = vi.fn()
      
      manager.on(SocketEvent.CONNECT, listener)
      manager.off(SocketEvent.CONNECT, listener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      expect(listener).not.toHaveBeenCalled()
    })

    it('应该能够订阅断开连接事件', async () => {
      const manager = SocketManager.getInstance()
      const listener = vi.fn()
      
      manager.on(SocketEvent.DISCONNECT, listener)
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      manager.disconnectTeam('L')
      
      expect(listener).toHaveBeenCalledWith('L')
    })
  })

  describe('连接状态查询', () => {
    it('应该正确返回连接状态', async () => {
      const manager = SocketManager.getInstance()
      manager.connectTeam('L', 'ws://localhost:8080')
      
      await Promise.resolve()
      const status = manager.getConnectionStatus()
      expect(status.L).toBe(true)
      expect(status.R).toBe(false)
    })

    it('应该正确检查单个队伍的连接状态', async () => {
      const manager = SocketManager.getInstance()
      
      expect(manager.isConnected('L')).toBe(false)
      
      manager.connectTeam('L', 'ws://localhost:8080')
      await Promise.resolve()
      
      expect(manager.isConnected('L')).toBe(true)
    })
  })
})
