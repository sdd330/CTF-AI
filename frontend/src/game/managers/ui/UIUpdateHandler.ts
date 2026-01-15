/**
 * UIUpdateHandler - UI 状态更新和渲染处理
 * 负责组件的显示、隐藏和更新
 */
import { UIComponent } from '../UIManager'
import { UIComponentManager } from './UIComponentManager'

/**
 * UI 更新处理器
 */
export class UIUpdateHandler {
  private componentManager: UIComponentManager

  constructor(componentManager: UIComponentManager) {
    this.componentManager = componentManager
  }

  /**
   * 更新组件
   */
  updateComponent(id: string, data?: unknown): void {
    const component = this.componentManager.getComponent(id)
    if (component) {
      component.update(data)
    }
  }

  /**
   * 显示组件
   */
  showComponent(id: string): void {
    const component = this.componentManager.getComponent(id)
    if (component) {
      component.show()
    }
  }

  /**
   * 隐藏组件
   */
  hideComponent(id: string): void {
    const component = this.componentManager.getComponent(id)
    if (component) {
      component.hide()
    }
  }
}
