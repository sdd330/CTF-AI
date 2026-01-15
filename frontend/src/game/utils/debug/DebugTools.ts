/**
 * 调试工具类
 * 提供统一的调试功能接口
 */
import type { DebugInfo } from '@/types'
import { WorldManager } from '../../managers/WorldManager'
import { PerformanceMonitor } from './PerformanceMonitor'
import { Logger } from './Logger'

export class DebugTools {
  private static performanceMonitor: PerformanceMonitor | null = null
  private static logger: Logger | null = null

  static init(): void {
    this.performanceMonitor = new PerformanceMonitor()
    this.logger = Logger.getInstance()
    
    if (import.meta.env.DEV) {
      this.logger.setLevel('debug')
    }
  }

  static getPerformanceMonitor(): PerformanceMonitor {
    if (!this.performanceMonitor) {
      this.init()
    }
    return this.performanceMonitor!
  }

  static getLogger(): Logger {
    if (!this.logger) {
      this.init()
    }
    return this.logger!
  }

  static getDebugInfo(): DebugInfo {
    const world = WorldManager.getInstance()
    const perfMonitor = this.getPerformanceMonitor()
    
    return {
      ...world.api.getDebugInfo(),
      performance: perfMonitor.getMetrics()
    }
  }

  static printDebugInfo(): void {
    const info = this.getDebugInfo()
    console.group('🔍 调试信息')
    console.log('游戏状态:', info.gameState)
    console.log('玩家数量:', info.players)
    console.log('旗帜数量:', info.flags)
    console.log('连接状态:', info.connections)
    if (info.performance) {
      console.log('性能指标:', {
        FPS: info.performance.fps.toFixed(1),
        '平均帧时间': `${info.performance.frameTime.toFixed(2)}ms`
      })
    }
    console.groupEnd()
  }
}
