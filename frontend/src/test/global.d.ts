/**
 * 全局类型声明文件
 * 用于测试环境中的全局对象类型扩展
 */

import type Phaser from 'phaser'

declare global {
  // eslint-disable-next-line no-var
  var Phaser: typeof Phaser
  // eslint-disable-next-line no-var
  var WebSocket: typeof WebSocket
}

export {}

