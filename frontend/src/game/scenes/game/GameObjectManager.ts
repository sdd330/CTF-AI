/**
 * GameObjectManager - 游戏对象管理器
 * 负责管理和设置所有游戏对象组（玩家、旗帜、区域）
 */
import type Phaser from 'phaser'
import { WorldManager } from '../../managers/WorldManager'
import type { GameInitializer } from './GameInitializer'

export interface GameObjects {
  lteamPlayers: Phaser.GameObjects.Group
  rteamPlayers: Phaser.GameObjects.Group
  lteamFlags: Phaser.GameObjects.Group
  rteamFlags: Phaser.GameObjects.Group
  lteamTargetZone: Phaser.GameObjects.Zone
  rteamTargetZone: Phaser.GameObjects.Zone
  lteamPrisonZone: Phaser.GameObjects.Zone
  rteamPrisonZone: Phaser.GameObjects.Zone
}

export class GameObjectManager {
  constructor(
    private world: WorldManager,
    private scene: Phaser.Scene,
    private initializer: GameInitializer
  ) {}

  setupGameObjects(): GameObjects {
    const teams = this.world.api.initTeams(
      this.world,
      this.scene, 
      this.initializer.mapManager, 
      this.initializer.physicsManager,
      true
    )
    
    if (teams.lteamInputManager && teams.rteamInputManager) {
      this.initializer.setInputManagers(teams.lteamInputManager, teams.rteamInputManager)
    }
    
    return {
      lteamPlayers: teams.lteamPlayers,
      rteamPlayers: teams.rteamPlayers,
      lteamFlags: teams.lteamFlags,
      rteamFlags: teams.rteamFlags,
      lteamTargetZone: teams.lteamTargetZone,
      rteamTargetZone: teams.rteamTargetZone,
      lteamPrisonZone: teams.lteamPrisonZone,
      rteamPrisonZone: teams.rteamPrisonZone
    }
  }
}
