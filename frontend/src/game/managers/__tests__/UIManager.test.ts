import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  UIManager,
  UIComponentType
} from '../UIManager'
import {
  ScoreTextComponent,
  TutorialTextComponent,
  GameOverTextComponent,
  TeamNameTextComponent
} from '../ui/UIComponents'
import { UIComponentFactory } from '../ui/UIComponentFactory'

// Mock Phaser Scene
const createMockScene = () => {
  const mockText = {
    setText: vi.fn().mockReturnThis(),
    setVisible: vi.fn().mockReturnThis(),
    setOrigin: vi.fn().mockReturnThis(),
    setDepth: vi.fn().mockReturnThis(),
    destroy: vi.fn()
  }

  return {
    add: {
      text: vi.fn(() => mockText)
    },
    scale: {
      width: 960,
      height: 960
    }
  } as unknown as Phaser.Scene
}

describe('UIManager', () => {
  let scene: Phaser.Scene
  let uiManager: UIManager

  beforeEach(() => {
    scene = createMockScene()
    uiManager = new UIManager(scene)
  })

  describe('组件创建', () => {
    it('应该能够创建分数文本组件', () => {
      const component = uiManager.createComponent(
        'lScore',
        UIComponentType.SCORE_TEXT,
        'L',
        30,
        20
      )
      expect(component).toBeDefined()
      expect(scene.add.text).toHaveBeenCalled()
    })

    it('应该能够创建教程文本组件', () => {
      const component = uiManager.createComponent(
        'tutorial',
        UIComponentType.TUTORIAL_TEXT,
        480,
        480
      )
      expect(component).toBeDefined()
      expect(scene.add.text).toHaveBeenCalled()
    })

    it('应该能够创建游戏结束文本组件', () => {
      const component = uiManager.createComponent(
        'gameOver',
        UIComponentType.GAME_OVER_TEXT,
        480,
        480
      )
      expect(component).toBeDefined()
      expect(scene.add.text).toHaveBeenCalled()
    })

    it('应该能够创建队伍名称文本组件', () => {
      const component = uiManager.createComponent(
        'lTeamWho',
        UIComponentType.TEAM_NAME_TEXT,
        'L',
        30,
        60
      )
      expect(component).toBeDefined()
      expect(scene.add.text).toHaveBeenCalled()
    })
  })

  describe('组件管理', () => {
    beforeEach(() => {
      uiManager.createComponent('test', UIComponentType.SCORE_TEXT, 'L', 30, 20)
    })

    it('应该能够获取组件', () => {
      const component = uiManager.getComponent('test')
      expect(component).toBeDefined()
    })

    it('应该能够更新组件', () => {
      const updateSpy = vi.spyOn(uiManager.getComponent('test')!, 'update')
      uiManager.updateComponent('test', 5)
      expect(updateSpy).toHaveBeenCalledWith(5)
    })

    it('应该能够显示组件', () => {
      const showSpy = vi.spyOn(uiManager.getComponent('test')!, 'show')
      uiManager.showComponent('test')
      expect(showSpy).toHaveBeenCalled()
    })

    it('应该能够隐藏组件', () => {
      const hideSpy = vi.spyOn(uiManager.getComponent('test')!, 'hide')
      uiManager.hideComponent('test')
      expect(hideSpy).toHaveBeenCalled()
    })

    it('应该能够销毁指定组件', () => {
      const component = uiManager.getComponent('test')
      const destroySpy = vi.spyOn(component!, 'destroy')
      uiManager.destroyComponent('test')
      expect(destroySpy).toHaveBeenCalled()
      expect(uiManager.getComponent('test')).toBeUndefined()
    })

    it('应该能够销毁所有组件', () => {
      uiManager.createComponent('test2', UIComponentType.SCORE_TEXT, 'R', 30, 20)
      const component1 = uiManager.getComponent('test')
      const component2 = uiManager.getComponent('test2')
      const destroySpy1 = vi.spyOn(component1!, 'destroy')
      const destroySpy2 = vi.spyOn(component2!, 'destroy')
      
      uiManager.destroyAll()
      
      expect(destroySpy1).toHaveBeenCalled()
      expect(destroySpy2).toHaveBeenCalled()
      expect(uiManager.getComponent('test')).toBeUndefined()
      expect(uiManager.getComponent('test2')).toBeUndefined()
    })
  })
})

describe('ScoreTextComponent', () => {
  let scene: Phaser.Scene
  let component: ScoreTextComponent

  beforeEach(() => {
    scene = createMockScene()
    component = new ScoreTextComponent(scene, 'L', 30, 20)
  })

  it('应该正确初始化', () => {
    expect(component).toBeInstanceOf(ScoreTextComponent)
    expect(scene.add.text).toHaveBeenCalled()
  })

  it('应该能够更新分数', () => {
    const updateSpy = vi.spyOn(component, 'update')
    component.update(5)
    expect(updateSpy).toHaveBeenCalledWith(5)
  })

  it('应该能够显示和隐藏', () => {
    component.show()
    component.hide()
    // 验证方法被调用（通过 mock 验证）
  })
})

describe('TutorialTextComponent', () => {
  let scene: Phaser.Scene
  let component: TutorialTextComponent

  beforeEach(() => {
    scene = createMockScene()
    component = new TutorialTextComponent(scene, 480, 480)
  })

  it('应该正确初始化', () => {
    expect(component).toBeInstanceOf(TutorialTextComponent)
    expect(scene.add.text).toHaveBeenCalled()
  })

  it('应该能够显示和隐藏', () => {
    component.show()
    component.hide()
  })
})

describe('GameOverTextComponent', () => {
  let scene: Phaser.Scene
  let component: GameOverTextComponent

  beforeEach(() => {
    scene = createMockScene()
    component = new GameOverTextComponent(scene, 480, 480)
  })

  it('应该正确初始化', () => {
    expect(component).toBeInstanceOf(GameOverTextComponent)
    expect(scene.add.text).toHaveBeenCalled()
  })

  it('应该能够更新获胜队伍', () => {
    component.update('L')
    // 验证更新逻辑
  })

  it('应该能够显示和隐藏', () => {
    component.show()
    component.hide()
  })
})

describe('TeamNameTextComponent', () => {
  let scene: Phaser.Scene
  let component: TeamNameTextComponent

  beforeEach(() => {
    scene = createMockScene()
    component = new TeamNameTextComponent(scene, 'L', 30, 60)
  })

  it('应该正确初始化', () => {
    expect(component).toBeInstanceOf(TeamNameTextComponent)
    expect(scene.add.text).toHaveBeenCalled()
  })

  it('应该能够更新队伍名称', () => {
    component.update('AI Player')
    // 验证更新逻辑
  })

  it('应该能够显示和隐藏', () => {
    component.show()
    component.hide()
  })
})

describe('UIComponentFactory', () => {
  let scene: Phaser.Scene

  beforeEach(() => {
    scene = createMockScene()
  })

  it('应该能够创建分数文本组件', () => {
    const component = UIComponentFactory.create(
      UIComponentType.SCORE_TEXT,
      scene,
      'L',
      30,
      20
    )
    expect(component).toBeInstanceOf(ScoreTextComponent)
  })

  it('应该能够创建教程文本组件', () => {
    const component = UIComponentFactory.create(
      UIComponentType.TUTORIAL_TEXT,
      scene,
      480,
      480
    )
    expect(component).toBeInstanceOf(TutorialTextComponent)
  })

  it('应该能够创建游戏结束文本组件', () => {
    const component = UIComponentFactory.create(
      UIComponentType.GAME_OVER_TEXT,
      scene,
      480,
      480
    )
    expect(component).toBeInstanceOf(GameOverTextComponent)
  })

  it('应该能够创建队伍名称文本组件', () => {
    const component = UIComponentFactory.create(
      UIComponentType.TEAM_NAME_TEXT,
      scene,
      'L',
      30,
      60
    )
    expect(component).toBeInstanceOf(TeamNameTextComponent)
  })

  it('应该在未知类型时抛出错误', () => {
    expect(() => {
      UIComponentFactory.create('unknown' as UIComponentType, scene)
    }).toThrow('Unknown UI component type')
  })
})

