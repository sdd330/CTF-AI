/**
 * LevelLayer - 关卡图层
 * 负责渲染墙壁、监狱、目标区域和障碍物
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import type { MapLayer } from '../MapManager'

/**
 * 关卡图层
 */
export class LevelLayer implements MapLayer {
  private layer: Phaser.Tilemaps.TilemapLayer
  private walls: Array<Position & { tileId?: number }> = []
  private targetTiles: number[] = [13, 14, 15, 25, 26, 27, 37, 38, 39]
  private prisonTiles: number[] = [97, 98, 99, 109, 110, 111, 121, 122, 123]
  private wallTiles: number[] = [45, 46, 47, 57, 59, 69, 70, 71]
  private tree1Tiles: number[] = [6, 18, 30, 29, 28]
  private tree2Tiles: number[][] = [[4, 16], [5, 17]]

  constructor(
    _scene: Phaser.Scene,
    private map: Phaser.Tilemaps.Tilemap,
    tileset: Phaser.Tilemaps.Tileset,
    mapX: number,
    mapY: number,
    private mapWidth: number,
    mapHeight: number
  ) {
    console.log('[LevelLayer] 创建关卡图层')
    this.layer = this.map.createBlankLayer('level', tileset, mapX, mapY)!
    if (!this.layer) {
      throw new Error('Failed to create level layer')
    }
    this.layer.setDepth(10)
    this.layer.setVisible(true)
    this.layer.fill(0, 0, 0, mapWidth, mapHeight)
  }

  setWalls(walls: Array<Position & { tileId?: number }>): void {
    this.walls = walls
  }

  renderWalls(): void {
    this.walls.forEach(wall => {
      const tile = this.layer.getTileAt(wall.x, wall.y)
      if (tile) {
        tile.index = wall.tileId || this.wallTiles[0]
        const collisionId = (wall.x - 1) * this.mapWidth + wall.y
        this.map.setCollision(collisionId)
      }
    })
  }

  renderPrisons(lTeamPrison: Position[], rTeamPrison: Position[]): void {
    lTeamPrison.forEach((prison, i) => {
      const tile = this.layer.getTileAt(prison.x, prison.y)
      if (tile && i < this.prisonTiles.length) {
        tile.index = this.prisonTiles[i]
      }
    })
    rTeamPrison.forEach((prison, i) => {
      const tile = this.layer.getTileAt(prison.x, prison.y)
      if (tile && i < this.prisonTiles.length) {
        tile.index = this.prisonTiles[i]
      }
    })
  }

  renderTargets(lTeamTarget: Position[], rTeamTarget: Position[]): void {
    lTeamTarget.forEach((target, i) => {
      const tile = this.layer.getTileAt(target.x, target.y)
      if (tile && i < this.targetTiles.length) {
        tile.index = this.targetTiles[i]
      }
    })
    rTeamTarget.forEach((target, i) => {
      const tile = this.layer.getTileAt(target.x, target.y)
      if (tile && i < this.targetTiles.length) {
        tile.index = this.targetTiles[i]
      }
    })
  }

  renderObstacles(obstacles1: Position[], obstacles2: Position[]): void {
    obstacles1.forEach(obs => {
      const tile = this.layer.getTileAt(obs.x, obs.y)
      if (tile) {
        tile.index = Phaser.Math.RND.pick(this.tree1Tiles)
        const collisionId = (obs.x - 1) * this.mapWidth + obs.y
        this.map.setCollision(collisionId)
      }
    })

    obstacles2.forEach(obs => {
      const treeTile = Phaser.Math.RND.pick(this.tree2Tiles)
      const tile1 = this.layer.getTileAt(obs.x, obs.y)
      const tile2 = this.layer.getTileAt(obs.x, obs.y + 1)
      if (tile1 && tile2) {
        tile1.index = treeTile[0]
        tile2.index = treeTile[1]
        tile1.setCollision(true)
        tile2.setCollision(true)
      }
    })
  }

  isWall(x: number, y: number): boolean {
    const tile = this.layer.getTileAtWorldXY(x, y, true)
    if (!tile) return false
    return (
      this.wallTiles.indexOf(tile.index) >= 0 ||
      this.tree1Tiles.indexOf(tile.index) >= 0 ||
      this.tree2Tiles[0].indexOf(tile.index) >= 0 ||
      this.tree2Tiles[1].indexOf(tile.index) >= 0
    )
  }

  getTileAtWorldXY(x: number, y: number): Phaser.Tilemaps.Tile | null {
    return this.layer.getTileAtWorldXY(x, y, true) || null
  }

  render(): void {
    // 图层渲染由具体方法处理
  }

  update(): void {
    // 关卡图层不需要更新
  }

  destroy(): void {
    this.layer.destroy()
  }
}
