/**
 * 日志管理器
 * 提供分级日志系统
 */
import type { LogLevel } from '@/types'

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

  setLevel(level: LogLevel): void {
    this.logLevel = level
  }

  log(level: LogLevel, message: string, data?: unknown): void {
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error']
    const currentLevelIndex = levels.indexOf(this.logLevel)
    const messageLevelIndex = levels.indexOf(level)

    if (messageLevelIndex < currentLevelIndex) {
      return
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

  getRecentLogs(count: number = 100): typeof this.logs {
    return this.logs.slice(-count)
  }

  clear(): void {
    this.logs = []
  }
}
