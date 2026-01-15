/**
 * 输入观察者管理器
 * 负责管理输入观察者的注册和通知
 */
import type { Direction } from '@/types'

export interface InputObserver {
  onInputChange(direction: Direction): void
}

export class InputObserverManager {
  private observers: Set<InputObserver> = new Set()
  private currentDirection: Direction = ''

  subscribe(observer: InputObserver): void {
    this.observers.add(observer)
  }

  unsubscribe(observer: InputObserver): void {
    this.observers.delete(observer)
  }

  notifyIfChanged(newDirection: Direction): void {
    if (newDirection !== this.currentDirection) {
      this.currentDirection = newDirection
      this.observers.forEach(observer => {
        observer.onInputChange(newDirection)
      })
    }
  }

  getCurrentDirection(): Direction {
    return this.currentDirection
  }

  reset(): void {
    this.currentDirection = ''
  }

  destroy(): void {
    this.observers.clear()
  }
}
