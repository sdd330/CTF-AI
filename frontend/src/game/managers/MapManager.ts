import Phaser from 'phaser'
import type { Position } from '@/types'
import { MapRenderer } from './map/MapRenderer'
import { MapLayerManager } from './map/MapLayerManager'
import { MapParameterManager } from './map/MapParameterManager'
import { MapDataGenerator } from './map/MapDataGenerator'
import type { GroundLayer } from './map/GroundLayer'
import type { LevelLayer } from './map/LevelLayer'
import type { BoundaryLayer } from './map/BoundaryLayer'

export interface MapLayer {
  render(): void
  update(time: number, delta: number): void
  destroy(): void
}

export { TileData } from './map/TileData'

export class MapManager {
  private static instance: MapManager | null = null
  private parameterManager: MapParameterManager
  private layerManager: MapLayerManager
  private renderer: MapRenderer
  private dataGenerator: MapDataGenerator

  private constructor(world: WorldManager) {
    this.parameterManager = new MapParameterManager(world)
    this.layerManager = new MapLayerManager(this.parameterManager)
    this.renderer = new MapRenderer(world, this.layerManager, this.parameterManager)
    this.dataGenerator = new MapDataGenerator(world, this.parameterManager)
  }

  static getInstance(world: WorldManager): MapManager {
    if (!MapManager.instance) {
      MapManager.instance = new MapManager(world)
    }
    return MapManager.instance
  }

  initializeRenderer(scene: Phaser.Scene): void {
    this.renderer.initializeRenderer(scene)
  }

  createGroundLayer(): GroundLayer { return this.layerManager.createGroundLayer() }
  createLevelLayer(): LevelLayer { return this.layerManager.createLevelLayer() }
  createBoundaryLayer(startY: number, endY: number): BoundaryLayer { return this.layerManager.createBoundaryLayer(startY, endY) }
  getLevelLayer(): LevelLayer | null { return this.layerManager.getLevelLayer() }
  updateLayers(time: number, delta: number): void { this.layerManager.updateLayers(time, delta) }
  renderLayers(): void { this.layerManager.renderLayers() }
  destroyLayers(): void { this.layerManager.destroyLayers() }

  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number } { return this.parameterManager.getMapOffset() }
  setMapParams(params: { tileSize?: number; mapWidth?: number; mapHeight?: number; mapX?: number; mapY?: number; centerX?: number; centerY?: number }): void { this.parameterManager.setMapParams(params) }
  getMapParams(): { mapX: number; mapY: number; mapWidth: number; mapHeight: number; tileSize: number; centerX: number; centerY: number } { return this.parameterManager.getMapParams() }

  isWall(x: number, y: number): boolean { return this.renderer.isWall(x, y) }
  getTileAt(x: number, y: number): Phaser.Tilemaps.Tile | null { return this.renderer.getTileAt(x, y) }
  getWalls(): Array<Position & { tileId?: number }> { return this.renderer.getWalls() }
  getObstacles(): { obstacles1: Position[]; obstacles2: Position[] } { return this.renderer.getObstacles() }
  renderMap(): void { this.renderer.renderMap() }

  generateWalls(): void { this.dataGenerator.generateWalls() }
  generateObstacles(): void { this.dataGenerator.generateObstacles() }
  generateMap(): void { this.dataGenerator.generateMap() }
  logMapDiagnostics(): void { this.dataGenerator.logMapDiagnostics() }
}

