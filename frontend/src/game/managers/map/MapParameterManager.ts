/**
 * MapParameterManager - 地图参数管理器
 * 负责管理地图参数（position, size, tile size）
 */
import Phaser from 'phaser'
import { WorldManager } from '../WorldManager'

/**
 * 地图参数管理器
 */
export class MapParameterManager {
  private mapX: number = 0
  private mapY: number = 0
  private mapWidth: number = 0
  private mapHeight: number = 0
  private tileSize: number = 32
  private centerX: number = 0
  private centerY: number = 0

  constructor(private world: WorldManager) {}

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
   * 自动计算地图参数（根据场景和配置）
   */
  calculateMapParams(scene: Phaser.Scene): void {
    // 如果地图参数未设置（为 0），则根据 scene 和配置自动计算
    if (this.mapWidth === 0 || this.mapHeight === 0) {
      const state = this.world.getState()
      const config = state.config
      const tileSize = this.tileSize || 32
      const centerX = scene.scale.width * 0.5
      const centerY = scene.scale.height * 0.5
      
      // 从配置中获取地图尺寸，如果没有则使用动态计算
      const mapWidth = config?.setup?.mapWidth || Math.floor((scene.scale.width / tileSize) - 5 * 2)
      const mapHeight = config?.setup?.mapHeight || Math.floor((scene.scale.height / tileSize) - 5 * 2)
      const mapX = centerX - (mapWidth * tileSize * 0.5)
      const mapY = centerY - (mapHeight * tileSize * 0.5)
      
      // 设置地图参数
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
  }
}
