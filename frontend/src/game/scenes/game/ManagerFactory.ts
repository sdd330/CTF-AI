/**
 * 管理器工厂
 * 负责创建和初始化所有游戏管理器
 */
import Phaser from 'phaser'
import type { GameConfig, Team } from '@/types'
import { UIManager, UIComponentType } from '../../managers/UIManager'
import { SocketManager } from '../../managers/SocketManager'
import { PhysicsManager, type CollisionCallbacks } from '../../managers/PhysicsManager'
import { WorldManager } from '../../managers/WorldManager'
import { MapManager } from '../../managers/MapManager'
import { PathVisualizationManager } from '../../managers/PathVisualizationManager'
import { Flag } from '../../objects/Flag'

export class ManagerFactory {
  constructor(
    private world: WorldManager,
    private scene: Phaser.Scene
  ) {}

  createSocketManager(config: GameConfig): SocketManager {
    const socketManager = SocketManager.getInstance(this.world)

    config.teams.forEach(team => {
      if (team.name !== 'L' && team.name !== 'R') return

      const wsUrl = team.ws_url || (team.who && config.servers[team.who])
      if (wsUrl) {
        socketManager.connectTeam(team.name, wsUrl)
        if (team.name === 'L') {
          this.world.api.setLTeamConnection(true, team.who || '-')
        } else {
          this.world.api.setRTeamConnection(true, team.who || '-')
        }
      }
    })

    return socketManager
  }

  createMapManager(): MapManager {
    return MapManager.getInstance(this.world)
  }

  createPathVisualizationManager(): PathVisualizationManager {
    const manager = PathVisualizationManager.getInstance(this.world)
    manager.initialize(this.scene)
    manager.setEnabled(true)
    return manager
  }

  createUIManager(): UIManager {
    const uiManager = new UIManager(this.scene)
    const mapManager = MapManager.getInstance(this.world)
    const mapParams = mapManager.getMapParams()
    const state = this.world.getState()

    uiManager.createComponent('lScore', UIComponentType.SCORE_TEXT, 'L', 30, 20)
    uiManager.createComponent('rScore', UIComponentType.SCORE_TEXT, 'R', this.scene.scale.width - 450, 20)
    uiManager.createComponent('tutorial', UIComponentType.TUTORIAL_TEXT, mapParams.centerX, mapParams.centerY)
    uiManager.createComponent('gameOver', UIComponentType.GAME_OVER_TEXT, this.scene.scale.width * 0.5, this.scene.scale.height * 0.5)
    uiManager.createComponent('lTeamWho', UIComponentType.TEAM_NAME_TEXT, 'L', 30, 60)
    uiManager.createComponent('rTeamWho', UIComponentType.TEAM_NAME_TEXT, 'R', this.scene.scale.width - 450, 60)
    uiManager.updateComponent('lTeamWho', state.lTeamWho)
    uiManager.updateComponent('rTeamWho', state.rTeamWho)
    uiManager.initAnimations()

    return uiManager
  }

  createPhysicsManager(): PhysicsManager {
    const callbacks: CollisionCallbacks = {
      onScoreUpdate: (team: Team) => {
        if ((this.scene as any).updateTeamScore) {
          (this.scene as any).updateTeamScore(team)
        }
      },
      onCreateFlag: (world: WorldManager, scene: Phaser.Scene, x: number, y: number, team: Team, canPickup: boolean) => {
        return new Flag(world, scene, x, y, team, canPickup)
      }
    }
    return new PhysicsManager(this.world, this.scene, callbacks)
  }

  initializeMapRenderer(): void {
    const mapManager = MapManager.getInstance(this.world)
    mapManager.initializeRenderer(this.scene)
    mapManager.createGroundLayer()
    mapManager.createLevelLayer()
    mapManager.renderMap()

    const mapParams = mapManager.getMapParams()
    const startY = mapParams.centerY - mapParams.mapHeight * mapParams.tileSize / 2
    const endY = mapParams.centerY + mapParams.mapHeight * mapParams.tileSize / 2
    mapManager.createBoundaryLayer(startY, endY)
  }
}
