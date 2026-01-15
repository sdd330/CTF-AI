/**
 * InputManager - 输入管理器
 * 支持键盘输入和服务器发送的远程控制指令
 * 键盘输入优先级高于远程控制
 */
import Phaser from 'phaser'
import type { Direction } from '@/types'
import { 
  KeyboardInputHandler, 
  type KeyBindings, 
  type KeyListener,
  WASD_BINDINGS, 
  ARROW_BINDINGS 
} from './input/KeyboardInputHandler'
import { RemoteInputHandler } from './input/RemoteInputHandler'
import { InputObserverManager, type InputObserver } from './input/InputObserverManager'

export { WASD_BINDINGS, ARROW_BINDINGS }
export type { KeyBindings, InputObserver, KeyListener }

export class InputManager {
  private keyboardHandler: KeyboardInputHandler
  private remoteHandler: RemoteInputHandler
  private observerManager: InputObserverManager

  constructor(scene: Phaser.Scene, keyBindings: KeyBindings = WASD_BINDINGS) {
    this.keyboardHandler = new KeyboardInputHandler(scene, keyBindings)
    this.remoteHandler = new RemoteInputHandler()
    this.observerManager = new InputObserverManager()
  }

  initKeyboard(enableKeyboard: boolean = true): void {
    this.keyboardHandler.init(enableKeyboard)
  }

  subscribe(observer: InputObserver): void {
    this.observerManager.subscribe(observer)
  }

  unsubscribe(observer: InputObserver): void {
    this.observerManager.unsubscribe(observer)
  }

  subscribeKeyListener(listener: KeyListener): void {
    this.keyboardHandler.subscribeKeyListener(listener)
  }

  unsubscribeKeyListener(listener: KeyListener): void {
    this.keyboardHandler.unsubscribeKeyListener(listener)
  }

  setRemoteControl(direction: Direction): void {
    this.remoteHandler.setDirection(direction)
  }

  update(): void {
    let newDirection: Direction = ''
    
    const keyboardDirection = this.keyboardHandler.isEnabled() ? this.keyboardHandler.getDirection() : ''
    const remoteDirection = this.remoteHandler.getDirection()
    
    if (keyboardDirection !== '') {
      newDirection = keyboardDirection
    } else if (remoteDirection !== '') {
      newDirection = remoteDirection
    }

    this.observerManager.notifyIfChanged(newDirection)
  }

  getCurrentDirection(): Direction {
    return this.observerManager.getCurrentDirection()
  }

  setKeyboardEnabled(enabled: boolean): void {
    this.keyboardHandler.setEnabled(enabled)
    if (!enabled) {
      this.observerManager.notifyIfChanged(this.remoteHandler.getDirection())
    }
  }

  isKeyboardEnabled(): boolean {
    return this.keyboardHandler.isEnabled()
  }

  reset(): void {
    this.remoteHandler.reset()
    this.observerManager.reset()
  }

  destroy(): void {
    this.keyboardHandler.destroy()
    this.observerManager.destroy()
  }
}
