import Phaser from 'phaser'
import type { Team, Direction, PlayerStatus } from '@/types'
import type { WorldManager } from '../managers/WorldManager'
import ASSETS from '../config/assets'
import { PlayerMovement } from './player/PlayerMovement'
import { PlayerAnimation } from './player/PlayerAnimation'
import { PlayerStateManager } from './player/PlayerStateManager'
import type { InputManager } from '../managers/InputManager'

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
  private world: WorldManager
  public target: { x: number; y: number } = { x: 0, y: 0 }
  public name: string
  public team: Team
  public spriteChoice: number
  public remoteControl: Direction | null = null
  public plannedPath: Array<{ x: number; y: number }> | null = null

  public get inPrison(): boolean {
    return this.stateManager.getInPrison()
  }
  public set inPrison(value: boolean) {
    if (value) {
      this.stateManager.toPrison()
    } else {
      this.stateManager.freeFromPrison()
    }
  }

  public get inPrisonTimeLeft(): number {
    return this.stateManager.getStatus(this.mapOffset, this.target.x, this.target.y).inPrisonTimeLeft
  }
  public set inPrisonTimeLeft(value: number) {
    this.stateManager.setInPrisonTimeLeft(value)
  }

  public get inPrisonDuration(): number {
    return 20000 // 常量
  }

  public get hasFlag(): boolean {
    return this.stateManager.getHasFlag()
  }
  public set hasFlag(value: boolean) {
    if (value) {
      this.stateManager.collectFlag()
    } else {
      this.stateManager.dropFlag()
    }
  }

  private movement: PlayerMovement
  private animation: PlayerAnimation
  private stateManager: PlayerStateManager
  private accumulator: number = 0
  private mapOffset: { x: number; y: number; tileSize: number } | null = null

  constructor(
    world: WorldManager,
    scene: Phaser.Scene,
    name: string,
    x: number,
    y: number,
    team: Team,
    spriteChoice: number = 1,
    inputManager: InputManager | null = null
  ) {
    const frameIndex = (spriteChoice - 1) * 12 + 1
    super(scene, 0, 0, ASSETS.spritesheet!.characters.key, frameIndex)

    this.world = world
    scene.add.existing(this)
    scene.physics.add.existing(this)

    this.name = name
    this.team = team
    this.spriteChoice = spriteChoice

    const sceneWithMap = scene as Phaser.Scene & ISceneWithMapMethods
    if (sceneWithMap.getMapOffset) {
      this.mapOffset = sceneWithMap.getMapOffset()
      this.target.x = this.mapOffset.x + (x * this.mapOffset.tileSize)
      this.target.y = this.mapOffset.y + (y * this.mapOffset.tileSize)
      this.setPosition(this.target.x, this.target.y)
    }

    this.setCollideWorldBounds(true)
    this.setDepth(100)

    // 使用 InputManager 而不是直接创建键盘输入
    this.stateManager = new PlayerStateManager(name, team)
    this.movement = new PlayerMovement(this, scene, this.target, this.mapOffset, inputManager)
    this.animation = new PlayerAnimation(this, spriteChoice, team)
  }

  collectFlag(): void {
    this.stateManager.collectFlag()
    this.animation.setHasFlag(true)
  }

  dropFlag(): void {
    this.stateManager.dropFlag()
    this.animation.setHasFlag(false)
  }

  setRemoteControl(remoteControl: Direction | null): void {
    if (remoteControl && remoteControl !== '') {
      console.log(`[Player ${this.name}] setRemoteControl: ${remoteControl}`)
    }
    this.remoteControl = remoteControl
    this.movement.setRemoteControl(remoteControl)
  }

  setPlannedPath(path: Array<{ x: number; y: number }> | null): void {
    this.plannedPath = path
    this.movement.setPlannedPath(path)
  }

  update(_time: number, delta: number): void {
    if (!this.mapOffset) return

    const frameDuration = 300 / this.mapOffset.tileSize
    this.accumulator += delta

    while (this.accumulator > frameDuration) {
      this.accumulator -= frameDuration
      
      this.stateManager.updatePrisonTime(frameDuration)
      
      if (!this.stateManager.getInPrison()) {
        this.movement.checkInput()
        this.movement.move()
        const target = this.movement.getTarget()
        this.animation.updateAnimation(target.x, target.y, this.x, this.y)
      } else {
        this.animation.showStaticImage()
      }
    }
  }

  toPrison(prisonX: number, prisonY: number): void {
    if (!this.mapOffset) return

    const targetX = this.mapOffset.x + (prisonX * this.mapOffset.tileSize)
    const targetY = this.mapOffset.y + (prisonY * this.mapOffset.tileSize)
    this.movement.setTarget(targetX, targetY)
    this.setPosition(targetX, targetY)
    this.stateManager.toPrison()
  }

  setCanGoNextTile(canGo: boolean): void {
    this.movement.setCanGoNextTile(canGo)
  }

  getStatus(): PlayerStatus {
    return this.stateManager.getStatus(this.mapOffset, this.target.x, this.target.y)
  }
}

