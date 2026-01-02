/**
 * PathVisualizationManager - 路径可视化管理器
 * 负责在前端可视化路径规划的路线
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import { MapManager } from './MapManager'

export interface PathVisualization {
  playerName: string
  path: Position[]
  color: number
  graphics: Phaser.GameObjects.Graphics | null
}

export class PathVisualizationManager {
  private static instance: PathVisualizationManager | null = null
  private scene: Phaser.Scene | null = null
  private paths: Map<string, PathVisualization> = new Map()
  private enabled: boolean = false

  private constructor() {}

  static getInstance(): PathVisualizationManager {
    if (!PathVisualizationManager.instance) {
      PathVisualizationManager.instance = new PathVisualizationManager()
    }
    return PathVisualizationManager.instance
  }

  /**
   * 初始化路径可视化管理器
   */
  initialize(scene: Phaser.Scene): void {
    this.scene = scene
    this.enabled = true
  }

  /**
   * 设置是否启用路径可视化
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled
    if (!enabled) {
      this.clearAllPaths()
    }
  }

  /**
   * 是否启用路径可视化
   */
  isEnabled(): boolean {
    return this.enabled
  }

  /**
   * 为玩家设置路径
   */
  setPath(playerName: string, path: Position[], color: number = 0x00ff00): void {
    if (!this.enabled || !this.scene) {
      return
    }

    // 🎯 如果路径相同，不需要重新绘制（优化性能）
    const existingVisualization = this.paths.get(playerName)
    if (existingVisualization) {
      // 检查路径是否相同
      if (existingVisualization.path.length === path.length &&
          existingVisualization.path.every((p, i) => p.x === path[i]?.x && p.y === path[i]?.y)) {
        // 路径相同，不需要重新绘制
        return
      }
    }

    // 清除旧路径
    this.clearPath(playerName)

    if (!path || path.length === 0) {
      return
    }

    // 创建新的图形对象
    const graphics = this.scene.add.graphics()
    graphics.setDepth(50) // 在玩家下方但在背景上方

    // 绘制路径
    this.drawPath(graphics, path, color)

    // 保存路径信息
    this.paths.set(playerName, {
      playerName,
      path: [...path], // 创建副本，避免引用问题
      color,
      graphics
    })
  }

  /**
   * 清除指定玩家的路径
   */
  clearPath(playerName: string): void {
    const visualization = this.paths.get(playerName)
    if (visualization && visualization.graphics) {
      visualization.graphics.destroy()
      this.paths.delete(playerName)
    }
  }

  /**
   * 清除所有路径
   */
  clearAllPaths(): void {
    this.paths.forEach((visualization) => {
      if (visualization.graphics) {
        visualization.graphics.destroy()
      }
    })
    this.paths.clear()
  }

  /**
   * 绘制路径
   */
  private drawPath(graphics: Phaser.GameObjects.Graphics, path: Position[], color: number): void {
    if (!this.scene) {
      return
    }

    const mapManager = MapManager.getInstance()
    const mapParams = mapManager.getMapParams()

    // 🎯 增强路径可见性：增加线条宽度和透明度
    graphics.lineStyle(4, color, 1.0)  // 线条宽度4，完全不透明
    graphics.fillStyle(color, 0.5)  // 填充透明度0.5，更明显

    // 绘制路径线
    for (let i = 0; i < path.length - 1; i++) {
      const start = path[i]
      const end = path[i + 1]

      const startX = mapParams.mapX + (start.x * mapParams.tileSize) + (mapParams.tileSize / 2)
      const startY = mapParams.mapY + (start.y * mapParams.tileSize) + (mapParams.tileSize / 2)
      const endX = mapParams.mapX + (end.x * mapParams.tileSize) + (mapParams.tileSize / 2)
      const endY = mapParams.mapY + (end.y * mapParams.tileSize) + (mapParams.tileSize / 2)

      // 绘制线段
      graphics.moveTo(startX, startY)
      graphics.lineTo(endX, endY)

      // 在路径点上绘制小圆圈
      graphics.fillCircle(startX, startY, 4)
    }

    // 绘制最后一个点
    if (path.length > 0) {
      const last = path[path.length - 1]
      const lastX = mapParams.mapX + (last.x * mapParams.tileSize) + (mapParams.tileSize / 2)
      const lastY = mapParams.mapY + (last.y * mapParams.tileSize) + (mapParams.tileSize / 2)
      graphics.fillCircle(lastX, lastY, 4)
    }
  }

  /**
   * 销毁管理器
   */
  destroy(): void {
    this.clearAllPaths()
    this.scene = null
    this.enabled = false
  }
}

