/**
 * InputManager - 输入管理器
 * 设计模式：观察者模式 + 策略模式
 */
import type { Direction } from '@/types'
import Phaser from 'phaser'
import { GameStateManager } from './GameStateManager'

// 观察者接口
export interface InputObserver {
  onInputChange(direction: Direction): void
}

// 输入策略接口
export interface InputStrategy {
  getDirection(): Direction
  update(time: number, delta: number): void
}

// 键盘输入策略
export class KeyboardInputStrategy implements InputStrategy {
  private keys: Phaser.Types.Input.Keyboard.CursorKeys | Record<string, Phaser.Input.Keyboard.Key>

  constructor(keys: Phaser.Types.Input.Keyboard.CursorKeys | Record<string, Phaser.Input.Keyboard.Key>) {
    this.keys = keys
  }

  getDirection(): Direction {
    if ('left' in this.keys && this.keys.left.isDown) return 'left'
    if ('right' in this.keys && this.keys.right.isDown) return 'right'
    if ('up' in this.keys && this.keys.up.isDown) return 'up'
    if ('down' in this.keys && this.keys.down.isDown) return 'down'
    return ''
  }

  update(): void {
    // 键盘输入不需要更新逻辑
  }
}

// 远程控制输入策略
export class RemoteInputStrategy implements InputStrategy {
  private remoteControl: Direction | null = null

  setRemoteControl(direction: Direction | null): void {
    this.remoteControl = direction
  }

  getDirection(): Direction {
    return this.remoteControl || ''
  }

  update(): void {
    // 远程输入不需要更新逻辑
  }
}

// 混合输入策略（键盘优先）
export class HybridInputStrategy implements InputStrategy {
  private keyboardStrategy: KeyboardInputStrategy
  public remoteStrategy: RemoteInputStrategy

  constructor(keyboardStrategy: KeyboardInputStrategy, remoteStrategy: RemoteInputStrategy) {
    this.keyboardStrategy = keyboardStrategy
    this.remoteStrategy = remoteStrategy
  }

  getDirection(): Direction {
    // 键盘输入优先
    const keyboardDir = this.keyboardStrategy.getDirection()
    if (keyboardDir) return keyboardDir
    return this.remoteStrategy.getDirection()
  }

  update(): void {
    this.keyboardStrategy.update()
    this.remoteStrategy.update()
  }
}

// 输入管理器主类
export class InputManager {
  private observers: Set<InputObserver> = new Set()
  private strategy: InputStrategy
  private currentDirection: Direction = ''
  private scene: Phaser.Scene | null = null
  private gameStartCallback: (() => void) | null = null

  constructor(strategy: InputStrategy) {
    this.strategy = strategy
  }

  /**
   * 初始化输入管理器（需要在场景创建后调用）
   */
  initialize(scene: Phaser.Scene, gameStartCallback: () => void): void {
    this.scene = scene
    this.gameStartCallback = gameStartCallback
    this.initGameControls()
  }

  /**
   * 初始化游戏控制（空格键：开始/暂停/继续）
   */
  private initGameControls(): void {
    if (!this.scene) {
      throw new Error('InputManager 未初始化，请先调用 initialize(scene, callback)')
    }

    // 确保键盘输入已启用
    if (!this.scene.input.keyboard) {
      console.error('[InputManager] 键盘输入未启用！')
      return
    }

    // 确保画布能够接收键盘事件
    const canvas = this.scene.game.canvas
    if (canvas) {
      canvas.tabIndex = 0
      canvas.style.outline = 'none'
      // 添加点击事件来聚焦画布（用户点击时自动聚焦）
      canvas.addEventListener('click', () => {
        canvas.focus()
        console.log('[InputManager] 画布已聚焦，可以接收键盘输入')
      })
    }

    console.log('[InputManager] 初始化游戏控制（空格键）')
    const spaceKey = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE)
    
    if (!spaceKey) {
      console.error('[InputManager] 无法创建空格键监听器！')
      return
    }

    spaceKey.on('down', () => {
      console.log('[InputManager] 空格键被按下')
      this.handleGameControl()
    })

    console.log('[InputManager] 空格键监听器已设置')
  }

  /**
   * 处理游戏控制逻辑
   */
  private handleGameControl(): void {
    console.log('[InputManager] handleGameControl() 被调用')
    const gameState = GameStateManager.getInstance()
    const state = gameState.getState()

    console.log('[InputManager] 当前游戏状态:', {
      gameStarted: state.gameStarted,
      gamePaused: state.gamePaused,
      flowState: state.flowState,
      flowSubState: state.flowSubState
    })

    if (!state.gameStarted) {
      // 开始游戏
      console.log('[InputManager] 准备开始游戏，调用 gameStartCallback')
      if (this.gameStartCallback) {
        this.gameStartCallback()
        console.log('[InputManager] gameStartCallback 已调用')
      } else {
        console.error('[InputManager] gameStartCallback 未设置！')
      }
    } else {
      // 切换暂停状态
      console.log('[InputManager] 切换暂停状态')
      gameState.pauseGame()
      // 同步流程状态
      if (state.flowState === 'playing' && state.flowSubState === 'running') {
        GameStateManager.sendFlowEvent({ type: 'PAUSE_GAME' })
      } else if (state.flowState === 'playing' && state.flowSubState === 'paused') {
        GameStateManager.sendFlowEvent({ type: 'RESUME_GAME' })
      }
    }
  }

  // 注册观察者
  subscribe(observer: InputObserver): void {
    this.observers.add(observer)
  }

  // 取消注册观察者
  unsubscribe(observer: InputObserver): void {
    this.observers.delete(observer)
  }

  // 通知所有观察者
  private notifyObservers(direction: Direction): void {
    this.observers.forEach(observer => {
      observer.onInputChange(direction)
    })
  }

  // 更新输入状态
  update(time: number, delta: number): void {
    this.strategy.update(time, delta)
    const newDirection = this.strategy.getDirection()
    
    if (newDirection !== this.currentDirection) {
      this.currentDirection = newDirection
      this.notifyObservers(newDirection)
    }
  }

  // 获取当前方向
  getCurrentDirection(): Direction {
    return this.currentDirection
  }

  // 切换策略
  setStrategy(strategy: InputStrategy): void {
    this.strategy = strategy
  }

  // 如果策略支持远程控制，设置远程控制方向
  setRemoteControl(direction: Direction | null): void {
    if (this.strategy instanceof HybridInputStrategy) {
      this.strategy.remoteStrategy.setRemoteControl(direction)
    } else if (this.strategy instanceof RemoteInputStrategy) {
      this.strategy.setRemoteControl(direction)
    }
  }
}

