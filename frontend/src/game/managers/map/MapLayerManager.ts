/**
 * MapLayerManager - 地图图层管理器
 * 负责图层管理（ground, level, boundary）
 */
import Phaser from 'phaser'
import type { MapLayer } from '../MapManager'
import { GroundLayer } from './GroundLayer'
import { LevelLayer } from './LevelLayer'
import { BoundaryLayer } from './BoundaryLayer'
import { MapParameterManager } from './MapParameterManager'

/**
 * 地图图层管理器
 */
export class MapLayerManager {
  private layers: MapLayer[] = []
  private map: Phaser.Tilemaps.Tilemap | null = null
  private tileset: Phaser.Tilemaps.Tileset | null = null
  private groundLayer: GroundLayer | null = null
  private levelLayer: LevelLayer | null = null
  private boundaryLayer: BoundaryLayer | null = null
  private scene: Phaser.Scene | null = null
  private parameterManager: MapParameterManager

  constructor(parameterManager: MapParameterManager) {
    this.parameterManager = parameterManager
  }

  /**
   * 设置场景和地图
   */
  setMapAndTileset(scene: Phaser.Scene, map: Phaser.Tilemaps.Tilemap, tileset: Phaser.Tilemaps.Tileset): void {
    this.scene = scene
    this.map = map
    this.tileset = tileset
  }

  /**
   * 创建背景图层
   */
  createGroundLayer(): GroundLayer {
    if (!this.scene || !this.map || !this.tileset) {
      throw new Error('Renderer not initialized. Call setMapAndTileset() first.')
    }
    const params = this.parameterManager.getMapParams()
    this.groundLayer = new GroundLayer(
      this.scene,
      this.map,
      this.tileset,
      params.mapX,
      params.mapY,
      params.mapWidth,
      params.mapHeight
    )
    this.layers.push(this.groundLayer)
    return this.groundLayer
  }

  /**
   * 创建关卡图层
   */
  createLevelLayer(): LevelLayer {
    if (!this.scene || !this.map || !this.tileset) {
      throw new Error('Renderer not initialized. Call setMapAndTileset() first.')
    }
    const params = this.parameterManager.getMapParams()
    this.levelLayer = new LevelLayer(
      this.scene,
      this.map,
      this.tileset,
      params.mapX,
      params.mapY,
      params.mapWidth,
      params.mapHeight
    )
    this.layers.push(this.levelLayer)
    return this.levelLayer
  }

  /**
   * 创建边界图层
   */
  createBoundaryLayer(startY: number, endY: number): BoundaryLayer {
    if (!this.scene) {
      throw new Error('Renderer not initialized. Call setMapAndTileset() first.')
    }
    const params = this.parameterManager.getMapParams()
    this.boundaryLayer = new BoundaryLayer(
      this.scene,
      params.centerX,
      startY,
      endY
    )
    this.layers.push(this.boundaryLayer)
    return this.boundaryLayer
  }

  /**
   * 获取关卡图层
   */
  getLevelLayer(): LevelLayer | null {
    return this.levelLayer
  }

  /**
   * 更新所有图层
   */
  updateLayers(time: number, delta: number): void {
    this.layers.forEach(layer => layer.update(time, delta))
  }

  /**
   * 渲染所有图层
   */
  renderLayers(): void {
    this.layers.forEach(layer => layer.render())
  }

  /**
   * 销毁所有图层
   */
  destroyLayers(): void {
    this.layers.forEach(layer => layer.destroy())
    this.layers = []
    this.map = null
    this.tileset = null
    this.groundLayer = null
    this.levelLayer = null
    this.boundaryLayer = null
  }
}
