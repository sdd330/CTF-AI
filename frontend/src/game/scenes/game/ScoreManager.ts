/**
 * ScoreManager - 分数和旗帜管理
 * 负责更新分数、移除旗帜和触发游戏结束
 */
import type { Team } from '@/types'
import type { Flag } from '../../objects/Flag'
import { WorldManager } from '../../managers/WorldManager'

export class ScoreManager {
  constructor(
    private world: WorldManager,
    private lteamFlags: Phaser.GameObjects.Group,
    private rteamFlags: Phaser.GameObjects.Group,
    private uiManager: any,
    private onGameOver: (team: Team) => void
  ) {}

  removeFlagItem(flag: Flag): void {
    if (flag.team === 'L') {
      this.lteamFlags.remove(flag, true, true)
    } else if (flag.team === 'R') {
      this.rteamFlags.remove(flag, true, true)
    }
  }

  updateTeamScore(team: Team): void {
    const state = this.world.getState()
    const NUM_FLAGS = state.numFlags
    
    if (team === 'L') {
      const newScore = state.lTeamScore + 1
      this.world.api.updateLTeamScore(newScore)
      this.uiManager.updateComponent('lScore', newScore)
      if (newScore === NUM_FLAGS) {
        this.onGameOver(team)
      }
    } else if (team === 'R') {
      const newScore = state.rTeamScore + 1
      this.world.api.updateRTeamScore(newScore)
      this.uiManager.updateComponent('rScore', newScore)
      if (newScore === NUM_FLAGS) {
        this.onGameOver(team)
      }
    }
  }
}
