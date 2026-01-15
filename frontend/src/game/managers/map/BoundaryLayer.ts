/**
 * BoundaryLayer - 边界图层
 */
import Phaser from 'phaser'
import type { MapLayer } from '../MapManager'

/**
 * 边界图层
 */
export class BoundaryLayer implements MapLayer {
  private line!: Phaser.GameObjects.Line
  private scene: Phaser.Scene
  private centerX: number
  private startY: number
  private endY: number

  constructor(
    scene: Phaser.Scene,
    centerX: number,
    startY: number,
    endY: number
  ) {
    this.scene = scene
    this.centerX = centerX
    this.startY = startY
    this.endY = endY
    this.render()
  }

  render(): void {
    this.line = this.scene.add.line(0, 0, this.centerX, this.startY, this.centerX, this.endY, 0x000000)
      .setOrigin(0, 0)
      .setLineWidth(1)
  }

  update(): void {
    // 边界不需要更新
  }

  destroy(): void {
    this.line.destroy()
  }
}
