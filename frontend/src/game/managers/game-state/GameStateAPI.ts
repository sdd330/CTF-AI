/**
 * GameStateAPI - 游戏状态公共 API
 * 提供团队状态、分数、玩家和旗帜的更新和查询方法
 * 以及配置、地图和流程控制
 */
import type Phaser from 'phaser'
import type { Team, PlayerStatus, FlagStatus, Position, GameConfig, LogLevel, DebugInfo } from '@/types'
import type { WorldManager } from '../WorldManager'
import type { GameState, TeamState, GameFlowEvent } from './types'
import { TeamStateDomain } from './TeamStateDomain'
import { TeamStateGenerator } from './TeamStateGenerator'
import { TeamInitializer } from './TeamInitializer'
import { GameStateDomain } from './GameStateDomain'
import { ConfigStateDomain } from './ConfigStateDomain'
import { MapStateDomain } from './MapStateDomain'
import { FlowStateDomain } from './FlowStateDomain'
import { GameStateDebugger } from './GameStateDebugger'

export class GameStateAPI {
  private gameStateDomain: GameStateDomain
  private teamStateDomain: TeamStateDomain
  private teamStateGenerator: TeamStateGenerator
  private teamInitializer: TeamInitializer
  private configStateDomain: ConfigStateDomain
  private mapStateDomain: MapStateDomain
  private flowStateDomain: FlowStateDomain
  private debugger: GameStateDebugger

  // 游戏对象组的缓存
  private lteamFlags: Phaser.GameObjects.Group | null = null
  private rteamFlags: Phaser.GameObjects.Group | null = null
  private lteamPlayers: Phaser.GameObjects.Group | null = null
  private rteamPlayers: Phaser.GameObjects.Group | null = null

  constructor(
    getState: () => GameState,
    updateState: (updates: Partial<GameState>) => void
  ) {
    this.gameStateDomain = new GameStateDomain(getState, updateState)
    this.teamStateDomain = new TeamStateDomain(getState, updateState)
    this.teamStateGenerator = new TeamStateGenerator(
      getState,
      (state) => this.teamStateDomain.setLTeamState(state),
      (state) => this.teamStateDomain.setRTeamState(state)
    )
    this.teamInitializer = new TeamInitializer()
    this.configStateDomain = new ConfigStateDomain(getState, updateState)
    this.mapStateDomain = new MapStateDomain(getState, updateState)
    this.flowStateDomain = new FlowStateDomain(getState, updateState)
    this.debugger = new GameStateDebugger(getState)
  }

  updateLTeamScore(score: number): void {
    this.teamStateDomain.updateLTeamScore(score)
  }
  updateRTeamScore(score: number): void {
    this.teamStateDomain.updateRTeamScore(score)
  }
  updateLTeamStateScore(score: number): void {
    this.teamStateDomain.updateLTeamScore(score)
  }
  updateRTeamStateScore(score: number): void {
    this.teamStateDomain.updateRTeamScore(score)
  }
  updateLTeamPlayers(players: PlayerStatus[]): void {
    this.teamStateDomain.updateLTeamPlayers(players)
  }
  updateRTeamPlayers(players: PlayerStatus[]): void {
    this.teamStateDomain.updateRTeamPlayers(players)
  }
  updateLTeamFlags(flags: FlagStatus[]): void {
    this.teamStateDomain.updateLTeamFlags(flags)
  }
  updateRTeamFlags(flags: FlagStatus[]): void {
    this.teamStateDomain.updateRTeamFlags(flags)
  }
  setLTeamConnection(connected: boolean, who: string = '-'): void {
    this.teamStateDomain.setLTeamConnection(connected, who)
  }
  setRTeamConnection(connected: boolean, who: string = '-'): void {
    this.teamStateDomain.setRTeamConnection(connected, who)
  }
  setLTeamState(state: Partial<TeamState>): void {
    this.teamStateDomain.setLTeamState(state)
  }
  setRTeamState(state: Partial<TeamState>): void {
    this.teamStateDomain.setRTeamState(state)
  }
  resetTeamStates(): void {
    this.teamStateDomain.resetTeamStates()
  }
  getTeamStates(): { lTeamState: TeamState; rTeamState: TeamState } {
    return this.teamStateDomain.getTeamStates()
  }
  generateFlags(obstacles: { obstacles1: Position[]; obstacles2: Position[] }, mapWidth: number, mapHeight: number): void {
    this.teamStateGenerator.generateFlags(obstacles, mapWidth, mapHeight)
  }
  generatePlayers(mapWidth: number): void {
    this.teamStateGenerator.generatePlayers(mapWidth)
  }
  generateTargetsAndPrisons(mapWidth: number, mapHeight: number): void {
    this.teamStateGenerator.generateTargetsAndPrisons(mapWidth, mapHeight)
  }
  generateTeamStates(obstacles: { obstacles1: Position[]; obstacles2: Position[] }, mapManager: { getMapParams: () => { mapWidth: number; mapHeight: number } }): void {
    this.teamStateGenerator.generateTeamStates(obstacles, mapManager)
  }
  initTeams(world: WorldManager, scene: Phaser.Scene, mapManager: { getMapParams: () => { mapX: number; mapY: number; tileSize: number } }, physicsManager: { addPhysicsBody: (body: Phaser.GameObjects.Zone) => void }, enableKeyboard: boolean = true): {
    lteamFlags: Phaser.GameObjects.Group
    rteamFlags: Phaser.GameObjects.Group
    lteamPlayers: Phaser.GameObjects.Group
    rteamPlayers: Phaser.GameObjects.Group
    lteamTargetZone: Phaser.GameObjects.Zone
    rteamTargetZone: Phaser.GameObjects.Zone
    lteamPrisonZone: Phaser.GameObjects.Zone
    rteamPrisonZone: Phaser.GameObjects.Zone
    lteamInputManager: any
    rteamInputManager: any
  } {
    const teamStates = this.getTeamStates()
    const mapParams = mapManager.getMapParams()
    const result = this.teamInitializer.initTeams(world, scene, teamStates, mapParams, physicsManager, enableKeyboard)
    this.lteamFlags = result.lteamFlags
    this.rteamFlags = result.rteamFlags
    this.lteamPlayers = result.lteamPlayers
    this.rteamPlayers = result.rteamPlayers
    return result
  }
  getLTeamFlags(): Phaser.GameObjects.Group | null {
    return this.lteamFlags
  }
  getRTeamFlags(): Phaser.GameObjects.Group | null {
    return this.rteamFlags
  }
  getLTeamPlayers(): Phaser.GameObjects.Group | null {
    return this.lteamPlayers
  }
  getRTeamPlayers(): Phaser.GameObjects.Group | null {
    return this.rteamPlayers
  }
  async loadConfig(configPath: string = 'game_config.json'): Promise<GameConfig> {
    return this.configStateDomain.loadConfig(configPath)
  }
  getConfig(): GameConfig | null {
    return this.configStateDomain.getConfig()
  }
  setConfig(config: GameConfig): void {
    this.configStateDomain.setConfig(config)
  }
  setMapData(data: { walls?: Array<Position & { tileId?: number }>; obstacles1?: Position[]; obstacles2?: Position[] }): void {
    this.mapStateDomain.setMapData(data)
  }
  resetMapState(): void {
    this.mapStateDomain.resetMapState()
  }
  startGame(): void {
    this.gameStateDomain.startGame()
  }
  pauseGame(): void {
    this.gameStateDomain.pauseGame()
  }
  endGame(team: Team): void {
    this.gameStateDomain.endGame(team)
  }
  resetGameState(): void {
    this.gameStateDomain.resetGameState()
    this.updateLTeamScore(0)
    this.updateRTeamScore(0)
  }
  sendFlowEvent(event: GameFlowEvent): void {
    this.flowStateDomain.sendFlowEvent(event)
  }
  isGameActive(): boolean {
    return this.gameStateDomain.isGameActive()
  }
  getDebugInfo(): DebugInfo {
    return this.debugger.getDebugInfo()
  }
  log(level: LogLevel, message: string, data?: unknown): void {
    this.debugger.log(level, message, data)
  }
}
