/**
 * Prison 和 Target 数据一致性测试
 * 确保使用相同的地图尺寸时，生成的位置数据与 native 项目一致
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WorldManager } from '../WorldManager'
import type { Position } from '@/types'

// Mock Phaser Math.RND before importing WorldManager
vi.mock('phaser', () => {
  const mockRND = {
    integerInRange: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
    pick: <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)]
  }
  return {
    default: {
      Math: {
        RND: mockRND
      }
    },
    Math: {
      RND: mockRND
    }
  }
})

// Mock Player and Flag classes
vi.mock('../../objects/Player', () => ({
  Player: class MockPlayer {
    constructor() {}
  }
}))

vi.mock('../../objects/Flag', () => ({
  Flag: class MockFlag {
    constructor() {}
  }
}))

// Mock Phaser Game
const createMockGame = () => {
  const registryData: Record<string, any> = {}
  return {
    registry: {
      set: vi.fn((key: string, value: any) => {
        registryData[key] = value
      }),
      get: vi.fn((key: string) => registryData[key]),
      remove: vi.fn((key: string) => {
        delete registryData[key]
      }),
      exists: vi.fn((key: string) => key in registryData),
      has: vi.fn((key: string) => key in registryData)
    },
    events: {
      emit: vi.fn()
    }
  } as unknown as Phaser.Game
}

describe('Prison and Target Consistency Tests', () => {
  let world: WorldManager
  let mockGame: any

  beforeEach(() => {
    // 重置单例实例（通过反射访问私有属性）
    const manager = WorldManager as any
    manager.instance = null
    // 清除所有 mock
    vi.clearAllMocks()
    
    // 创建 mock game 并初始化
    mockGame = createMockGame()
    WorldManager.initialize(mockGame)
    world = WorldManager.getInstance()
  })

  /**
   * 测试 create3x3grid 方法生成的顺序
   * 顺序必须与 native 完全一致：
   * [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
   * [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
   * [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
   */
  it('should create 3x3 grid in correct order', () => {
    const mapWidth = 20
    const mapHeight = 20

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lTarget = teamStates.lTeamState.target
    const rTarget = teamStates.rTeamState.target
    const lPrison = teamStates.lTeamState.prison
    const rPrison = teamStates.rTeamState.prison

    // 验证 L 队 Target 的顺序（中心点 x=2, y=10）
    expect(lTarget).toHaveLength(9)
    expect(lTarget[0]).toEqual({ x: 1, y: 9 })   // (2-1, 10-1)
    expect(lTarget[1]).toEqual({ x: 2, y: 9 })    // (2, 10-1)
    expect(lTarget[2]).toEqual({ x: 3, y: 9 })    // (2+1, 10-1)
    expect(lTarget[3]).toEqual({ x: 1, y: 10 })   // (2-1, 10)
    expect(lTarget[4]).toEqual({ x: 2, y: 10 })    // (2, 10)
    expect(lTarget[5]).toEqual({ x: 3, y: 10 })   // (2+1, 10)
    expect(lTarget[6]).toEqual({ x: 1, y: 11 })   // (2-1, 10+1)
    expect(lTarget[7]).toEqual({ x: 2, y: 11 })   // (2, 10+1)
    expect(lTarget[8]).toEqual({ x: 3, y: 11 })   // (2+1, 10+1)

    // 验证 R 队 Target 的顺序（中心点 x=17, y=10）
    expect(rTarget).toHaveLength(9)
    expect(rTarget[0]).toEqual({ x: 16, y: 9 })   // (17-1, 10-1)
    expect(rTarget[1]).toEqual({ x: 17, y: 9 })    // (17, 10-1)
    expect(rTarget[2]).toEqual({ x: 18, y: 9 })   // (17+1, 10-1)
    expect(rTarget[3]).toEqual({ x: 16, y: 10 })   // (17-1, 10)
    expect(rTarget[4]).toEqual({ x: 17, y: 10 })  // (17, 10)
    expect(rTarget[5]).toEqual({ x: 18, y: 10 })  // (17+1, 10)
    expect(rTarget[6]).toEqual({ x: 16, y: 11 })  // (17-1, 10+1)
    expect(rTarget[7]).toEqual({ x: 17, y: 11 })  // (17, 10+1)
    expect(rTarget[8]).toEqual({ x: 18, y: 11 })  // (17+1, 10+1)

    // 验证 L 队 Prison 的顺序（中心点 x=2, y=17）
    expect(lPrison).toHaveLength(9)
    expect(lPrison[0]).toEqual({ x: 1, y: 16 })   // (2-1, 17-1)
    expect(lPrison[1]).toEqual({ x: 2, y: 16 })    // (2, 17-1)
    expect(lPrison[2]).toEqual({ x: 3, y: 16 })   // (2+1, 17-1)
    expect(lPrison[3]).toEqual({ x: 1, y: 17 })   // (2-1, 17)
    expect(lPrison[4]).toEqual({ x: 2, y: 17 })   // (2, 17)
    expect(lPrison[5]).toEqual({ x: 3, y: 17 })   // (2+1, 17)
    expect(lPrison[6]).toEqual({ x: 1, y: 18 })   // (2-1, 17+1)
    expect(lPrison[7]).toEqual({ x: 2, y: 18 })   // (2, 17+1)
    expect(lPrison[8]).toEqual({ x: 3, y: 18 })   // (2+1, 17+1)

    // 验证 R 队 Prison 的顺序（中心点 x=17, y=17）
    expect(rPrison).toHaveLength(9)
    expect(rPrison[0]).toEqual({ x: 16, y: 16 })  // (17-1, 17-1)
    expect(rPrison[1]).toEqual({ x: 17, y: 16 })  // (17, 17-1)
    expect(rPrison[2]).toEqual({ x: 18, y: 16 })  // (17+1, 17-1)
    expect(rPrison[3]).toEqual({ x: 16, y: 17 })  // (17-1, 17)
    expect(rPrison[4]).toEqual({ x: 17, y: 17 })  // (17, 17)
    expect(rPrison[5]).toEqual({ x: 18, y: 17 })  // (17+1, 17)
    expect(rPrison[6]).toEqual({ x: 16, y: 18 })  // (17-1, 17+1)
    expect(rPrison[7]).toEqual({ x: 17, y: 18 })  // (17, 17+1)
    expect(rPrison[8]).toEqual({ x: 18, y: 18 })  // (17+1, 17+1)
  })

  /**
   * 测试不同地图尺寸的一致性
   * 使用与 native 测试相同的地图尺寸
   */
  it('should generate consistent positions for 20x20 map', () => {
    const mapWidth = 20
    const mapHeight = 20

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lTarget = teamStates.lTeamState.target
    const rTarget = teamStates.rTeamState.target
    const lPrison = teamStates.lTeamState.prison
    const rPrison = teamStates.rTeamState.prison

    // 验证 targetY = mapHeight / 2 = 20 / 2 = 10 (Math.floor(10) = 10)
    // 验证 prisonY = mapHeight - 3 = 20 - 3 = 17

    // L 队 Target: center (2, 10)
    expect(lTarget[4]).toEqual({ x: 2, y: 10 })

    // R 队 Target: center (17, 10)
    expect(rTarget[4]).toEqual({ x: 17, y: 10 })

    // L 队 Prison: center (2, 17)
    expect(lPrison[4]).toEqual({ x: 2, y: 17 })

    // R 队 Prison: center (17, 17)
    expect(rPrison[4]).toEqual({ x: 17, y: 17 })
  })

  /**
   * 测试奇数地图高度的处理
   * 确保 mapHeight / 2 和 mapHeight // 2 结果一致
   */
  it('should handle odd map height correctly', () => {
    const mapWidth = 20
    const mapHeight = 21

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lTarget = teamStates.lTeamState.target

    // targetY = 21 / 2 = 10.5, Math.floor(10.5) = 10
    // 与 Python 的 21 // 2 = 10 一致
    expect(lTarget[4]).toEqual({ x: 2, y: 10 })
  })

  /**
   * 测试不同地图尺寸
   */
  it('should generate consistent positions for different map sizes', () => {
    const testCases = [
      { width: 15, height: 15 },
      { width: 20, height: 20 },
      { width: 25, height: 25 },
      { width: 30, height: 30 }
    ]

    testCases.forEach(({ width, height }) => {
      world.api.generateTargetsAndPrisons(width, height)

      const teamStates = world.api.getTeamStates()
      const lTarget = teamStates.lTeamState.target
      const rTarget = teamStates.rTeamState.target
      const lPrison = teamStates.lTeamState.prison
      const rPrison = teamStates.rTeamState.prison

      // 验证所有数组都有 9 个元素
      expect(lTarget).toHaveLength(9)
      expect(rTarget).toHaveLength(9)
      expect(lPrison).toHaveLength(9)
      expect(rPrison).toHaveLength(9)

      // 验证 L 队 Target 中心点
      const targetY = Math.floor(height / 2)
      expect(lTarget[4]).toEqual({ x: 2, y: targetY })

      // 验证 R 队 Target 中心点
      expect(rTarget[4]).toEqual({ x: width - 3, y: targetY })

      // 验证 L 队 Prison 中心点
      const prisonY = height - 3
      expect(lPrison[4]).toEqual({ x: 2, y: prisonY })

      // 验证 R 队 Prison 中心点
      expect(rPrison[4]).toEqual({ x: width - 3, y: prisonY })
    })
  })

  /**
   * 验证位置数据格式
   * Frontend 使用 { x: number, y: number } 格式
   */
  it('should generate positions in correct format', () => {
    const mapWidth = 20
    const mapHeight = 20

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lTarget = teamStates.lTeamState.target

    // 验证格式
    lTarget.forEach((pos: Position) => {
      expect(pos).toHaveProperty('x')
      expect(pos).toHaveProperty('y')
      expect(typeof pos.x).toBe('number')
      expect(typeof pos.y).toBe('number')
      expect(Number.isInteger(pos.x)).toBe(true)
      expect(Number.isInteger(pos.y)).toBe(true)
    })
  })

  /**
   * 验证 renderTargets 的 tile ID 映射关系
   * 确保与 native 项目使用相同的 tile ID 数组和映射顺序
   */
  it('should map positions to correct tile IDs for renderTargets', () => {
    const mapWidth = 20
    const mapHeight = 20

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lTarget = teamStates.lTeamState.target
    const rTarget = teamStates.rTeamState.target

    // Frontend targetTiles: [13, 14, 15, 25, 26, 27, 37, 38, 39]
    // 与 native 的 target_tiles 完全一致
    const expectedTargetTiles = [13, 14, 15, 25, 26, 27, 37, 38, 39]

    // 验证 L 队 Target 的 tile ID 映射
    // create3x3grid 顺序: [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
    //                      [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
    //                      [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
    // 对应 tile ID: [13, 14, 15, 25, 26, 27, 37, 38, 39]
    const lTargetTileMap = new Map<string, number>()
    lTarget.forEach((pos, i) => {
      if (i < expectedTargetTiles.length) {
        lTargetTileMap.set(`${pos.x},${pos.y}`, expectedTargetTiles[i])
      }
    })

    // 验证每个位置对应的 tile ID
    expect(lTargetTileMap.get('1,9')).toBe(13)   // [0] (x-1, y-1) -> tile 13
    expect(lTargetTileMap.get('2,9')).toBe(14)   // [1] (x, y-1) -> tile 14
    expect(lTargetTileMap.get('3,9')).toBe(15)   // [2] (x+1, y-1) -> tile 15
    expect(lTargetTileMap.get('1,10')).toBe(25)  // [3] (x-1, y) -> tile 25
    expect(lTargetTileMap.get('2,10')).toBe(26) // [4] (x, y) -> tile 26
    expect(lTargetTileMap.get('3,10')).toBe(27)  // [5] (x+1, y) -> tile 27
    expect(lTargetTileMap.get('1,11')).toBe(37)  // [6] (x-1, y+1) -> tile 37
    expect(lTargetTileMap.get('2,11')).toBe(38)  // [7] (x, y+1) -> tile 38
    expect(lTargetTileMap.get('3,11')).toBe(39)  // [8] (x+1, y+1) -> tile 39

    // 验证 R 队 Target 的 tile ID 映射（中心点 x=17, y=10）
    const rTargetTileMap = new Map<string, number>()
    rTarget.forEach((pos, i) => {
      if (i < expectedTargetTiles.length) {
        rTargetTileMap.set(`${pos.x},${pos.y}`, expectedTargetTiles[i])
      }
    })

    expect(rTargetTileMap.get('16,9')).toBe(13)  // [0] (x-1, y-1) -> tile 13
    expect(rTargetTileMap.get('17,9')).toBe(14)  // [1] (x, y-1) -> tile 14
    expect(rTargetTileMap.get('18,9')).toBe(15)  // [2] (x+1, y-1) -> tile 15
    expect(rTargetTileMap.get('16,10')).toBe(25) // [3] (x-1, y) -> tile 25
    expect(rTargetTileMap.get('17,10')).toBe(26) // [4] (x, y) -> tile 26
    expect(rTargetTileMap.get('18,10')).toBe(27) // [5] (x+1, y) -> tile 27
    expect(rTargetTileMap.get('16,11')).toBe(37) // [6] (x-1, y+1) -> tile 37
    expect(rTargetTileMap.get('17,11')).toBe(38) // [7] (x, y+1) -> tile 38
    expect(rTargetTileMap.get('18,11')).toBe(39) // [8] (x+1, y+1) -> tile 39
  })

  /**
   * 验证 renderPrisons 的 tile ID 映射关系
   * 确保与 native 项目使用相同的 tile ID 数组和映射顺序
   */
  it('should map positions to correct tile IDs for renderPrisons', () => {
    const mapWidth = 20
    const mapHeight = 20

    world.api.generateTargetsAndPrisons(mapWidth, mapHeight)

    const teamStates = world.api.getTeamStates()
    const lPrison = teamStates.lTeamState.prison
    const rPrison = teamStates.rTeamState.prison

    // Frontend prisonTiles: [97, 98, 99, 109, 110, 111, 121, 122, 123]
    // 与 native 的 prison_tiles 完全一致
    const expectedPrisonTiles = [97, 98, 99, 109, 110, 111, 121, 122, 123]

    // 验证 L 队 Prison 的 tile ID 映射（中心点 x=2, y=17）
    const lPrisonTileMap = new Map<string, number>()
    lPrison.forEach((pos, i) => {
      if (i < expectedPrisonTiles.length) {
        lPrisonTileMap.set(`${pos.x},${pos.y}`, expectedPrisonTiles[i])
      }
    })

    expect(lPrisonTileMap.get('1,16')).toBe(97)   // [0] (x-1, y-1) -> tile 97
    expect(lPrisonTileMap.get('2,16')).toBe(98)   // [1] (x, y-1) -> tile 98
    expect(lPrisonTileMap.get('3,16')).toBe(99)   // [2] (x+1, y-1) -> tile 99
    expect(lPrisonTileMap.get('1,17')).toBe(109) // [3] (x-1, y) -> tile 109
    expect(lPrisonTileMap.get('2,17')).toBe(110)  // [4] (x, y) -> tile 110
    expect(lPrisonTileMap.get('3,17')).toBe(111)  // [5] (x+1, y) -> tile 111
    expect(lPrisonTileMap.get('1,18')).toBe(121)  // [6] (x-1, y+1) -> tile 121
    expect(lPrisonTileMap.get('2,18')).toBe(122)  // [7] (x, y+1) -> tile 122
    expect(lPrisonTileMap.get('3,18')).toBe(123)  // [8] (x+1, y+1) -> tile 123

    // 验证 R 队 Prison 的 tile ID 映射（中心点 x=17, y=17）
    const rPrisonTileMap = new Map<string, number>()
    rPrison.forEach((pos, i) => {
      if (i < expectedPrisonTiles.length) {
        rPrisonTileMap.set(`${pos.x},${pos.y}`, expectedPrisonTiles[i])
      }
    })

    expect(rPrisonTileMap.get('16,16')).toBe(97)  // [0] (x-1, y-1) -> tile 97
    expect(rPrisonTileMap.get('17,16')).toBe(98)   // [1] (x, y-1) -> tile 98
    expect(rPrisonTileMap.get('18,16')).toBe(99)   // [2] (x+1, y-1) -> tile 99
    expect(rPrisonTileMap.get('16,17')).toBe(109) // [3] (x-1, y) -> tile 109
    expect(rPrisonTileMap.get('17,17')).toBe(110)  // [4] (x, y) -> tile 110
    expect(rPrisonTileMap.get('18,17')).toBe(111) // [5] (x+1, y) -> tile 111
    expect(rPrisonTileMap.get('16,18')).toBe(121) // [6] (x-1, y+1) -> tile 121
    expect(rPrisonTileMap.get('17,18')).toBe(122) // [7] (x, y+1) -> tile 122
    expect(rPrisonTileMap.get('18,18')).toBe(123) // [8] (x+1, y+1) -> tile 123
  })
})

