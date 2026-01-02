/**
 * 调试工具模块
 * 提供性能监控、日志记录等调试功能
 */
import type { PerformanceMetrics, DebugInfo, LogLevel } from '@/types'
import { GameStateManager } from '../managers/GameStateManager'

/**
 * 性能监控器
 */
export class PerformanceMonitor {
  private frameCount = 0
  private lastFpsTime = 0
  private fps = 0
  private frameTimes: number[] = []
  private maxFrameTimeHistory = 60

  /**
   * 记录一帧
   */
  tick(): void {
    this.frameCount++
    const now = performance.now()
    
    if (this.lastFpsTime === 0) {
      this.lastFpsTime = now
      return
    }

    const frameTime = now - this.lastFpsTime
    this.frameTimes.push(frameTime)
    
    if (this.frameTimes.length > this.maxFrameTimeHistory) {
      this.frameTimes.shift()
    }

    // 每秒更新一次 FPS
    if (now - this.lastFpsTime >= 1000) {
      this.fps = this.frameCount
      this.frameCount = 0
      this.lastFpsTime = now
    }
  }

  /**
   * 获取性能指标
   */
  getMetrics(): PerformanceMetrics {
    const avgFrameTime = this.frameTimes.length > 0
      ? this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length
      : 0

    return {
      fps: this.fps,
      frameTime: avgFrameTime,
      renderTime: 0, // 需要在实际渲染时记录
      updateTime: 0  // 需要在实际更新时记录
    }
  }

  /**
   * 重置监控器
   */
  reset(): void {
    this.frameCount = 0
    this.lastFpsTime = 0
    this.fps = 0
    this.frameTimes = []
  }
}

/**
 * 日志管理器（分级日志系统）
 */
export class Logger {
  private static instance: Logger | null = null
  private logLevel: LogLevel = 'info'
  private logs: Array<{ level: LogLevel; message: string; timestamp: Date; data?: unknown }> = []
  private maxLogs = 1000

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  /**
   * 设置日志级别
   */
  setLevel(level: LogLevel): void {
    this.logLevel = level
  }

  /**
   * 记录日志
   */
  log(level: LogLevel, message: string, data?: unknown): void {
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error']
    const currentLevelIndex = levels.indexOf(this.logLevel)
    const messageLevelIndex = levels.indexOf(level)

    if (messageLevelIndex < currentLevelIndex) {
      return // 低于当前日志级别，不记录
    }

    const logEntry = {
      level,
      message,
      timestamp: new Date(),
      data
    }

    this.logs.push(logEntry)
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // 输出到控制台
    const prefix = `[Logger:${level.toUpperCase()}]`
    switch (level) {
      case 'debug':
        console.debug(prefix, message, data || '')
        break
      case 'info':
        console.info(prefix, message, data || '')
        break
      case 'warn':
        console.warn(prefix, message, data || '')
        break
      case 'error':
        console.error(prefix, message, data || '')
        break
    }
  }

  /**
   * 获取最近的日志
   */
  getRecentLogs(count: number = 100): typeof this.logs {
    return this.logs.slice(-count)
  }

  /**
   * 清空日志
   */
  clear(): void {
    this.logs = []
  }
}

/**
 * 调试工具类
 */
export class DebugTools {
  private static performanceMonitor: PerformanceMonitor | null = null
  private static logger: Logger | null = null

  /**
   * 初始化调试工具
   */
  static init(): void {
    this.performanceMonitor = new PerformanceMonitor()
    this.logger = Logger.getInstance()
    
    // 在开发环境下启用调试日志
    if (process.env.NODE_ENV === 'development') {
      this.logger.setLevel('debug')
    }
  }

  /**
   * 获取性能监控器
   */
  static getPerformanceMonitor(): PerformanceMonitor {
    if (!this.performanceMonitor) {
      this.init()
    }
    return this.performanceMonitor!
  }

  /**
   * 获取日志管理器
   */
  static getLogger(): Logger {
    if (!this.logger) {
      this.init()
    }
    return this.logger!
  }

  /**
   * 获取完整的调试信息
   */
  static getDebugInfo(): DebugInfo {
    const gameState = GameStateManager.getInstance()
    const perfMonitor = this.getPerformanceMonitor()
    
    return {
      ...gameState.getDebugInfo(),
      performance: perfMonitor.getMetrics()
    }
  }

  /**
   * 在控制台输出调试信息
   */
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
