/**
 * TeamInitializer - 队伍初始化器
 * 职责：初始化队伍（创建玩家、旗帜和区域对象）
 */
import Phaser from 'phaser'
import type { WorldManager } from '../WorldManager'
import type { TeamState } from './types'
import { Player } from '../../objects/Player'
import { Flag } from '../../objects/Flag'
import { InputManager, WASD_BINDINGS, ARROW_BINDINGS } from '../InputManager'

export class TeamInitializer {
  /**
   * 初始化队伍（创建玩家、旗帜和区域对象）
   */
  initTeams(
    world: WorldManager,
    scene: Phaser.Scene,
    teamStates: { lTeamState: TeamState; rTeamState: TeamState },
    mapParams: { mapX: number; mapY: number; tileSize: number },
    physicsManager: { addPhysicsBody: (body: Phaser.GameObjects.Zone) => void },
    enableKeyboard: boolean = true
  ): {
    lteamFlags: Phaser.GameObjects.Group
    rteamFlags: Phaser.GameObjects.Group
    lteamPlayers: Phaser.GameObjects.Group
    rteamPlayers: Phaser.GameObjects.Group
    lteamTargetZone: Phaser.GameObjects.Zone
    rteamTargetZone: Phaser.GameObjects.Zone
    lteamPrisonZone: Phaser.GameObjects.Zone
    rteamPrisonZone: Phaser.GameObjects.Zone
    lteamInputManager: InputManager | null
    rteamInputManager: InputManager | null
  } {
    // 为两个队伍创建独立的 InputManager
    let lteamInputManager: InputManager | null = null
    let rteamInputManager: InputManager | null = null
    
    if (enableKeyboard) {
      // L队使用 WASD 键
      lteamInputManager = new InputManager(scene, WASD_BINDINGS)
      lteamInputManager.initKeyboard(true)
      
      // R队使用方向键
      rteamInputManager = new InputManager(scene, ARROW_BINDINGS)
      rteamInputManager.initKeyboard(true)
    }
    // L队
    const lteamFlags = scene.add.group()
    const lteamPlayers = scene.add.group()

    console.log('[TeamInitializer] 创建 L 队旗帜，数量:', teamStates.lTeamState.flags.length)
    teamStates.lTeamState.flags.forEach(flag => {
      const flagObj = new Flag(world, scene, flag.x, flag.y, 'L', true)
      console.log('[TeamInitializer] 创建 L 队旗帜:', flag.x, flag.y, '实际位置:', flagObj.x, flagObj.y)
      lteamFlags.add(flagObj)
    })

    console.log('[TeamInitializer] 创建 L 队玩家，数量:', teamStates.lTeamState.players.length)
    console.log('[TeamInitializer] L 队 InputManager:', lteamInputManager ? '已创建' : '未创建')
    teamStates.lTeamState.players.forEach(player => {
      const playerObj = new Player(world, scene, player.name, player.x, player.y, 'L', teamStates.lTeamState.playerSpriteChoice, lteamInputManager)
      console.log('[TeamInitializer] 创建 L 队玩家:', player.name, player.x, player.y, '实际位置:', playerObj.x, playerObj.y)
      lteamPlayers.add(playerObj)
    })

    const lteamTargetZone = scene.add.zone(
      mapParams.mapX + (teamStates.lTeamState.target[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.lTeamState.target[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(lteamTargetZone)

    const lteamPrisonZone = scene.add.zone(
      mapParams.mapX + (teamStates.lTeamState.prison[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.lTeamState.prison[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(lteamPrisonZone)

    // R队
    const rteamFlags = scene.add.group()
    const rteamPlayers = scene.add.group()

    console.log('[TeamInitializer] 创建 R 队旗帜，数量:', teamStates.rTeamState.flags.length)
    teamStates.rTeamState.flags.forEach(flag => {
      const flagObj = new Flag(world, scene, flag.x, flag.y, 'R', true)
      console.log('[TeamInitializer] 创建 R 队旗帜:', flag.x, flag.y, '实际位置:', flagObj.x, flagObj.y)
      rteamFlags.add(flagObj)
    })

    console.log('[TeamInitializer] 创建 R 队玩家，数量:', teamStates.rTeamState.players.length)
    console.log('[TeamInitializer] R 队 InputManager:', rteamInputManager ? '已创建' : '未创建')
    teamStates.rTeamState.players.forEach(player => {
      const playerObj = new Player(world, scene, player.name, player.x, player.y, 'R', teamStates.rTeamState.playerSpriteChoice, rteamInputManager)
      console.log('[TeamInitializer] 创建 R 队玩家:', player.name, player.x, player.y, '实际位置:', playerObj.x, playerObj.y)
      rteamPlayers.add(playerObj)
    })

    const rteamTargetZone = scene.add.zone(
      mapParams.mapX + (teamStates.rTeamState.target[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.rTeamState.target[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(rteamTargetZone)

    const rteamPrisonZone = scene.add.zone(
      mapParams.mapX + (teamStates.rTeamState.prison[0].x * mapParams.tileSize + 1.5 * mapParams.tileSize),
      mapParams.mapY + (teamStates.rTeamState.prison[0].y * mapParams.tileSize + 1.5 * mapParams.tileSize),
      3 * mapParams.tileSize,
      3 * mapParams.tileSize
    )
    physicsManager.addPhysicsBody(rteamPrisonZone)

    return {
      lteamFlags,
      rteamFlags,
      lteamPlayers,
      rteamPlayers,
      lteamTargetZone,
      rteamTargetZone,
      lteamPrisonZone,
      rteamPrisonZone,
      lteamInputManager,
      rteamInputManager
    }
  }
}
