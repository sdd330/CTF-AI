import Phaser from 'phaser'
import { UIComponent, UIComponentType } from '../UIManager'
import { ScoreTextComponent, TutorialTextComponent, GameOverTextComponent, TeamNameTextComponent } from './UIComponents'

export class UIComponentFactory {
  static create(
    type: UIComponentType,
    scene: Phaser.Scene,
    ...args: unknown[]
  ): UIComponent {
    switch (type) {
      case UIComponentType.SCORE_TEXT:
        return new ScoreTextComponent(scene, args[0] as 'L' | 'R', args[1] as number, args[2] as number)
      case UIComponentType.TUTORIAL_TEXT:
        return new TutorialTextComponent(scene, args[0] as number, args[1] as number)
      case UIComponentType.GAME_OVER_TEXT:
        return new GameOverTextComponent(scene, args[0] as number, args[1] as number)
      case UIComponentType.TEAM_NAME_TEXT:
        return new TeamNameTextComponent(scene, args[0] as 'L' | 'R', args[1] as number, args[2] as number)
      default:
        throw new Error(`Unknown UI component type: ${type}`)
    }
  }
}
