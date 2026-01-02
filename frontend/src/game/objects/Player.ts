import Phaser from 'phaser'
import type { Team, Direction } from '@/types'
import ASSETS from '../config/assets'

// 场景接口（用于类型安全地访问场景方法）
export interface ISceneWithMapMethods {
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number }
  isWall(x: number, y: number): boolean
}

export enum PlayerDirection {
  UP = 'up',
  DOWN = 'down',
  LEFT = 'left',
  RIGHT = 'right'
}

export class Player extends Phaser.Physics.Arcade.Sprite {
  public target: { x: number; y: number } = { x: 0, y: 0 }
  public name: string
  public team: Team
  public inPrison: boolean = false
  public inPrisonTimeLeft: number = 0
  public inPrisonDuration: number = 20000
  public hasFlag: boolean = false
  public spriteChoice: number
  public remoteControl: Direction | null = null
  public plannedPath: Array<{ x: number; y: number }> | null = null // 存储路径用于预判

  private moveSpeed: number = 300
  private frameDuration: number = 0
  private accumulator: number = 0
  private mapOffset: { x: number; y: number; tileSize: number } | null = null
  private canGoNextTile: boolean = false
  private keys: Phaser.Types.Input.Keyboard.CursorKeys | null = null

  constructor(
    scene: Phaser.Scene,
    name: string,
    x: number,
    y: number,
    team: Team,
    spriteChoice: number = 1,
    useAWSD: boolean = true
  ) {
    const frameIndex = (spriteChoice - 1) * 12 + 1
    super(scene, 0, 0, ASSETS.spritesheet!.characters.key, frameIndex)

    scene.add.existing(this)
    scene.physics.add.existing(this)

    this.name = name
    this.team = team
    this.spriteChoice = spriteChoice

    // 获取地图偏移量
    const sceneWithMap = scene as Phaser.Scene & ISceneWithMapMethods
    if (sceneWithMap.getMapOffset) {
      this.mapOffset = sceneWithMap.getMapOffset()
      this.target.x = this.mapOffset.x + (x * this.mapOffset.tileSize)
      this.target.y = this.mapOffset.y + (y * this.mapOffset.tileSize)
      this.setPosition(this.target.x, this.target.y)
      this.frameDuration = this.moveSpeed / this.mapOffset.tileSize
    }

    this.setCollideWorldBounds(true)
    this.setDepth(100)

    // 键盘控制
    if (useAWSD) {
      this.keys = scene.input.keyboard!.addKeys({
        up: Phaser.Input.Keyboard.KeyCodes.W,
        left: Phaser.Input.Keyboard.KeyCodes.A,
        down: Phaser.Input.Keyboard.KeyCodes.S,
        right: Phaser.Input.Keyboard.KeyCodes.D
      }) as Phaser.Types.Input.Keyboard.CursorKeys
    } else {
      this.keys = scene.input.keyboard!.createCursorKeys()
    }
  }

  collectFlag(): void {
    this.hasFlag = true
  }

  dropFlag(): void {
    this.hasFlag = false
  }

  /**
   * 从路径计算方向
   */
  private calculateDirectionFromPath(currentPos: { x: number; y: number }, nextPos: { x: number; y: number }): Direction | null {
    if (!this.mapOffset) return null
    
    const dx = nextPos.x - currentPos.x
    const dy = nextPos.y - currentPos.y
    
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? 'right' : 'left'
    } else if (Math.abs(dy) > Math.abs(dx)) {
      return dy > 0 ? 'down' : 'up'
    }
    return null
  }

  /**
   * 检查路径中是否有连续相同的方向（预判）
   */
  private canContinueMoving(): boolean {
    if (!this.mapOffset || !this.plannedPath || this.plannedPath.length < 3) {
      return false
    }
    
    const EPSILON = 0.1
    const currentTileX = Math.round((this.x - this.mapOffset.x) / this.mapOffset.tileSize)
    const currentTileY = Math.round((this.y - this.mapOffset.y) / this.mapOffset.tileSize)
    
    // 找到当前玩家在路径中的位置
    let currentIndex = -1
    for (let i = 0; i < this.plannedPath.length; i++) {
      const pathPos = this.plannedPath[i]
      if (Math.abs(pathPos.x - currentTileX) < EPSILON && Math.abs(pathPos.y - currentTileY) < EPSILON) {
        currentIndex = i
        break
      }
    }
    
    // 如果找不到当前位置，或者已经接近路径末尾，不预判
    if (currentIndex < 0 || currentIndex >= this.plannedPath.length - 2) {
      return false
    }
    
    // 检查下一步和再下一步的方向是否相同
    const nextPos = this.plannedPath[currentIndex + 1]
    const nextNextPos = this.plannedPath[currentIndex + 2]
    
    const currentPos = { x: currentTileX, y: currentTileY }
    const nextDir = this.calculateDirectionFromPath(currentPos, nextPos)
    const nextNextDir = this.calculateDirectionFromPath(nextPos, nextNextPos)
    
    // 如果下一步和再下一步方向相同，且与当前指令方向相同，可以继续移动
    return nextDir !== null && nextDir === nextNextDir && nextDir === this.remoteControl
  }

  setRemoteControl(remoteControl: Direction | null): void {
    // 关键逻辑：优化预判 - 如果下一步和再下一步方向相同，可以继续移动
    if (!this.mapOffset) {
      this.remoteControl = remoteControl
      return
    }
    
    const EPSILON = 0.1
    const atTarget = Math.abs(this.target.x - this.x) < EPSILON && 
                     Math.abs(this.target.y - this.y) < EPSILON
    
    // 如果玩家还在移动中（未到达目标）
    if (!atTarget) {
      // 检查是否可以预判继续移动（下一步和再下一步方向相同）
      if (this.canContinueMoving()) {
        // 可以预判，保持当前指令继续移动
        return
      }
      // 不能预判，忽略新指令，停留在当前格子
      if (this.remoteControl !== null && this.remoteControl !== '') {
        return
      }
    }
    
    // 玩家已到达目标位置，或者当前没有指令，可以接受新指令
    if (this.remoteControl !== remoteControl && remoteControl !== null && remoteControl !== '') {
      const oldDirection = this.remoteControl

      if (oldDirection !== null && oldDirection !== '') {
        this.target.x = this.x
        this.target.y = this.y
      }
    }
    this.remoteControl = remoteControl
  }

  /**
   * 设置路径用于预判
   */
  setPlannedPath(path: Array<{ x: number; y: number }> | null): void {
    this.plannedPath = path
  }

  update(_time: number, delta: number): void {
    if (!this.mapOffset) return

    this.accumulator += delta

    while (this.accumulator > this.frameDuration) {
      this.accumulator -= this.frameDuration
      
      if (this.inPrison) {
        this.inPrisonTimeLeft -= this.frameDuration
        if (this.inPrisonTimeLeft <= 0) {
          this.inPrison = false
          this.inPrisonTimeLeft = 0
        }
      }
      
      if (!this.inPrison) {
        this.checkInput()
        this.move()
      } else {
        this.showStaticImage()
      }
    }
  }

  private checkInput(): void {
    if (!this.mapOffset) return

    const EPSILON = 0.1
    const atTarget = Math.abs(this.target.x - this.x) < EPSILON && Math.abs(this.target.y - this.y) < EPSILON

    if (this.canGoNextTile && atTarget) {
      this.canGoNextTile = false
      const moveDirection = { x: 0, y: 0 }

      // 键盘优先于远程控制
      if (this.keys) {
        if (this.keys.left.isDown) moveDirection.x--
        else if (this.keys.right.isDown) moveDirection.x++
        else if (this.keys.up.isDown) moveDirection.y--
        else if (this.keys.down.isDown) moveDirection.y++
      }

      // 远程控制：优化预判逻辑
      // 如果下一步和再下一步方向相同，保持移动；否则执行完一个动作后清除
      if (moveDirection.x === 0 && moveDirection.y === 0) {
        if (this.remoteControl === PlayerDirection.LEFT) {
          moveDirection.x--
          // 检查是否可以预判继续移动
          if (!this.canContinueMoving()) {
            this.remoteControl = null // 不能预判，执行完动作后清除，等待下一个指令
          }
        } else if (this.remoteControl === PlayerDirection.RIGHT) {
          moveDirection.x++
          // 检查是否可以预判继续移动
          if (!this.canContinueMoving()) {
            this.remoteControl = null // 不能预判，执行完动作后清除，等待下一个指令
          }
        } else if (this.remoteControl === PlayerDirection.UP) {
          moveDirection.y--
          // 检查是否可以预判继续移动
          if (!this.canContinueMoving()) {
            this.remoteControl = null // 不能预判，执行完动作后清除，等待下一个指令
          }
        } else if (this.remoteControl === PlayerDirection.DOWN) {
          moveDirection.y++
          // 检查是否可以预判继续移动
          if (!this.canContinueMoving()) {
            this.remoteControl = null // 不能预判，执行完动作后清除，等待下一个指令
          }
        }
      }

      // 设置下一个目标位置
      const nextPosition = {
        x: this.x + (moveDirection.x * this.mapOffset.tileSize),
        y: this.y + (moveDirection.y * this.mapOffset.tileSize)
      }

      // 检查是否可以移动到下一个位置
      const sceneWithMap = this.scene as Phaser.Scene & ISceneWithMapMethods
      if (sceneWithMap.isWall && !sceneWithMap.isWall(nextPosition.x, nextPosition.y)) {
        this.target.x = nextPosition.x
        this.target.y = nextPosition.y
      } else {
        // 如果无法移动到下一个位置（比如是墙），也清除 remoteControl
        // 避免卡在无法移动的方向上
        if (moveDirection.x !== 0 || moveDirection.y !== 0) {
          // 已经在上面清除了，这里不需要再清除
        }
      }
    }
  }

  private move(): void {
    // 参考 frontend/src/gameObjects/Player.js 的 move() 方法
    // frontend: "player" + spriteChoice + (hasFlag ? "-characters_"+team+"_flag-": "-characters-")
    const animationKey = `player${this.spriteChoice}${this.hasFlag ? `-characters_${this.team}_flag-` : '-characters-'}`

    // frontend 使用 if...else if 处理 x 方向，然后独立的 if 处理 y 方向
    // 注意：frontend 没有停止动画的逻辑，每次移动都会播放动画
    if (this.x < this.target.x) {
      this.x++
      this.anims.play(`${animationKey}right`, true)
    } else if (this.x > this.target.x) {
      this.x--
      this.anims.play(`${animationKey}left`, true)
    }
    
    if (this.y < this.target.y) {
      this.y++
      this.anims.play(`${animationKey}down`, true)
    } else if (this.y > this.target.y) {
      this.y--
      this.anims.play(`${animationKey}up`, true)
    }
  }

  private showStaticImage(): void {
    const animationKey = `player${this.spriteChoice}-characters-down`
    this.anims.play(animationKey, true)
  }

  toPrison(prisonX: number, prisonY: number): void {
    if (!this.mapOffset) return

    this.target.x = this.mapOffset.x + (prisonX * this.mapOffset.tileSize)
    this.target.y = this.mapOffset.y + (prisonY * this.mapOffset.tileSize)
    this.setPosition(this.target.x, this.target.y)
    this.inPrison = true
    this.inPrisonTimeLeft = this.inPrisonDuration
  }

  setCanGoNextTile(canGo: boolean): void {
    // 使用位或操作符累积标志，与老项目保持一致
    // 如果 canGo 是 true，设置为 true；如果是 false，保持原值（不改变）
    // 注意：这里使用位或操作符 |= 的语义
    if (canGo) {
      this.canGoNextTile = true
    }
    // 如果 canGo 是 false，不改变 canGoNextTile 的值
  }

  getStatus() {
    if (!this.mapOffset) {
      return {
        name: this.name,
        team: this.team,
        hasFlag: this.hasFlag,
        posX: 0,
        posY: 0,
        inPrison: this.inPrison,
        inPrisonTimeLeft: this.inPrisonTimeLeft,
        inPrisonDuration: this.inPrisonDuration
      }
    }

    const targetPosX = Math.round((this.target.x - this.mapOffset.x) / this.mapOffset.tileSize)
    const targetPosY = Math.round((this.target.y - this.mapOffset.y) / this.mapOffset.tileSize)

    return {
      name: this.name,
      team: this.team,
      hasFlag: this.hasFlag,
      posX: targetPosX,
      posY: targetPosY,
      inPrison: this.inPrison,
      inPrisonTimeLeft: this.inPrisonTimeLeft,
      inPrisonDuration: this.inPrisonDuration
    }
  }
}

