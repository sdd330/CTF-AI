/**
 * 全局类型声明文件
 * 用于测试环境中的全局对象类型扩展
 */

import type Phaser from 'phaser'

declare global {
  // 在 TypeScript 全局声明中，var 是必需的语法
  var Phaser: typeof Phaser
  var WebSocket: typeof WebSocket
}

export {}

