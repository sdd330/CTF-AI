/**
 * PathPredictor - 路径预判器
 * 负责路径预判逻辑
 */
import type { Direction } from '@/types'

/**
 * 路径预判器
 */
export class PathPredictor {
  private mapOffset: { x: number; y: number; tileSize: number } | null
  private plannedPath: Array<{ x: number; y: number }> | null = null
  private remoteControl: Direction | null = null

  constructor(mapOffset: { x: number; y: number; tileSize: number } | null) {
    this.mapOffset = mapOffset
  }

  /**
   * 设置地图偏移量
   */
  setMapOffset(mapOffset: { x: number; y: number; tileSize: number } | null): void {
    this.mapOffset = mapOffset
  }

  /**
   * 设置路径
   */
  setPlannedPath(path: Array<{ x: number; y: number }> | null): void {
    this.plannedPath = path
  }

  /**
   * 设置远程控制
   */
  setRemoteControl(remoteControl: Direction | null): void {
    this.remoteControl = remoteControl
  }

  /**
   * 从路径计算方向
   */
  private calculateDirectionFromPath(currentPos: { x: number; y: number }, nextPos: { x: number; y: number }): Direction | null {
    if (!this.mapOffset) return null
    
    const dx = nextPos.x - currentPos.x
    const dy = nextPos.y - currentPos.y
    
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? 'right' : 'left'
    } else if (Math.abs(dy) > Math.abs(dx)) {
      return dy > 0 ? 'down' : 'up'
    }
    return null
  }

  /**
   * 检查路径中是否有连续相同的方向（预判）
   */
  canContinueMoving(currentX: number, currentY: number): boolean {
    if (!this.mapOffset || !this.plannedPath || this.plannedPath.length < 3) {
      return false
    }
    
    const EPSILON = 0.1
    const currentTileX = Math.round((currentX - this.mapOffset.x) / this.mapOffset.tileSize)
    const currentTileY = Math.round((currentY - this.mapOffset.y) / this.mapOffset.tileSize)
    
    // 找到当前玩家在路径中的位置
    let currentIndex = -1
    for (let i = 0; i < this.plannedPath.length; i++) {
      const pathPos = this.plannedPath[i]
      if (Math.abs(pathPos.x - currentTileX) < EPSILON && Math.abs(pathPos.y - currentTileY) < EPSILON) {
        currentIndex = i
        break
      }
    }
    
    // 如果找不到当前位置，或者已经接近路径末尾，不预判
    if (currentIndex < 0 || currentIndex >= this.plannedPath.length - 2) {
      return false
    }
    
    // 检查下一步和再下一步的方向是否相同
    const nextPos = this.plannedPath[currentIndex + 1]
    const nextNextPos = this.plannedPath[currentIndex + 2]
    
    const currentPos = { x: currentTileX, y: currentTileY }
    const nextDir = this.calculateDirectionFromPath(currentPos, nextPos)
    const nextNextDir = this.calculateDirectionFromPath(nextPos, nextNextPos)
    
    // 如果下一步和再下一步方向相同，且与当前指令方向相同，可以继续移动
    return nextDir !== null && nextDir === nextNextDir && nextDir === this.remoteControl
  }
}
