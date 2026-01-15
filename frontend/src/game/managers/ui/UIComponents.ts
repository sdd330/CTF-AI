import Phaser from 'phaser'
import { UIComponent } from '../UIManager'

export class ScoreTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text
  private team: 'L' | 'R'

  constructor(scene: Phaser.Scene, team: 'L' | 'R', x: number, y: number) {
    this.team = team
    this.text = scene.add.text(x, y, `${team}Team #Flags: 0`, {
      fontFamily: 'Arial Black',
      fontSize: 36,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: team === 'L' ? 'left' : 'right'
    }).setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(score: number): void {
    this.text.setText(`${this.team}Team #Flags: ${score}`)
  }

  destroy(): void {
    this.text.destroy()
  }
}

export class TutorialTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, 'Arrow keys to move!\nPress Spacebar to Start', {
      fontFamily: 'Arial Black',
      fontSize: 48,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: 'center'
    })
      .setOrigin(0.5)
      .setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(text?: string): void {
    if (text !== undefined) {
      this.text.setText(text)
    }
  }

  destroy(): void {
    this.text.destroy()
  }
}

export class GameOverTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, 'Game Over', {
      fontFamily: 'Arial Black',
      fontSize: 64,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: 'center'
    })
      .setOrigin(0.5)
      .setDepth(100)
      .setVisible(false)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(winner?: string): void {
    if (winner) {
      this.text.setText(`${winner}Team Won!`)
    }
  }

  destroy(): void {
    this.text.destroy()
  }
}

export class TeamNameTextComponent implements UIComponent {
  private text: Phaser.GameObjects.Text

  constructor(scene: Phaser.Scene, team: 'L' | 'R', x: number, y: number) {
    this.text = scene.add.text(x, y, '-', {
      fontFamily: 'Arial Black',
      fontSize: 36,
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 8,
      align: team === 'L' ? 'left' : 'right'
    }).setDepth(100)
  }

  show(): void {
    this.text.setVisible(true)
  }

  hide(): void {
    this.text.setVisible(false)
  }

  update(who: string): void {
    this.text.setText(who)
  }

  destroy(): void {
    this.text.destroy()
  }
}
