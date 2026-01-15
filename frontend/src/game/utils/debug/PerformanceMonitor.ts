/**
 * 性能监控器
 * 负责 FPS 监控和帧时间统计
 */
import type { PerformanceMetrics } from '@/types'

export class PerformanceMonitor {
  private frameCount = 0
  private lastFpsTime = 0
  private fps = 0
  private frameTimes: number[] = []
  private maxFrameTimeHistory = 60

  tick(): void {
    this.frameCount++
    const now = performance.now()
    
    if (this.lastFpsTime === 0) {
      this.lastFpsTime = now
      return
    }

    const frameTime = now - this.lastFpsTime
    this.frameTimes.push(frameTime)
    
    if (this.frameTimes.length > this.maxFrameTimeHistory) {
      this.frameTimes.shift()
    }

    if (now - this.lastFpsTime >= 1000) {
      this.fps = this.frameCount
      this.frameCount = 0
      this.lastFpsTime = now
    }
  }

  getMetrics(): PerformanceMetrics {
    const avgFrameTime = this.frameTimes.length > 0
      ? this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length
      : 0

    return {
      fps: this.fps,
      frameTime: avgFrameTime,
      renderTime: 0,
      updateTime: 0
    }
  }

  reset(): void {
    this.frameCount = 0
    this.lastFpsTime = 0
    this.fps = 0
    this.frameTimes = []
  }
}
