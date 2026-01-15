<template>
  <div class="map-demo">
    <div class="demo-header">
      <h1>MapManager 测试页面</h1>
      <div class="nav-links">
        <router-link to="/">返回游戏</router-link>
      </div>
    </div>
    <div id="map-demo-container" class="map-container"></div>
    <div class="demo-info">
      <div class="info-section">
        <h3>地图信息</h3>
        <div v-if="mapInfo">
          <p>地图大小: {{ mapInfo.mapWidth }}x{{ mapInfo.mapHeight }}</p>
          <p>瓦片大小: {{ mapInfo.tileSize }}</p>
          <p>中心位置: ({{ mapInfo.centerX }}, {{ mapInfo.centerY }})</p>
        </div>
        <div v-else>
          <p>正在加载地图...</p>
        </div>
        <div class="controls-hint">
          <h4>键盘控制</h4>
          <p><strong>L队:</strong> W/A/S/D</p>
          <p><strong>R队:</strong> ↑/↓/←/→</p>
        </div>
      </div>
      
      <div class="info-section" v-if="gameElements">
        <h3>游戏元素</h3>
        <div class="team-info">
          <div class="team-section">
            <h4>L队 (左侧)</h4>
            <p>旗帜数量: {{ gameElements.lFlags }}</p>
            <p>玩家数量: {{ gameElements.lPlayers }}</p>
            <p>目标区域: {{ gameElements.lTarget }}</p>
            <p>监狱区域: {{ gameElements.lPrison }}</p>
          </div>
          <div class="team-section">
            <h4>R队 (右侧)</h4>
            <p>旗帜数量: {{ gameElements.rFlags }}</p>
            <p>玩家数量: {{ gameElements.rPlayers }}</p>
            <p>目标区域: {{ gameElements.rTarget }}</p>
            <p>监狱区域: {{ gameElements.rPrison }}</p>
          </div>
        </div>
        <div class="obstacles-info">
          <h4>障碍物</h4>
          <p>障碍物1 (单瓦片): <span style="color: #ffa500;">{{ gameElements.obstacles1 }}</span> 个</p>
          <p>障碍物2 (双瓦片): <span style="color: #ff6b6b;">{{ gameElements.obstacles2 }}</span> 个</p>
          <p style="font-size: 10px; margin-top: 5px; opacity: 0.7;">
            <span style="color: #ffa500;">■</span> 橙色 = 单瓦片障碍物<br>
            <span style="color: #ff6b6b;">■</span> 红色 = 双瓦片障碍物
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import Phaser from 'phaser'
import { MapManager } from '@/game/managers/MapManager'
import { WorldManager } from '@/game/managers/WorldManager'
import { UIManager } from '@/game/managers/UIManager'
import { Player } from '@/game/objects/Player'
import ASSETS from '@/game/config/assets'

const game = ref<Phaser.Game | null>(null)
const mapInfo = ref<{
  mapWidth: number
  mapHeight: number
  tileSize: number
  centerX: number
  centerY: number
} | null>(null)

const gameElements = ref<{
  lFlags: number
  rFlags: number
  lPlayers: number
  rPlayers: number
  lTarget: string
  rTarget: string
  lPrison: string
  rPrison: string
  obstacles1: number
  obstacles2: number
} | null>(null)

// Boot 场景 - 第一个启动的场景
class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' })
  }

  preload() {
    // Boot 场景通常用于加载预加载器所需的资源
    // 这里可以加载游戏 logo 或背景等小文件
    // 在 MapDemo 中不需要加载额外资源
  }

  create() {
    // 启动预加载场景
    // Boot 场景是第一个场景，会自动启动
    // 然后启动 PreloadScene 场景开始加载资源
    console.log('[MapDemo] Boot 场景启动，切换到 PreloadScene')
    this.scene.start('PreloadScene')
  }
}

// 预加载场景
class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: 'PreloadScene' })
  }

  preload() {
    // 加载所有资源
    console.log('[MapDemo] 开始加载资源...')
    
    // 加载图片
    if (ASSETS.image) {
      Object.values(ASSETS.image).forEach(asset => {
        this.load.image(asset.key, asset.args[0] as string)
      })
    }
    
    // 加载精灵表
    if (ASSETS.spritesheet) {
      Object.values(ASSETS.spritesheet).forEach(asset => {
        const args = asset.args as [string, { frameWidth: number; frameHeight: number }]
        this.load.spritesheet(asset.key, args[0], args[1])
      })
    }
    
    // 加载地图
    if (ASSETS.tilemapTiledJSON) {
      Object.values(ASSETS.tilemapTiledJSON).forEach(asset => {
        this.load.tilemapTiledJSON(asset.key, asset.args[0] as string)
      })
    }
  }

  create() {
    console.log('[MapDemo] 资源加载完成，切换到 MapScene')
    this.scene.start('MapScene')
  }
}

// 地图测试场景
class MapScene extends Phaser.Scene {
  private mapManager!: MapManager
  private gameState!: WorldManager
  private uiManager!: UIManager

  constructor() {
    super({ key: 'MapScene' })
  }
  
  // 实现 ISceneWithMapMethods 接口
  // 参考 Game.ts：直接调用 MapManager.getMapOffset()
  getMapOffset(): { x: number; y: number; width: number; height: number; tileSize: number } {
    return this.mapManager.getMapOffset()
  }
  
  isWall(x: number, y: number): boolean {
    // 参考 frontend/src/scenes/Game.js 的 isWall 方法
    // frontend 使用: this.levelLayer.getTileAtWorldXY(x, y, true)
    // 直接使用 MapManager 的 isWall 方法，它内部使用 levelLayer.getTileAtWorldXY
    return this.mapManager.isWall(x, y)
  }

  async create() {
    console.log('[MapDemo] MapScene create() 被调用')
    
    // 初始化 WorldManager
    try {
      this.gameState = WorldManager.getInstance()
    } catch {
      WorldManager.initialize(this.game)
      this.gameState = WorldManager.getInstance()
    }
    
    // 从 WorldManager 加载游戏配置
    await this.world.loadConfig('game_config.json')
    
    // 初始化 UI 管理器（用于动画初始化）
    this.uiManager = new UIManager(this)
    
    // 初始化动画（必须在创建玩家之前）
    this.uiManager.initAnimations()
    
    // 初始化 MapManager
    this.mapManager = MapManager.getInstance()
    
    // 初始化渲染器（地图参数从 WorldManager 获取）
    this.mapManager.initializeRenderer(this)
    
    // 生成地图（只生成地图数据：墙壁和障碍物）
    this.mapManager.generateMap()
    
    // 生成 TeamStates（由 WorldManager 统一管理）
    const obstacles = this.mapManager.getObstacles()
    this.world.generateTeamStates(obstacles, this.mapManager)
    
    // 创建图层
    this.mapManager.createGroundLayer()
    this.mapManager.createLevelLayer()
    
    // 渲染地图（包括障碍物、墙壁、监狱、目标区域）
    this.mapManager.renderMap()
    
    // 创建边界线（中间线）
    const mapParams = this.mapManager.getMapParams()
    const startY = mapParams.mapY
    const endY = mapParams.mapY + mapParams.mapHeight * mapParams.tileSize
    this.mapManager.createBoundaryLayer(startY, endY)
    
    // 初始化团队元素（使用 WorldManager）
    // 在 MapDemo 中，我们不需要 PhysicsManager 的完整功能，只提供一个模拟的 addPhysicsBody
    this.world.initTeams(this, this.mapManager, { addPhysicsBody: () => {} })
    
    // 获取团队状态用于调试
    const teamStates = this.world.getTeamStates()
    const mapOffset = this.getMapOffset()
    
    // 确保所有玩家可以移动（初始化 canGoNextTile）
    const lteamPlayers = this.world.getLTeamPlayers()
    if (lteamPlayers) {
      lteamPlayers.getChildren().forEach((child) => {
      const player = child as Player
      if (player) {
        player.setCanGoNextTile(true)
        const playerData = teamStates.lTeamState.players.find(p => p.name === player.name)
        console.log(`[MapDemo] L队玩家 ${player.name} 位置:`, {
          tileX: playerData?.x,
          tileY: playerData?.y,
          worldX: player.x,
          worldY: player.y,
          targetX: player.target.x,
          targetY: player.target.y,
          expectedWorldX: mapOffset.x + (playerData?.x || 0) * mapOffset.tileSize,
          expectedWorldY: mapOffset.y + (playerData?.y || 0) * mapOffset.tileSize,
          mapOffset
        })
      }
      })
    }
    const rteamPlayers = this.world.getRTeamPlayers()
    if (rteamPlayers) {
      rteamPlayers.getChildren().forEach((child) => {
      const player = child as Player
      if (player) {
        player.setCanGoNextTile(true)
        const playerData = teamStates.rTeamState.players.find(p => p.name === player.name)
        console.log(`[MapDemo] R队玩家 ${player.name} 位置:`, {
          tileX: playerData?.x,
          tileY: playerData?.y,
          worldX: player.x,
          worldY: player.y,
          targetX: player.target.x,
          targetY: player.target.y,
          expectedWorldX: mapOffset.x + (playerData?.x || 0) * mapOffset.tileSize,
          expectedWorldY: mapOffset.y + (playerData?.y || 0) * mapOffset.tileSize,
          mapOffset
        })
      }
      })
    }
    
    // 更新地图信息
    const params = this.mapManager.getMapParams()
    mapInfo.value = {
      mapWidth: params.mapWidth,
      mapHeight: params.mapHeight,
      tileSize: params.tileSize,
      centerX: params.centerX,
      centerY: params.centerY
    }
    
    console.log('[MapDemo] 地图创建完成', mapInfo.value)
    
    // 更新游戏元素信息（只显示地图相关信息）
    // teamStates 已在上面获取，直接使用
    gameElements.value = {
      lFlags: teamStates.lTeamState.flags.length,
      rFlags: teamStates.rTeamState.flags.length,
      lPlayers: teamStates.lTeamState.players.length,
      rPlayers: teamStates.rTeamState.players.length,
      lTarget: `(${teamStates.lTeamState.target[0].x}, ${teamStates.lTeamState.target[0].y})`,
      rTarget: `(${teamStates.rTeamState.target[0].x}, ${teamStates.rTeamState.target[0].y})`,
      lPrison: `(${teamStates.lTeamState.prison[0].x}, ${teamStates.lTeamState.prison[0].y})`,
      rPrison: `(${teamStates.rTeamState.prison[0].x}, ${teamStates.rTeamState.prison[0].y})`,
      obstacles1: obstacles.obstacles1.length,
      obstacles2: obstacles.obstacles2.length
    }
    
    // 添加控制说明
    this.addControlsInfo()
  }
  
  update(_time: number, delta: number): void {
    // 更新所有玩家（处理键盘输入和移动）
    const EPSILON = 0.1
    let playersReady = 0
    let totalPlayers = 0
    
    // 从 WorldManager 获取玩家组
    const lteamPlayers = this.world.getLTeamPlayers()
    const rteamPlayers = this.world.getRTeamPlayers()
    
    // 检查所有玩家是否都到达目标位置
    if (lteamPlayers) {
      lteamPlayers.getChildren().forEach((child) => {
        const player = child as Player
        if (player) {
          totalPlayers++
          const dx = Math.abs(player.x - player.target.x)
          const dy = Math.abs(player.y - player.target.y)
          if (dx < EPSILON && dy < EPSILON) {
            playersReady++
          }
        }
      })
    }
    
    if (rteamPlayers) {
      rteamPlayers.getChildren().forEach((child) => {
        const player = child as Player
        if (player) {
          totalPlayers++
          const dx = Math.abs(player.x - player.target.x)
          const dy = Math.abs(player.y - player.target.y)
          if (dx < EPSILON && dy < EPSILON) {
            playersReady++
          }
        }
      })
    }
    
    // 只有当所有玩家都到达目标位置时，才允许移动到下一个瓦片
    const canGoNextTile = playersReady === totalPlayers
    
    // 更新所有玩家
    if (lteamPlayers) {
      lteamPlayers.getChildren().forEach((child) => {
        const player = child as Player
        if (player && typeof player.update === 'function') {
          player.setCanGoNextTile(canGoNextTile)
          player.update(_time, delta)
        }
      })
    }
    
    if (rteamPlayers) {
      rteamPlayers.getChildren().forEach((child) => {
        const player = child as Player
        if (player && typeof player.update === 'function') {
          player.setCanGoNextTile(canGoNextTile)
          player.update(_time, delta)
        }
      })
    }
  }
  
  private addControlsInfo(): void {
    // 添加控制说明文字
    const controlsText = this.add.text(
      this.scale.width / 2,
      30,
      '键盘控制: W/A/S/D 控制 L队玩家 | 方向键控制 R队玩家',
      {
        fontSize: '16px',
        color: '#ffffff',
        backgroundColor: '#000000',
        padding: { x: 10, y: 5 }
      }
    )
    controlsText.setOrigin(0.5)
    controlsText.setDepth(200)
    controlsText.setScrollFactor(0) // 固定位置，不随相机移动
    
    // 添加提示：点击玩家来选择控制
    const hintText = this.add.text(
      this.scale.width / 2,
      60,
      '提示: L队使用 WASD | R队使用方向键',
      {
        fontSize: '14px',
        color: '#74b9ff',
        backgroundColor: '#000000',
        padding: { x: 10, y: 5 }
      }
    )
    hintText.setOrigin(0.5)
    hintText.setDepth(200)
    hintText.setScrollFactor(0)
  }
}

onMounted(() => {
  const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    width: 960,
    height: 640,
    parent: 'map-demo-container',
    backgroundColor: '#2d3436',
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    physics: {
      default: 'arcade',
      arcade: {
        debug: false,
        gravity: { x: 0, y: 0 }
      }
    },
    scene: [BootScene, PreloadScene, MapScene]
  }

  const phaserGame = new Phaser.Game(config)
  game.value = phaserGame as unknown as Phaser.Game
})

onUnmounted(() => {
  if (game.value) {
    game.value.destroy(true)
    game.value = null
  }
})
</script>

<style scoped>
.map-demo {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  color: #fff;
}

.demo-header {
  padding: 20px;
  background: #2d3436;
  border-bottom: 2px solid #636e72;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.demo-header h1 {
  margin: 0;
  font-size: 24px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: #74b9ff;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  background: #0984e3;
  transition: background 0.3s;
}

.nav-links a:hover {
  background: #74b9ff;
}

.map-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
}

.demo-info {
  padding: 20px;
  background: #2d3436;
  border-top: 2px solid #636e72;
  display: flex;
  gap: 30px;
  max-height: 200px;
  overflow-y: auto;
}

.info-section {
  flex: 1;
}

.info-section h3 {
  margin-top: 0;
  color: #74b9ff;
  font-size: 18px;
}

.info-section h4 {
  margin: 10px 0 5px 0;
  color: #55efc4;
  font-size: 14px;
}

.info-section p {
  margin: 5px 0;
  font-family: monospace;
  font-size: 12px;
}

.team-info {
  display: flex;
  gap: 20px;
}

.team-section {
  flex: 1;
  padding: 10px;
  background: rgba(116, 185, 255, 0.1);
  border-radius: 4px;
}

.obstacles-info {
  margin-top: 10px;
  padding: 10px;
  background: rgba(255, 165, 0, 0.1);
  border-radius: 4px;
  border-left: 3px solid #ffa500;
}

.controls-hint {
  margin-top: 15px;
  padding: 10px;
  background: rgba(116, 185, 255, 0.1);
  border-radius: 4px;
  border-left: 3px solid #74b9ff;
}

.controls-hint h4 {
  margin: 0 0 8px 0;
  color: #74b9ff;
  font-size: 14px;
}

.controls-hint p {
  margin: 4px 0;
  font-size: 12px;
}

</style>

