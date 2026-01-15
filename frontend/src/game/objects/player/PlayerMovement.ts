/**
 * PlayerMovement - 玩家移动逻辑
 * 负责玩家的移动、路径跟随和输入处理
 */
import Phaser from 'phaser'
import type { Direction } from '@/types'
import { PathPredictor } from './PathPredictor'
import { InputHandler } from './InputHandler'
import type { InputManager } from '@/game/managers/InputManager'

/**
 * 玩家移动管理器
 */
export class PlayerMovement {
  private player: Phaser.Physics.Arcade.Sprite
  private scene: Phaser.Scene
  private mapOffset: { x: number; y: number; tileSize: number } | null = null
  private target: { x: number; y: number }
  private moveSpeed: number = 300
  private frameDuration: number = 0
  private canGoNextTile: boolean = false
  private pathPredictor: PathPredictor
  private inputHandler: InputHandler

  constructor(
    player: Phaser.Physics.Arcade.Sprite,
    scene: Phaser.Scene,
    target: { x: number; y: number },
    mapOffset: { x: number; y: number; tileSize: number } | null,
    inputManager: InputManager | null
  ) {
    this.player = player
    this.scene = scene
    this.target = target
    this.mapOffset = mapOffset
    this.pathPredictor = new PathPredictor(mapOffset)
    this.inputHandler = new InputHandler(inputManager, this.pathPredictor)
    if (mapOffset) {
      this.frameDuration = this.moveSpeed / mapOffset.tileSize
    }
  }

  /**
   * 设置地图偏移量
   */
  setMapOffset(mapOffset: { x: number; y: number; tileSize: number } | null): void {
    this.mapOffset = mapOffset
    this.pathPredictor.setMapOffset(mapOffset)
    if (mapOffset) {
      this.frameDuration = this.moveSpeed / mapOffset.tileSize
    }
  }

  /**
   * 设置远程控制
   */
  setRemoteControl(remoteControl: Direction | null): void {
    if (!this.mapOffset) {
      this.inputHandler.setRemoteControl(remoteControl)
      return
    }
    
    const EPSILON = 0.1
    const atTarget = Math.abs(this.target.x - this.player.x) < EPSILON && 
                     Math.abs(this.target.y - this.player.y) < EPSILON
    
    // 如果玩家还在移动中（未到达目标）
    if (!atTarget) {
      // 检查是否可以预判继续移动（下一步和再下一步方向相同）
      if (this.pathPredictor.canContinueMoving(this.player.x, this.player.y)) {
        // 可以预判，保持当前指令继续移动
        return
      }
      // 不能预判，忽略新指令，停留在当前格子
      if (this.inputHandler.getRemoteControl() !== null && this.inputHandler.getRemoteControl() !== '') {
        return
      }
    }
    
    // 玩家已到达目标位置，或者当前没有指令，可以接受新指令
    const currentRemoteControl = this.inputHandler.getRemoteControl()
    if (currentRemoteControl !== remoteControl && remoteControl !== null && remoteControl !== '') {
      if (currentRemoteControl !== null && currentRemoteControl !== '') {
        this.target.x = this.player.x
        this.target.y = this.player.y
      }
    }
    this.inputHandler.setRemoteControl(remoteControl)
  }

  /**
   * 设置路径用于预判
   */
  setPlannedPath(path: Array<{ x: number; y: number }> | null): void {
    this.pathPredictor.setPlannedPath(path)
  }

  /**
   * 检查输入并更新目标位置
   */
  checkInput(): void {
    if (!this.mapOffset) return

    const EPSILON = 0.1
    const atTarget = Math.abs(this.target.x - this.player.x) < EPSILON && Math.abs(this.target.y - this.player.y) < EPSILON

    if (this.canGoNextTile && atTarget) {
      this.canGoNextTile = false
      const moveDirection = this.inputHandler.getMoveDirection(this.player.x, this.player.y)

      // 设置下一个目标位置
      const nextPosition = {
        x: this.player.x + (moveDirection.x * this.mapOffset.tileSize),
        y: this.player.y + (moveDirection.y * this.mapOffset.tileSize)
      }

      // 检查是否可以移动到下一个位置
      const sceneWithMap = this.scene as Phaser.Scene & { isWall?: (x: number, y: number) => boolean }
      if (sceneWithMap.isWall && !sceneWithMap.isWall(nextPosition.x, nextPosition.y)) {
        this.target.x = nextPosition.x
        this.target.y = nextPosition.y
      }
    }
  }

  /**
   * 执行移动
   */
  move(): void {
    if (this.player.x < this.target.x) {
      this.player.x++
    } else if (this.player.x > this.target.x) {
      this.player.x--
    }
    
    if (this.player.y < this.target.y) {
      this.player.y++
    } else if (this.player.y > this.target.y) {
      this.player.y--
    }
  }

  /**
   * 设置是否可以移动到下一个格子
   */
  setCanGoNextTile(canGo: boolean): void {
    if (canGo) {
      this.canGoNextTile = true
    }
  }

  /**
   * 获取目标位置
   */
  getTarget(): { x: number; y: number } {
    return this.target
  }

  /**
   * 设置目标位置
   */
  setTarget(x: number, y: number): void {
    this.target.x = x
    this.target.y = y
  }
}
