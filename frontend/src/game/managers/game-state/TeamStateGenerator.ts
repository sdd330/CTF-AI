/**
 * TeamStateGenerator - 团队状态生成器
 * 职责：生成团队状态（flags, players, targets, prisons）
 */
import Phaser from 'phaser'
import type { Position, TeamState, GameState } from './types'

export class TeamStateGenerator {
  private getState: () => GameState
  private setLTeamState: (state: Partial<TeamState>) => void
  private setRTeamState: (state: Partial<TeamState>) => void

  constructor(
    getState: () => GameState,
    setLTeamState: (state: Partial<TeamState>) => void,
    setRTeamState: (state: Partial<TeamState>) => void
  ) {
    this.getState = getState
    this.setLTeamState = setLTeamState
    this.setRTeamState = setRTeamState
  }

  /**
   * 生成旗帜位置
   */
  generateFlags(
    obstacles: { obstacles1: Position[]; obstacles2: Position[] },
    mapWidth: number,
    mapHeight: number
  ): void {
    const state = this.getState()
    const numFlags = state.numFlags
    const useRandomFlags = state.useRandomFlags
    const obstacles1 = obstacles.obstacles1
    const obstacles2 = obstacles.obstacles2

    // 计算中间线（与后端保持一致：middle_line = width / 2.0）
    const middleLine = mapWidth / 2.0
    const lMaxX = Math.floor(middleLine - 0.1)
    const rMinX = Math.ceil(middleLine)

    let lFlags: Position[] = []
    let rFlags: Position[] = []

    if (useRandomFlags) {
      const notContains = (arr: Position[], x: number, y: number) => {
        return !arr.find(obj => obj.x === x && obj.y === y)
      }

      const MAX_RETRIES = 1000

      // L队旗帜：在左半场随机摆放
      for (let i = 0; i < numFlags; i++) {
        let retries = 0
        let found = false
        while (retries < MAX_RETRIES) {
          const x = Phaser.Math.RND.integerInRange(2, lMaxX)
          const y = Phaser.Math.RND.integerInRange(1, mapHeight - 3)
          if (
            notContains(obstacles1, x, y) &&
            notContains(obstacles2, x, y - 1) &&
            notContains(obstacles2, x, y) &&
            notContains(lFlags, x, y)
          ) {
            lFlags.push({ x, y })
            found = true
            break
          }
          retries++
        }
        if (!found) {
          const fallbackX = Math.min(1, lMaxX)
          lFlags.push({ x: fallbackX, y: i + 1 })
        }
      }

      // R队旗帜：在右半场随机摆放
      for (let i = 0; i < numFlags; i++) {
        let retries = 0
        let found = false
        while (retries < MAX_RETRIES) {
          const x = Phaser.Math.RND.integerInRange(rMinX, mapWidth - 2)
          const y = Phaser.Math.RND.integerInRange(1, mapHeight - 3)
          if (
            notContains(obstacles1, x, y) &&
            notContains(obstacles2, x, y - 1) &&
            notContains(obstacles2, x, y) &&
            notContains(rFlags, x, y)
          ) {
            rFlags.push({ x, y })
            found = true
            break
          }
          retries++
        }
        if (!found) {
          const fallbackX = Math.max(rMinX, mapWidth - 2)
          rFlags.push({ x: fallbackX, y: i + 1 })
        }
      }
    } else {
      // 固定模式
      lFlags = Array.from({ length: numFlags }, (_, i) => ({ 
        x: Math.min(1, lMaxX),
        y: i + 1 
      }))
      rFlags = Array.from({ length: numFlags }, (_, i) => ({ 
        x: Math.max(rMinX, mapWidth - 2),
        y: i + 1 
      }))
    }

    this.setLTeamState({ flags: lFlags })
    this.setRTeamState({ flags: rFlags })
  }

  /**
   * 生成玩家位置
   */
  generatePlayers(mapWidth: number): void {
    const state = this.getState()
    const numPlayers = state.numPlayers
    const useRandomFlags = state.useRandomFlags

    const lPlayers = useRandomFlags
      ? Array.from({ length: numPlayers }, (_, i) => ({ x: 1, y: i + 1, name: `L${i}` }))
      : Array.from({ length: numPlayers }, (_, i) => ({ x: 2, y: i + 1, name: `L${i}` }))

    const rPlayers = useRandomFlags
      ? Array.from({ length: numPlayers }, (_, i) => ({ x: mapWidth - 2, y: i + 1, name: `R${i}` }))
      : Array.from({ length: numPlayers }, (_, i) => ({ x: mapWidth - 3, y: i + 1, name: `R${i}` }))

    this.setLTeamState({ players: lPlayers })
    this.setRTeamState({ players: rPlayers })
  }

  /**
   * 生成目标区域和监狱位置
   */
  generateTargetsAndPrisons(mapWidth: number, mapHeight: number): void {
    const targetY = mapHeight / 2
    const prisonY = mapHeight - 3

    const lTarget = this.create3x3grid(2, Math.floor(targetY))
    const lPrison = this.create3x3grid(2, Math.floor(prisonY))
    const rTarget = this.create3x3grid(mapWidth - 3, Math.floor(targetY))
    const rPrison = this.create3x3grid(mapWidth - 3, Math.floor(prisonY))

    console.log('[TeamStateGenerator] 生成目标和监狱:')
    console.log('  L队 target:', lTarget.length, '个位置', lTarget)
    console.log('  L队 prison:', lPrison.length, '个位置', lPrison)
    console.log('  R队 target:', rTarget.length, '个位置', rTarget)
    console.log('  R队 prison:', rPrison.length, '个位置', rPrison)

    this.setLTeamState({
      target: lTarget,
      prison: lPrison
    })
    this.setRTeamState({
      target: rTarget,
      prison: rPrison
    })
  }

  /**
   * 创建 3x3 网格位置
   */
  private create3x3grid(x: number, y: number): Position[] {
    return [
      { x: x - 1, y: y - 1 }, { x: x, y: y - 1 }, { x: x + 1, y: y - 1 },
      { x: x - 1, y: y }, { x: x, y: y }, { x: x + 1, y: y },
      { x: x - 1, y: y + 1 }, { x: x, y: y + 1 }, { x: x + 1, y: y + 1 }
    ]
  }

  /**
   * 生成所有 TeamStates
   */
  generateTeamStates(
    obstacles: { obstacles1: Position[]; obstacles2: Position[] },
    mapManager: { getMapParams: () => { mapWidth: number; mapHeight: number } }
  ): void {
    const mapParams = mapManager.getMapParams()
    this.generateFlags(obstacles, mapParams.mapWidth, mapParams.mapHeight)
    this.generatePlayers(mapParams.mapWidth)
    this.generateTargetsAndPrisons(mapParams.mapWidth, mapParams.mapHeight)
  }
}
