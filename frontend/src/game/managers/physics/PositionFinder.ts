/**
 * PositionFinder - 位置查找器
 * 负责查找可用的位置（监狱、旗帜等）
 */
import Phaser from 'phaser'
import type { Position } from '@/types'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { MapManager } from '../MapManager'

/**
 * 位置查找器
 */
export class PositionFinder {
  private mapManager: MapManager | null = null

  constructor(mapManager: MapManager | null = null) {
    this.mapManager = mapManager
  }

  /**
   * 设置地图管理器
   */
  setMapManager(mapManager: MapManager): void {
    this.mapManager = mapManager
  }

  /**
   * 查找可用的监狱位置
   */
  findAvailablePrisonTile(players: Player[], prisons: Position[]): Position {
    if (!this.mapManager) {
      return prisons[0] || { x: 0, y: 0 }
    }

    for (const prison of prisons) {
      let isAvailable = true
      for (const player of players) {
        if (!player.inPrison) continue
        const playerSprite = player as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(playerSprite.x, playerSprite.y)
        if (tile && tile.x === prison.x && tile.y === prison.y) {
          isAvailable = false
          break
        }
      }
      if (isAvailable) {
        return prison
      }
    }
    return prisons[0] || { x: 0, y: 0 }
  }

  /**
   * 查找可用的旗帜位置
   */
  findAvailableFlagTile(flags: Flag[], targets: Position[]): Position {
    if (!this.mapManager) {
      return targets[0] || { x: 0, y: 0 }
    }

    for (const target of targets) {
      let isAvailable = true
      for (const flag of flags) {
        if (flag.canPickup) continue
        const flagSprite = flag as Phaser.Physics.Arcade.Sprite
        const tile = this.mapManager.getTileAt(flagSprite.x, flagSprite.y)
        if (tile && tile.x === target.x && tile.y === target.y) {
          isAvailable = false
          break
        }
      }
      if (isAvailable) {
        return target
      }
    }
    return targets[0] || { x: 0, y: 0 }
  }
}
