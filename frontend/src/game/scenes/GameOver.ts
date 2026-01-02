import Phaser from 'phaser'
import { GameStateManager } from '../managers/GameStateManager'

export class GameOver extends Phaser.Scene {
  constructor() {
    super('GameOver')
  }

  create() {
    const state = GameStateManager.getInstance().getState()
    const winner = state.winner
    const winnerText = winner ? `${winner}Team Won!` : 'Game Over'

    this.add.text(this.scale.width * 0.5, this.scale.height * 0.5, winnerText, {
      fontFamily: 'Arial Black',
      fontSize: 64,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: 'center'
    }).setOrigin(0.5)

    // 添加重新开始的提示
    this.add.text(this.scale.width * 0.5, this.scale.height * 0.5 + 100, 'Press R to Restart\nPress L to Reload', {
      fontFamily: 'Arial',
      fontSize: 24,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 4,
      align: 'center'
    }).setOrigin(0.5)

    // 键盘控制
    const rKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.R)
    const lKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.L)

    rKey.on('down', () => {
      GameStateManager.sendFlowEvent({ type: 'RESTART' })
    })

    lKey.on('down', () => {
      GameStateManager.sendFlowEvent({ type: 'RESTART_LOADING' })
    })
  }
}

