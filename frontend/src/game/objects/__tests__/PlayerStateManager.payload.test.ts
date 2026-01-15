/**
 * PlayerStateManager Payload 测试
 * 确保 getStatus 返回的坐标是整数
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { PlayerStateManager } from '../player/PlayerStateManager'
import type { PlayerStatus } from '@/types'

describe('PlayerStateManager - 坐标格式', () => {
  let stateManager: PlayerStateManager

  beforeEach(() => {
    stateManager = new PlayerStateManager('L0', 'L', 20000)
  })

  describe('getStatus 坐标类型', () => {
    it('应该返回整数坐标（不是浮点数）', () => {
      const mapOffset = { x: 100, y: 100, tileSize: 32 }
      
      // 玩家在网格 (5, 10)
      const targetX = mapOffset.x + 5 * mapOffset.tileSize  // 260
      const targetY = mapOffset.y + 10 * mapOffset.tileSize // 420
      
      const status = stateManager.getStatus(mapOffset, targetX, targetY)
      
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(10)
      
      // 验证是整数
      expect(Number.isInteger(status.posX)).toBe(true)
      expect(Number.isInteger(status.posY)).toBe(true)
    })

    it('应该正确处理有小数误差的像素坐标', () => {
      const mapOffset = { x: 100, y: 100, tileSize: 32 }
      
      // 模拟浮点数精度误差：应该是 260，但可能是 259.99999
      const targetX = mapOffset.x + 5 * mapOffset.tileSize - 0.001
      const targetY = mapOffset.y + 10 * mapOffset.tileSize + 0.001
      
      const status = stateManager.getStatus(mapOffset, targetX, targetY)
      
      // Math.round 应该正确处理
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(10)
    })

    it('所有 PlayerStatus 字段的坐标都应该是整数', () => {
      const mapOffset = { x: 100, y: 100, tileSize: 32 }
      const targetX = mapOffset.x + 7 * mapOffset.tileSize
      const targetY = mapOffset.y + 15 * mapOffset.tileSize
      
      const status: PlayerStatus = stateManager.getStatus(mapOffset, targetX, targetY)
      
      // 验证所有数值字段
      expect(Number.isInteger(status.posX)).toBe(true)
      expect(Number.isInteger(status.posY)).toBe(true)
      expect(typeof status.inPrisonTimeLeft).toBe('number')
      expect(typeof status.inPrisonDuration).toBe('number')
      
      // 验证字段值
      expect(status.posX).toBe(7)
      expect(status.posY).toBe(15)
      expect(status.name).toBe('L0')
      expect(status.team).toBe('L')
    })

    it('序列化为 JSON 后坐标仍然是整数格式', () => {
      const mapOffset = { x: 100, y: 100, tileSize: 32 }
      const targetX = mapOffset.x + 5 * mapOffset.tileSize
      const targetY = mapOffset.y + 10 * mapOffset.tileSize
      
      const status = stateManager.getStatus(mapOffset, targetX, targetY)
      
      // 序列化为 JSON
      const jsonString = JSON.stringify(status)
      const parsed = JSON.parse(jsonString)
      
      // 验证反序列化后仍然是正确的整数
      expect(parsed.posX).toBe(5)
      expect(parsed.posY).toBe(10)
      expect(Number.isInteger(parsed.posX)).toBe(true)
      expect(Number.isInteger(parsed.posY)).toBe(true)
      
      // 验证 JSON 字符串中是整数格式（不是 "5.0"）
      expect(jsonString).toContain('"posX":5')
      expect(jsonString).toContain('"posY":10')
      expect(jsonString).not.toContain('"posX":5.0')
      expect(jsonString).not.toContain('"posY":10.0')
    })

    it('边界情况：mapOffset 为 null', () => {
      const status = stateManager.getStatus(null, 0, 0)
      
      expect(status.posX).toBe(0)
      expect(status.posY).toBe(0)
      expect(Number.isInteger(status.posX)).toBe(true)
      expect(Number.isInteger(status.posY)).toBe(true)
    })
  })

  describe('坐标计算精度', () => {
    it('应该使用 target 位置而不是当前像素位置', () => {
      const mapOffset = { x: 100, y: 100, tileSize: 32 }
      
      // target 在网格 (5, 10) 的左上角
      const targetX = mapOffset.x + 5 * mapOffset.tileSize  // 260
      const targetY = mapOffset.y + 10 * mapOffset.tileSize // 420
      
      const status = stateManager.getStatus(mapOffset, targetX, targetY)
      
      // 应该报告网格坐标 (5, 10)，不是像素坐标 (260, 420)
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(10)
    })

    it('不同 tileSize 的坐标转换', () => {
      // tileSize = 16
      let mapOffset = { x: 0, y: 0, tileSize: 16 }
      let targetX = 5 * 16  // 80
      let targetY = 10 * 16 // 160
      let status = stateManager.getStatus(mapOffset, targetX, targetY)
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(10)
      
      // tileSize = 64
      mapOffset = { x: 0, y: 0, tileSize: 64 }
      targetX = 5 * 64  // 320
      targetY = 10 * 64 // 640
      status = stateManager.getStatus(mapOffset, targetX, targetY)
      expect(status.posX).toBe(5)
      expect(status.posY).toBe(10)
    })
  })
})
