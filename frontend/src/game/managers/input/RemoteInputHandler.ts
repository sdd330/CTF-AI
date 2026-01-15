/**
 * 远程输入处理器
 * 负责管理远程控制方向
 */
import type { Direction } from '@/types'

export class RemoteInputHandler {
  private remoteDirection: Direction = ''

  setDirection(direction: Direction): void {
    this.remoteDirection = direction
  }

  getDirection(): Direction {
    return this.remoteDirection
  }

  reset(): void {
    this.remoteDirection = ''
  }
}
