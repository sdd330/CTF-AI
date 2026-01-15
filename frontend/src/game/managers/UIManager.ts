import Phaser from 'phaser'
import { UIComponentFactory } from './ui/UIComponentFactory'
import { UIComponentManager } from './ui/UIComponentManager'
import { UIUpdateHandler } from './ui/UIUpdateHandler'
import { AnimationInitializer } from './ui/AnimationInitializer'

export interface UIComponent {
  show(): void
  hide(): void
  update(data?: unknown): void
  destroy(): void
}

export enum UIComponentType {
  SCORE_TEXT = 'score_text',
  TUTORIAL_TEXT = 'tutorial_text',
  GAME_OVER_TEXT = 'game_over_text',
  TEAM_NAME_TEXT = 'team_name_text'
}

export class UIManager {
  private componentManager: UIComponentManager
  private updateHandler: UIUpdateHandler
  private animationInitializer: AnimationInitializer
  private scene: Phaser.Scene

  constructor(scene: Phaser.Scene) {
    this.scene = scene
    this.componentManager = new UIComponentManager()
    this.updateHandler = new UIUpdateHandler(this.componentManager)
    this.animationInitializer = new AnimationInitializer(scene)
  }

  initAnimations(): void {
    this.animationInitializer.initAnimations()
  }

  isAnimationsInitialized(): boolean {
    return this.animationInitializer.isAnimationsInitialized()
  }

  createComponent(id: string, type: UIComponentType, ...args: unknown[]): UIComponent {
    const component = UIComponentFactory.create(type, this.scene, ...args)
    this.componentManager.addComponent(id, component)
    return component
  }

  getComponent(id: string): UIComponent | undefined {
    return this.componentManager.getComponent(id)
  }

  updateComponent(id: string, data?: unknown): void {
    this.updateHandler.updateComponent(id, data)
  }

  showComponent(id: string): void {
    this.updateHandler.showComponent(id)
  }

  hideComponent(id: string): void {
    this.updateHandler.hideComponent(id)
  }

  destroyAll(): void {
    this.componentManager.destroyAll()
  }

  destroyComponent(id: string): void {
    this.componentManager.destroyComponent(id)
  }
}

