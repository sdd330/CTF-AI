/**
 * MapManager - 地图管理器
 * 职责：
 * - 管理地图参数（mapWidth, mapHeight, mapX, mapY, tileSize, centerX, centerY）
 * - 生成地图数据（墙壁、障碍物）
 * - 渲染地图图层（背景、关卡、边界）
 * - 提供地图数据访问接口
 * 
 * 注意：TeamStates（旗帜、玩家、目标区域、监狱）的生成和维护由 GameStateManager 负责
 * 设计模式：组合模式 + 享元模式
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import { GameStateManager } from './GameStateManager'
import ASSETS from '../config/assets'

// 地图图层接口（组合模式）
export interface MapLayer {
  render(): void
  update(time: number, delta: number): void
  destroy(): void
}

// 图块数据（享元模式）
export class TileData {
  private static cache: Map<number, TileData> = new Map()
  
  constructor(
    public readonly tileId: number,
    public readonly isCollidable: boolean = false
  ) {}

  // 享元工厂方法
  static getTileData(tileId: number, isCollidable: boolean = false): TileData {
    const key = tileId * 1000 + (isCollidable ? 1 : 0)
    if (!TileData.cache.has(key)) {
      TileData.cache.set(key, new TileData(tileId, isCollidable))
    }
    return TileData.cache.get(key)!
  }
}

// 背景图层
class GroundLayer implements MapLayer {
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
    console.log('[GroundLayer] 创建背景图层, mapX:', mapX, 'mapY:', mapY, 'mapWidth:', mapWidth, 'mapHeight:', mapHeight)
    this.layer = this.map.createBlankLayer('ground', tileset, mapX, mapY)!
    if (!this.layer) {
      throw new Error('Failed to create ground layer')
    }
    this.layer.setDepth(0) // 设置背景图层深度为 0（最底层）
    this.layer.setVisible(true) // 确保图层可见
    this.render()
    console.log('[GroundLayer] 背景图层创建并渲染完成', {
      visible: this.layer.visible,
      alpha: this.layer.alpha,
      depth: this.layer.depth,
      x: this.layer.x,
      y: this.layer.y
    })
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

// 关卡图层（组合模式：包含多个子图层）
class LevelLayer implements MapLayer {
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
    console.log('[LevelLayer] 创建关卡图层, mapX:', mapX, 'mapY:', mapY, 'mapWidth:', mapWidth, 'mapHeight:', mapHeight)
    this.layer = this.map.createBlankLayer('level', tileset, mapX, mapY)!
    if (!this.layer) {
      throw new Error('Failed to create level layer')
    }
    this.layer.setDepth(10) // 设置关卡图层深度为 10（在地图背景之上，UI 之下）
    this.layer.setVisible(true) // 确保图层可见
    this.layer.fill(0, 0, 0, mapWidth, mapHeight)
    console.log('[LevelLayer] 关卡图层创建完成', {
      visible: this.layer.visible,
      alpha: this.layer.alpha,
      depth: this.layer.depth,
      x: this.layer.x,
      y: this.layer.y
    })
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
        // 设置碰撞（直接在 tile 上设置）
        tile1.setCollision(true)
        tile2.setCollision(true)
      }
    })
  }

  render(): void {
    // 由外部调用具体的渲染方法
  }

  update(): void {
    // 关卡图层不需要更新
  }

  destroy(): void {
    this.layer.destroy()
  }

  getLayer(): Phaser.Tilemaps.TilemapLayer {
    return this.layer
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
}

// 边界图层
class BoundaryLayer implements MapLayer {
  private line!: Phaser.GameObjects.Line

  constructor(
    private scene: Phaser.Scene,
    private centerX: number,
    private startY: number,
    private endY: number
  ) {
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

export class MapManager {
  private static instance: MapManager | null = null
  private gameState: GameStateManager
  
  // 地图渲染相关属性
  private layers: MapLayer[] = []
  private map: Phaser.Tilemaps.Tilemap | null = null
  private tileset: Phaser.Tilemaps.Tileset | null = null
  private groundLayer: GroundLayer | null = null
  private levelLayer: LevelLayer | null = null
  private boundaryLayer: BoundaryLayer | null = null
  private scene: Phaser.Scene | null = null
  // 地图参数（由 MapManager 统一管理）
  private mapX: number = 0
  private mapY: number = 0
  private mapWidth: number = 0
  private mapHeight: number = 0
  private tileSize: number = 32
  private centerX: number = 0
  private centerY: number = 0

  private constructor() {
    this.gameState = GameStateManager.getInstance()
  }

  /**
   * 获取单例实例
   */
  static getInstance(): MapManager {
    if (!MapManager.instance) {
      MapManager.instance = new MapManager()
    }
    return MapManager.instance
  }

  /**
   * 初始化地图渲染器（合并自 MapRenderer）
   * 地图参数由 MapManager 统一管理，如果未设置则根据 scene 和配置自动计算
   */
  initializeRenderer(scene: Phaser.Scene): void {
    this.scene = scene
    
    // 如果地图参数未设置（为 0），则根据 scene 和配置自动计算
    if (this.mapWidth === 0 || this.mapHeight === 0) {
      const state = this.gameState.getState()
      const config = state.config
      const tileSize = this.tileSize || 32
      const centerX = scene.scale.width * 0.5
      const centerY = scene.scale.height * 0.5
      
      // 从配置中获取地图尺寸，如果没有则使用动态计算
      const mapWidth = config?.setup?.mapWidth || Math.floor((scene.scale.width / tileSize) - 5 * 2)
      const mapHeight = config?.setup?.mapHeight || Math.floor((scene.scale.height / tileSize) - 5 * 2)
      const mapX = centerX - (mapWidth * tileSize * 0.5)
      const mapY = centerY - (mapHeight * tileSize * 0.5)
      
      // 设置地图参数（由 MapManager 统一管理）
      this.setMapParams({
        centerX,
        centerY,
        mapWidth,
        mapHeight,
        mapX,
        mapY,
        tileSize
      })
    }

    const tilemapKey = ASSETS.tilemapTiledJSON?.map.key
    const tilesetKey = ASSETS.spritesheet?.tiles.key
    if (!tilemapKey || !tilesetKey) {
      throw new Error('Missing required asset keys')
    }
    
    console.log('[MapManager] 创建 tilemap, key:', tilemapKey)
    console.log('[MapManager] 添加 tileset, key:', tilesetKey)
    
    // 检查资源是否已加载
    const tilemapExists = scene.cache.tilemap.exists(tilemapKey)
    const tilesetExists = scene.textures.exists(tilesetKey)
    console.log('[MapManager] 资源检查:', {
      tilemapExists,
      tilesetExists,
      allTextures: Object.keys(scene.textures.list),
      allTilemaps: Object.keys(scene.cache.tilemap.entries)
    })
    
    if (!tilemapExists) {
      throw new Error(`Tilemap not loaded: ${tilemapKey}`)
    }
    if (!tilesetExists) {
      throw new Error(`Tileset not loaded: ${tilesetKey}`)
    }
    
    // 创建 tilemap（使用已加载的 tilemap JSON）
    this.map = scene.make.tilemap({ key: tilemapKey })
    
    // 添加 tileset（与 frontend 保持一致）
    this.tileset = this.map.addTilesetImage(tilesetKey)!
    
    if (!this.tileset) {
      console.error('[MapManager] 无法添加 tileset，tilesetKey:', tilesetKey)
      throw new Error(`Failed to add tileset image: ${tilesetKey}`)
    }
    
    console.log('[MapManager] Tilemap 和 tileset 创建成功, tileset:', this.tileset)
  }

  /**
   * 创建背景图层
   */
  createGroundLayer(): GroundLayer {
    if (!this.scene || !this.map || !this.tileset) {
      throw new Error('Renderer not initialized. Call initializeRenderer() first.')
    }
    this.groundLayer = new GroundLayer(
      this.scene,
      this.map,
      this.tileset,
      this.mapX,
      this.mapY,
      this.mapWidth,
      this.mapHeight
    )
    this.layers.push(this.groundLayer)
    return this.groundLayer
  }

  /**
   * 创建关卡图层
   */
  createLevelLayer(): LevelLayer {
    if (!this.scene || !this.map || !this.tileset) {
      throw new Error('Renderer not initialized. Call initializeRenderer() first.')
    }
    this.levelLayer = new LevelLayer(
      this.scene,
      this.map,
      this.tileset,
      this.mapX,
      this.mapY,
      this.mapWidth,
      this.mapHeight
    )
    this.layers.push(this.levelLayer)
    return this.levelLayer
  }

  /**
   * 创建边界图层
   */
  createBoundaryLayer(startY: number, endY: number): BoundaryLayer {
    if (!this.scene) {
      throw new Error('Renderer not initialized. Call initializeRenderer() first.')
    }
    this.boundaryLayer = new BoundaryLayer(
      this.scene,
      this.centerX,
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

  /**
   * 获取地图偏移量
   */
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number } {
    return {
      x: this.mapX + this.tileSize * 0.5,
      y: this.mapY + this.tileSize * 0.5,
      width: this.mapWidth,
      height: this.mapHeight,
      tileSize: this.tileSize
    }
  }

  /**
   * 检查是否为墙壁
   */
  isWall(x: number, y: number): boolean {
    return this.levelLayer?.isWall(x, y) || false
  }

  /**
   * 获取世界坐标的图块
   */
  getTileAt(x: number, y: number): Phaser.Tilemaps.Tile | null {
    return this.levelLayer?.getTileAtWorldXY(x, y) || null
  }

  // ========== 地图参数管理（由 MapManager 统一管理） ==========

  /**
   * 设置地图参数
   */
  setMapParams(params: {
    tileSize?: number
    mapWidth?: number
    mapHeight?: number
    mapX?: number
    mapY?: number
    centerX?: number
    centerY?: number
  }): void {
    if (params.tileSize !== undefined) this.tileSize = params.tileSize
    if (params.mapWidth !== undefined) this.mapWidth = params.mapWidth
    if (params.mapHeight !== undefined) this.mapHeight = params.mapHeight
    if (params.mapX !== undefined) this.mapX = params.mapX
    if (params.mapY !== undefined) this.mapY = params.mapY
    if (params.centerX !== undefined) this.centerX = params.centerX
    if (params.centerY !== undefined) this.centerY = params.centerY
  }

  /**
   * 获取地图参数
   */
  getMapParams(): {
    mapX: number
    mapY: number
    mapWidth: number
    mapHeight: number
    tileSize: number
    centerX: number
    centerY: number
  } {
    return {
      mapX: this.mapX,
      mapY: this.mapY,
      mapWidth: this.mapWidth,
      mapHeight: this.mapHeight,
      tileSize: this.tileSize,
      centerX: this.centerX,
      centerY: this.centerY
    }
  }

  /**
   * 获取墙壁数据
   */
  getWalls(): Array<Position & { tileId?: number }> {
    return this.gameState.getState().walls
  }

  /**
   * 获取障碍物数据
   */
  getObstacles(): { obstacles1: Position[]; obstacles2: Position[] } {
    const state = this.gameState.getState()
    return {
      obstacles1: state.obstacles1,
      obstacles2: state.obstacles2
    }
  }


  /**
   * 渲染地图（统一入口）
   */
  renderMap(): void {
    if (!this.levelLayer) {
      throw new Error('Level layer not created. Call createLevelLayer() first.')
    }

    // TeamStates 由 GameStateManager 统一管理
    const teamStates = this.gameState.getTeamStates()
    const obstacles = this.getObstacles()

    // 设置并渲染墙壁
    this.levelLayer.setWalls(this.getWalls())
    this.levelLayer.renderWalls()

    // 渲染监狱和目标区域
    this.levelLayer.renderPrisons(teamStates.lTeamState.prison, teamStates.rTeamState.prison)
    this.levelLayer.renderTargets(teamStates.lTeamState.target, teamStates.rTeamState.target)

    // 渲染障碍物
    this.levelLayer.renderObstacles(obstacles.obstacles1, obstacles.obstacles2)
  }

  /**
   * 生成墙壁
   */
  generateWalls(): void {
    const mapWidth = this.mapWidth
    const mapHeight = this.mapHeight

    const walls = [
      { x: 0, y: 0, tileId: 45 },
      { x: mapWidth - 1, y: 0, tileId: 47 },
      { x: 0, y: mapHeight - 1, tileId: 69 },
      { x: mapWidth - 1, y: mapHeight - 1, tileId: 71 }
    ].concat(
      Array.from({ length: mapWidth - 2 }, (_, i) => ({ x: i + 1, y: 0, tileId: 46 })),
      Array.from({ length: mapWidth - 2 }, (_, i) => ({ x: i + 1, y: mapHeight - 1, tileId: 46 })),
      Array.from({ length: mapHeight - 2 }, (_, i) => ({ x: 0, y: i + 1, tileId: 57 })),
      Array.from({ length: mapHeight - 2 }, (_, i) => ({ x: mapWidth - 1, y: i + 1, tileId: 59 }))
    )

    this.gameState.setMapData({ walls })
  }

  /**
   * 生成障碍物
   */
  generateObstacles(): void {
    const state = this.gameState.getState()
    const mapWidth = this.mapWidth
    const mapHeight = this.mapHeight
    const numObstacles1 = state.numObstacles1
    const numObstacles2 = state.numObstacles2

    const obstacles1: Position[] = []
    const obstacles2: Position[] = []
    const OBSTACLE_MAX_RETRIES = 1000

    const notContains = (arr: Position[], x: number, y: number) => {
      return !arr.find(obj => obj.x === x && obj.y === y)
    }

    // 生成障碍物1
    for (let i = 0; i < numObstacles1; i++) {
      let retries = 0
      while (retries < OBSTACLE_MAX_RETRIES) {
        const x = Phaser.Math.RND.integerInRange(4, mapWidth - 5)
        const y = Phaser.Math.RND.integerInRange(1, mapHeight - 2)
        if (notContains(obstacles1, x, y)) {
          obstacles1.push({ x, y })
          break
        }
        retries++
      }
    }

    // 生成障碍物2
    for (let i = 0; i < numObstacles2; i++) {
      let retries = 0
      while (retries < OBSTACLE_MAX_RETRIES) {
        const x = Phaser.Math.RND.integerInRange(4, mapWidth - 5)
        const y = Phaser.Math.RND.integerInRange(1, mapHeight - 3)
        if (
          notContains(obstacles1, x, y) &&
          notContains(obstacles1, x, y + 1) &&
          notContains(obstacles2, x, y - 1) &&
          notContains(obstacles2, x, y)
        ) {
          obstacles2.push({ x, y })
          break
        }
        retries++
      }
    }

    // 更新到状态管理器
    this.gameState.setMapData({ obstacles1, obstacles2 })
  }


  /**
   * 生成完整地图（只生成地图数据：墙壁和障碍物）
   * TeamStates（旗帜、玩家、目标区域、监狱）由 GameStateManager 生成
   */
  generateMap(): void {
    this.generateWalls()
    this.generateObstacles()
    // TeamStates 的生成已移到 GameStateManager，保持职责明确
  }

  /**
   * 记录地图诊断信息
   */
  logMapDiagnostics(): void {
    const state = this.gameState.getState()
    const mapWidth = this.mapWidth
    const mapHeight = this.mapHeight
    const numFlags = state.numFlags
    const obstacles1 = state.obstacles1
    const obstacles2 = state.obstacles2

    const notContains = (arr: Position[], x: number, y: number) => {
      return !arr.find(obj => obj.x === x && obj.y === y)
    }

    const lFlagAreaX = [2, Math.floor(mapWidth / 2) - 1]
    const lFlagAreaY = [1, mapHeight - 3]
    const rFlagAreaX = [Math.floor(mapWidth / 2), mapWidth - 2]
    const rFlagAreaY = [1, mapHeight - 3]

    // 计算L队可用位置
    const lAvailableSpots: Position[] = []
    for (let x = lFlagAreaX[0]; x <= lFlagAreaX[1]; x++) {
      for (let y = lFlagAreaY[0]; y <= lFlagAreaY[1]; y++) {
        if (
          notContains(obstacles1, x, y) &&
          notContains(obstacles2, x, y - 1) &&
          notContains(obstacles2, x, y)
        ) {
          lAvailableSpots.push({ x, y })
        }
      }
    }

    // 计算R队可用位置
    const rAvailableSpots: Position[] = []
    for (let x = rFlagAreaX[0]; x <= rFlagAreaX[1]; x++) {
      for (let y = rFlagAreaY[0]; y <= rFlagAreaY[1]; y++) {
        if (
          notContains(obstacles1, x, y) &&
          notContains(obstacles2, x, y - 1) &&
          notContains(obstacles2, x, y)
        ) {
          rAvailableSpots.push({ x, y })
        }
      }
    }

    console.log(`地图诊断: 地图大小=${mapWidth}x${mapHeight}, 需要旗帜=${numFlags}`)
    console.log(`L队可用位置: ${lAvailableSpots.length}, 需要: ${numFlags}`)
    console.log(`R队可用位置: ${rAvailableSpots.length}, 需要: ${numFlags}`)
    if (lAvailableSpots.length < numFlags) {
      console.error(`警告: L队可用位置不足！只有 ${lAvailableSpots.length} 个位置，但需要 ${numFlags} 个旗帜`)
    }
    if (rAvailableSpots.length < numFlags) {
      console.error(`警告: R队可用位置不足！只有 ${rAvailableSpots.length} 个位置，但需要 ${numFlags} 个旗帜`)
    }
  }
}

