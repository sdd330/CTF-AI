/**
 * TeamStateDomain - 队伍状态域
 * 职责：管理队伍分数和玩家/旗帜状态
 */
import type { PlayerStatus, FlagStatus, TeamState, GameState } from './types'

export class TeamStateDomain {
  private getState: () => GameState
  private updateState: (updates: Partial<GameState>) => void

  constructor(
    getState: () => GameState,
    updateState: (updates: Partial<GameState>) => void
  ) {
    this.getState = getState
    this.updateState = updateState
  }

  /**
   * 更新 L 队分数
   */
  updateLTeamScore(score: number): void {
    const state = this.getState()
    this.updateState({
      lTeamScore: score,
      lTeamState: { ...state.lTeamState, score }
    })
  }

  /**
   * 更新 R 队分数
   */
  updateRTeamScore(score: number): void {
    const state = this.getState()
    this.updateState({
      rTeamScore: score,
      rTeamState: { ...state.rTeamState, score }
    })
  }

  /**
   * 更新 L 队玩家状态
   */
  updateLTeamPlayers(players: PlayerStatus[]): void {
    this.updateState({ lTeamPlayers: players })
  }

  /**
   * 更新 R 队玩家状态
   */
  updateRTeamPlayers(players: PlayerStatus[]): void {
    this.updateState({ rTeamPlayers: players })
  }

  /**
   * 更新 L 队旗帜状态
   */
  updateLTeamFlags(flags: FlagStatus[]): void {
    this.updateState({ lTeamFlags: flags })
  }

  /**
   * 更新 R 队旗帜状态
   */
  updateRTeamFlags(flags: FlagStatus[]): void {
    this.updateState({ rTeamFlags: flags })
  }

  /**
   * 设置 L 队连接状态
   */
  setLTeamConnection(connected: boolean, who: string = '-'): void {
    this.updateState({
      lTeamConnected: connected,
      lTeamWho: who
    })
  }

  /**
   * 设置 R 队连接状态
   */
  setRTeamConnection(connected: boolean, who: string = '-'): void {
    this.updateState({
      rTeamConnected: connected,
      rTeamWho: who
    })
  }

  /**
   * 设置 L 队状态
   */
  setLTeamState(state: Partial<TeamState>): void {
    const currentState = this.getState()
    this.updateState({
      lTeamState: { ...currentState.lTeamState, ...state }
    })
  }

  /**
   * 设置 R 队状态
   */
  setRTeamState(state: Partial<TeamState>): void {
    const currentState = this.getState()
    this.updateState({
      rTeamState: { ...currentState.rTeamState, ...state }
    })
  }

  /**
   * 重置团队状态
   */
  resetTeamStates(): void {
    this.updateState({
      lTeamState: {
        score: 0,
        playerSpriteChoice: 1,
        flags: [],
        players: [],
        target: [],
        prison: []
      },
      rTeamState: {
        score: 0,
        playerSpriteChoice: 4,
        flags: [],
        players: [],
        target: [],
        prison: []
      },
      lTeamScore: 0,
      rTeamScore: 0,
      lTeamPlayers: [],
      rTeamPlayers: [],
      lTeamFlags: [],
      rTeamFlags: []
    })
  }

  /**
   * 获取团队状态数据
   */
  getTeamStates(): {
    lTeamState: TeamState
    rTeamState: TeamState
  } {
    const state = this.getState()
    return {
      lTeamState: state.lTeamState,
      rTeamState: state.rTeamState
    }
  }
}
