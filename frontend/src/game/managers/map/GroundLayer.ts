/**
 * GroundLayer - 背景图层
 */
import Phaser from 'phaser'
import type { MapLayer } from '../MapManager'

/**
 * 背景图层
 */
export class GroundLayer implements MapLayer {
  private layer: Phaser.Tilemaps.TilemapLayer
  private backgroundTiles: number[] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 44]

  constructor(
    _scene: Phaser.Scene,
    private map: Phaser.Tilemaps.Tilemap,
    tileset: Phaser.Tilemaps.Tileset,
    mapX: number,
    mapY: number,
    private mapWidth: number,
    private mapHeight: number
  ) {
    console.log('[GroundLayer] 创建背景图层')
    this.layer = this.map.createBlankLayer('ground', tileset, mapX, mapY)!
    if (!this.layer) {
      throw new Error('Failed to create ground layer')
    }
    this.layer.setDepth(0)
    this.layer.setVisible(true)
    this.render()
  }

  render(): void {
    for (let y = 0; y < this.mapHeight; y++) {
      for (let x = 0; x < this.mapWidth; x++) {
        const tileIndex = Phaser.Math.RND.pick(this.backgroundTiles)
        this.layer.putTileAt(tileIndex, x, y)
      }
    }
  }

  update(): void {
    // 背景图层不需要更新
  }

  destroy(): void {
    this.layer.destroy()
  }
}
