/**
 * UIComponentManager - UI 组件生命周期管理
 * 负责组件的创建、存储、查找和销毁
 */
import { UIComponent } from '../UIManager'

/**
 * UI 组件管理器
 */
export class UIComponentManager {
  private components: Map<string, UIComponent> = new Map()

  /**
   * 添加组件
   */
  addComponent(id: string, component: UIComponent): void {
    this.components.set(id, component)
  }

  /**
   * 获取组件
   */
  getComponent(id: string): UIComponent | undefined {
    return this.components.get(id)
  }

  /**
   * 移除组件（不销毁）
   */
  removeComponent(id: string): void {
    this.components.delete(id)
  }

  /**
   * 销毁指定组件
   */
  destroyComponent(id: string): void {
    const component = this.components.get(id)
    if (component) {
      component.destroy()
      this.components.delete(id)
    }
  }

  /**
   * 销毁所有组件
   */
  destroyAll(): void {
    this.components.forEach(component => component.destroy())
    this.components.clear()
  }

  /**
   * 获取所有组件 ID
   */
  getComponentIds(): string[] {
    return Array.from(this.components.keys())
  }

  /**
   * 检查组件是否存在
   */
  hasComponent(id: string): boolean {
    return this.components.has(id)
  }
}
