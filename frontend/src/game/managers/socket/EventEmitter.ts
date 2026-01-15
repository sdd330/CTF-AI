/**
 * EventEmitter - 事件发射器
 * 实现发布订阅模式
 */
import { SocketEvent } from '../SocketManager'

// 事件监听器类型
type EventListener = (...args: unknown[]) => void

/**
 * 事件发射器（发布订阅模式）
 */
export class EventEmitter {
  private events: Map<SocketEvent, Set<EventListener>> = new Map()

  /**
   * 订阅事件
   */
  on(event: SocketEvent, listener: EventListener): void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set())
    }
    this.events.get(event)!.add(listener)
    console.log(`[EventEmitter] ✅ 订阅事件: ${event}, 当前监听器数: ${this.events.get(event)!.size}`)
  }

  /**
   * 取消订阅
   */
  off(event: SocketEvent, listener: EventListener): void {
    const listeners = this.events.get(event)
    if (listeners) {
      listeners.delete(listener)
    }
  }

  /**
   * 发布事件
   */
  emit(event: SocketEvent, ...args: unknown[]): void {
    const listeners = this.events.get(event)
    if (listeners && listeners.size > 0) {
      console.log(`[EventEmitter] 📤 发布事件: ${event}, 监听器数量: ${listeners.size}`)
      listeners.forEach(listener => {
        try {
          listener(...args)
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error)
        }
      })
    } else {
      console.warn(`[EventEmitter] ⚠️ 没有监听器订阅事件: ${event}`)
    }
  }

  /**
   * 清除所有监听器
   */
  removeAllListeners(event?: SocketEvent): void {
    if (event) {
      this.events.delete(event)
    } else {
      this.events.clear()
    }
  }
}
