import Phaser from 'phaser'

export class Boot extends Phaser.Scene {
  constructor() {
    super('Boot')
  }

  preload() {
    // Boot 场景通常用于加载预加载器所需的资源
    // 这里可以加载游戏 logo 或背景等小文件
  }

  create() {
    // 启动预加载场景
    // Boot 场景是第一个场景，会自动启动
    // 然后启动 Preloader 场景开始加载资源
    this.scene.start('Preloader')
  }
}

