/**
 * MapRenderer - 地图渲染器
 * 负责地图渲染和显示
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import { WorldManager } from '../WorldManager'
import ASSETS from '../../config/assets'
import { MapLayerManager } from './MapLayerManager'
import { MapParameterManager } from './MapParameterManager'

/**
 * 地图渲染器
 */
export class MapRenderer {
  private scene: Phaser.Scene | null = null
  private map: Phaser.Tilemaps.Tilemap | null = null
  private tileset: Phaser.Tilemaps.Tileset | null = null

  constructor(
    private world: WorldManager,
    private layerManager: MapLayerManager,
    private parameterManager: MapParameterManager
  ) {}

  /**
   * 初始化地图渲染器
   */
  initializeRenderer(scene: Phaser.Scene): void {
    this.scene = scene
    
    // 自动计算地图参数
    this.parameterManager.calculateMapParams(scene)

    const tilemapKey = ASSETS.tilemapTiledJSON?.map.key
    const tilesetKey = ASSETS.spritesheet?.tiles.key
    if (!tilemapKey || !tilesetKey) {
      throw new Error('Missing required asset keys')
    }
    
    console.log('[MapRenderer] 创建 tilemap, key:', tilemapKey)
    console.log('[MapRenderer] 添加 tileset, key:', tilesetKey)
    
    // 检查资源是否已加载
    const tilemapExists = scene.cache.tilemap.exists(tilemapKey)
    const tilesetExists = scene.textures.exists(tilesetKey)
    console.log('[MapRenderer] 资源检查:', {
      tilemapExists,
      tilesetExists
    })
    
    if (!tilemapExists) {
      throw new Error(`Tilemap not loaded: ${tilemapKey}`)
    }
    if (!tilesetExists) {
      throw new Error(`Tileset not loaded: ${tilesetKey}`)
    }
    
    // 创建 tilemap
    this.map = scene.make.tilemap({ key: tilemapKey })
    
    // 添加 tileset
    this.tileset = this.map.addTilesetImage(tilesetKey)!
    
    if (!this.tileset) {
      console.error('[MapRenderer] 无法添加 tileset，tilesetKey:', tilesetKey)
      throw new Error(`Failed to add tileset image: ${tilesetKey}`)
    }
    
    console.log('[MapRenderer] Tilemap 和 tileset 创建成功')
    
    // 设置图层管理器
    this.layerManager.setMapAndTileset(scene, this.map, this.tileset)
  }

  /**
   * 渲染地图
   */
  renderMap(): void {
    const levelLayer = this.layerManager.getLevelLayer()
    if (!levelLayer) {
      throw new Error('Level layer not created. Call createLevelLayer() first.')
    }

    // TeamStates 由 WorldManager 统一管理
    const teamStates = this.world.api.getTeamStates()
    const obstacles = this.getObstacles()

    // 设置并渲染墙壁
    levelLayer.setWalls(this.getWalls())
    levelLayer.renderWalls()

    // 渲染监狱和目标区域
    levelLayer.renderPrisons(teamStates.lTeamState.prison, teamStates.rTeamState.prison)
    levelLayer.renderTargets(teamStates.lTeamState.target, teamStates.rTeamState.target)

    // 渲染障碍物
    levelLayer.renderObstacles(obstacles.obstacles1, obstacles.obstacles2)
  }

  /**
   * 获取墙壁数据
   */
  getWalls(): Array<Position & { tileId?: number }> {
    return this.world.getState().walls
  }

  /**
   * 获取障碍物数据
   */
  getObstacles(): { obstacles1: Position[]; obstacles2: Position[] } {
    const state = this.world.getState()
    return {
      obstacles1: state.obstacles1,
      obstacles2: state.obstacles2
    }
  }

  /**
   * 检查是否为墙壁
   */
  isWall(x: number, y: number): boolean {
    return this.layerManager.getLevelLayer()?.isWall(x, y) || false
  }

  /**
   * 获取世界坐标的图块
   */
  getTileAt(x: number, y: number): Phaser.Tilemaps.Tile | null {
    return this.layerManager.getLevelLayer()?.getTileAtWorldXY(x, y) || null
  }
}
