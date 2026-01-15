/**
 * 事件设置
 * 负责设置所有游戏事件监听器
 */
import Phaser from 'phaser'
import type { Team, PlayerActions } from '@/types'
import { InputManager } from '../../managers/InputManager'
import { SocketManager, SocketEvent } from '../../managers/SocketManager'

export class EventSetup {
  private scene: Phaser.Scene
  private socketManager: SocketManager

  constructor(scene: Phaser.Scene, socketManager: SocketManager) {
    this.scene = scene
    this.socketManager = socketManager
  }

  setupSocketListeners(onPlayerInfoUpdate: (team: Team, actions: PlayerActions) => void): void {
    this.socketManager.on(SocketEvent.ACTIONS_RECEIVED, (...args: unknown[]) => {
      const team = args[0] as Team
      const actions = args[1] as PlayerActions
      onPlayerInfoUpdate(team, actions)
    })
  }

  setupInputManagers(lteamInputManager: InputManager): void {
    lteamInputManager.subscribeKeyListener({
      onSpacePress: () => {
        if ((this.scene as any).startOrPauseOrContinue) {
          (this.scene as any).startOrPauseOrContinue()
        }
      }
    })
  }
}
