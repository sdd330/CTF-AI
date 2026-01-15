/**
 * InputHandler - 输入处理器
 * 负责处理键盘输入和远程控制输入
 * 现在通过 InputManager 统一管理输入
 */
import type { Direction } from '@/types'
import { PlayerDirection } from '../Player'
import { PathPredictor } from './PathPredictor'
import type { InputManager } from '@/game/managers/InputManager'

/**
 * 输入处理器
 */
export class InputHandler {
  private inputManager: InputManager | null = null
  private remoteControl: Direction | null = null
  private pathPredictor: PathPredictor

  constructor(
    inputManager: InputManager | null,
    pathPredictor: PathPredictor
  ) {
    this.inputManager = inputManager
    this.pathPredictor = pathPredictor
  }

  /**
   * 设置远程控制
   */
  setRemoteControl(remoteControl: Direction | null): void {
    this.remoteControl = remoteControl
    this.pathPredictor.setRemoteControl(remoteControl)
    
    // 同时更新 InputManager 的远程控制
    if (this.inputManager) {
      this.inputManager.setRemoteControl(remoteControl || '')
    }
  }

  /**
   * 获取移动方向
   */
  getMoveDirection(currentX: number, currentY: number): { x: number; y: number } {
    const moveDirection = { x: 0, y: 0 }

    // 从 InputManager 获取当前方向（已经处理了键盘和远程控制的优先级）
    let direction: Direction = ''
    
    if (this.inputManager) {
      // InputManager 已经处理了优先级：远程控制 > 键盘输入
      direction = this.inputManager.getCurrentDirection()
    } else {
      // 如果没有 InputManager，回退到使用 remoteControl
      direction = this.remoteControl || ''
    }

    // 根据方向设置移动
    if (direction === PlayerDirection.LEFT) {
      moveDirection.x--
      if (!this.pathPredictor.canContinueMoving(currentX, currentY)) {
        this.remoteControl = null
        this.pathPredictor.setRemoteControl(null)
        if (this.inputManager) {
          this.inputManager.setRemoteControl('')
        }
      }
    } else if (direction === PlayerDirection.RIGHT) {
      moveDirection.x++
      if (!this.pathPredictor.canContinueMoving(currentX, currentY)) {
        this.remoteControl = null
        this.pathPredictor.setRemoteControl(null)
        if (this.inputManager) {
          this.inputManager.setRemoteControl('')
        }
      }
    } else if (direction === PlayerDirection.UP) {
      moveDirection.y--
      if (!this.pathPredictor.canContinueMoving(currentX, currentY)) {
        this.remoteControl = null
        this.pathPredictor.setRemoteControl(null)
        if (this.inputManager) {
          this.inputManager.setRemoteControl('')
        }
      }
    } else if (direction === PlayerDirection.DOWN) {
      moveDirection.y++
      if (!this.pathPredictor.canContinueMoving(currentX, currentY)) {
        this.remoteControl = null
        this.pathPredictor.setRemoteControl(null)
        if (this.inputManager) {
          this.inputManager.setRemoteControl('')
        }
      }
    }

    return moveDirection
  }

  /**
   * 获取远程控制
   */
  getRemoteControl(): Direction | null {
    return this.remoteControl
  }
}
