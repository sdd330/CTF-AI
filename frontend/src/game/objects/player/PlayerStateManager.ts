/**
 * PlayerStateManager - 玩家状态管理器
 * 负责管理玩家的状态（监狱、旗帜等）
 */
import type { PlayerStatus } from '@/types'

/**
 * 玩家状态管理器
 */
export class PlayerStateManager {
  private name: string
  private team: string
  private inPrison: boolean = false
  private inPrisonTimeLeft: number = 0
  private inPrisonDuration: number = 20000
  private hasFlag: boolean = false

  constructor(name: string, team: string) {
    this.name = name
    this.team = team
  }

  /**
   * 收集旗帜
   */
  collectFlag(): void {
    this.hasFlag = true
  }

  /**
   * 掉落旗帜
   */
  dropFlag(): void {
    this.hasFlag = false
  }

  /**
   * 进入监狱
   */
  toPrison(): void {
    this.inPrison = true
    this.inPrisonTimeLeft = this.inPrisonDuration
  }

  /**
   * 从监狱释放
   */
  freeFromPrison(): void {
    this.inPrison = false
    this.inPrisonTimeLeft = 0
  }

  /**
   * 更新监狱时间
   */
  updatePrisonTime(delta: number): void {
    if (this.inPrison) {
      this.inPrisonTimeLeft -= delta
      if (this.inPrisonTimeLeft <= 0) {
        this.inPrison = false
        this.inPrisonTimeLeft = 0
      }
    }
  }

  /**
   * 获取状态
   */
  getStatus(mapOffset: { x: number; y: number; tileSize: number } | null, targetX: number, targetY: number): PlayerStatus {
    if (!mapOffset) {
      return {
        name: this.name,
        team: this.team as 'L' | 'R',
        posX: 0,
        posY: 0,
        hasFlag: this.hasFlag,
        inPrison: this.inPrison,
        inPrisonTimeLeft: this.inPrisonTimeLeft,
        inPrisonDuration: this.inPrisonDuration
      }
    }

    const targetPosX = Math.round((targetX - mapOffset.x) / mapOffset.tileSize)
    const targetPosY = Math.round((targetY - mapOffset.y) / mapOffset.tileSize)

    return {
      name: this.name,
      team: this.team as 'L' | 'R',
      posX: targetPosX,
      posY: targetPosY,
      hasFlag: this.hasFlag,
      inPrison: this.inPrison,
      inPrisonTimeLeft: this.inPrisonTimeLeft,
      inPrisonDuration: this.inPrisonDuration
    }
  }

  /**
   * 获取是否有旗帜
   */
  getHasFlag(): boolean {
    return this.hasFlag
  }

  /**
   * 获取是否在监狱
   */
  getInPrison(): boolean {
    return this.inPrison
  }

  /**
   * 设置监狱时间剩余
   */
  setInPrisonTimeLeft(time: number): void {
    this.inPrisonTimeLeft = time
  }
}
