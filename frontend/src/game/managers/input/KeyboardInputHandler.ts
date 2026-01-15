/**
 * 键盘输入处理器
 * 负责键盘输入的检测和方向获取
 */
import Phaser from 'phaser'
import type { Direction } from '@/types'

export interface KeyBindings {
  up: number
  down: number
  left: number
  right: number
}

export const WASD_BINDINGS: KeyBindings = {
  up: 87,
  down: 83,
  left: 65,
  right: 68
}

export const ARROW_BINDINGS: KeyBindings = {
  up: 38,
  down: 40,
  left: 37,
  right: 39
}

export interface KeyListener {
  onSpacePress?(): void
  onEscapePress?(): void
}

export class KeyboardInputHandler {
  private scene: Phaser.Scene
  private enabled: boolean = false
  private keyBindings: KeyBindings
  private directionKeys?: {
    up: Phaser.Input.Keyboard.Key
    down: Phaser.Input.Keyboard.Key
    left: Phaser.Input.Keyboard.Key
    right: Phaser.Input.Keyboard.Key
  }
  private spaceKey?: Phaser.Input.Keyboard.Key
  private escapeKey?: Phaser.Input.Keyboard.Key
  private keyListeners: Set<KeyListener> = new Set()

  constructor(scene: Phaser.Scene, keyBindings: KeyBindings = WASD_BINDINGS) {
    this.scene = scene
    this.keyBindings = keyBindings
  }

  init(enabled: boolean = true): void {
    this.enabled = enabled

    if (!enabled || !this.scene.input.keyboard) {
      return
    }

    this.directionKeys = this.scene.input.keyboard.addKeys({
      up: this.keyBindings.up,
      down: this.keyBindings.down,
      left: this.keyBindings.left,
      right: this.keyBindings.right
    }) as {
      up: Phaser.Input.Keyboard.Key
      down: Phaser.Input.Keyboard.Key
      left: Phaser.Input.Keyboard.Key
      right: Phaser.Input.Keyboard.Key
    }

    this.spaceKey = this.scene.input.keyboard.addKey(
      Phaser.Input.Keyboard.KeyCodes.SPACE
    )
    this.spaceKey.on('down', () => {
      this.notifyKeyListeners('space')
    })

    this.escapeKey = this.scene.input.keyboard.addKey(
      Phaser.Input.Keyboard.KeyCodes.ESC
    )
    this.escapeKey.on('down', () => {
      this.notifyKeyListeners('escape')
    })
  }

  getDirection(): Direction {
    if (!this.enabled || !this.directionKeys) {
      return ''
    }

    let direction: Direction = ''
    if (this.directionKeys.up.isDown) {
      direction = 'up'
    } else if (this.directionKeys.down.isDown) {
      direction = 'down'
    } else if (this.directionKeys.left.isDown) {
      direction = 'left'
    } else if (this.directionKeys.right.isDown) {
      direction = 'right'
    }

    return direction
  }

  setEnabled(enabled: boolean): void {
    this.enabled = enabled
  }

  isEnabled(): boolean {
    return this.enabled
  }

  subscribeKeyListener(listener: KeyListener): void {
    this.keyListeners.add(listener)
  }

  unsubscribeKeyListener(listener: KeyListener): void {
    this.keyListeners.delete(listener)
  }

  private notifyKeyListeners(key: 'space' | 'escape'): void {
    this.keyListeners.forEach(listener => {
      if (key === 'space' && listener.onSpacePress) {
        listener.onSpacePress()
      } else if (key === 'escape' && listener.onEscapePress) {
        listener.onEscapePress()
      }
    })
  }

  destroy(): void {
    if (this.spaceKey) {
      this.spaceKey.removeAllListeners()
    }
    if (this.escapeKey) {
      this.escapeKey.removeAllListeners()
    }
    this.keyListeners.clear()
  }
}
