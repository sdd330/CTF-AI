/**
 * MapDataGenerator - 地图数据生成器
 * 负责生成地图数据（墙壁、障碍物）
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import { WorldManager } from '../WorldManager'
import { MapParameterManager } from './MapParameterManager'

/**
 * 地图数据生成器
 */
export class MapDataGenerator {
  constructor(
    private world: WorldManager,
    private parameterManager: MapParameterManager
  ) {}

  /**
   * 生成墙壁
   */
  generateWalls(): void {
    const params = this.parameterManager.getMapParams()
    const mapWidth = params.mapWidth
    const mapHeight = params.mapHeight

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

    this.world.api.setMapData({ walls })
  }

  /**
   * 生成障碍物
   */
  generateObstacles(): void {
    const state = this.world.getState()
    const params = this.parameterManager.getMapParams()
    const mapWidth = params.mapWidth
    const mapHeight = params.mapHeight
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
    this.world.api.setMapData({ obstacles1, obstacles2 })
  }

  /**
   * 生成完整地图（只生成地图数据：墙壁和障碍物）
   */
  generateMap(): void {
    this.generateWalls()
    this.generateObstacles()
  }

  /**
   * 记录地图诊断信息
   */
  logMapDiagnostics(): void {
    const state = this.world.getState()
    const params = this.parameterManager.getMapParams()
    const mapWidth = params.mapWidth
    const mapHeight = params.mapHeight
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
