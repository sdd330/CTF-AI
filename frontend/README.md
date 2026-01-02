# CTF-AI Frontend

基于 Vue 3.5 + TypeScript + Vite + Phaser 3 的现代化前端项目。

## 技术栈

- **Vue 3.5** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript 超集
- **Vite** - 下一代前端构建工具
- **Phaser 3.85+** - HTML5 游戏框架
- **Playwright** - E2E 自动化测试

## 快速开始

### 安装依赖

```bash
# 安装 pnpm (如果还没有安装)
npm install -g pnpm

# 安装依赖
pnpm install

# 安装 Playwright 浏览器（用于 E2E 测试）
npx playwright install
```

### 运行项目

```bash
# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 预览生产构建
pnpm preview
```

### 运行测试

```bash
# 单元测试
pnpm test

# E2E 测试（UI 模式，推荐）
pnpm test:e2e:ui

# E2E 测试（命令行模式）
pnpm test:e2e

# E2E 测试（调试模式）
pnpm test:e2e:debug
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # Vue 组件
│   ├── game/                # 游戏核心代码
│   │   ├── config/          # 配置文件
│   │   ├── managers/        # 管理器模块
│   │   │   ├── InputManager.ts      # 输入管理（观察者+策略模式）
│   │   │   ├── UIManager.ts         # UI 管理（工厂+组件化）
│   │   │   ├── MapManager.ts        # 地图管理
│   │   │   ├── SocketManager.ts     # Socket 管理（单例+发布订阅）
│   │   │   └── GameStateManager.ts  # 游戏状态管理（统一管理）
│   │   ├── objects/         # 游戏对象（Player, Flag）
│   │   └── scenes/          # Phaser 场景（Boot, Preloader, Game, GameOver）
│   └── main.ts              # 入口文件
├── e2e/                     # E2E 测试
│   ├── game-automation.spec.ts    # 基础自动化测试
│   └── game-advanced.spec.ts      # 高级自动化测试
├── public/
│   ├── game_config.json     # 游戏配置（服务器地址等）
│   └── assets/              # 游戏资源
└── playwright.config.ts     # Playwright 配置
```

## 核心设计模式

### 管理器模块

- **InputManager**: 输入管理（观察者+策略模式）
- **UIManager**: UI 管理（工厂+组件化）
- **MapManager**: 地图管理（组合+享元模式）
- **SocketManager**: Socket 管理（单例+发布订阅）
- **GameStateManager**: 游戏状态管理（统一管理游戏状态和流程）

## 游戏状态管理

### GameStateManager 使用

使用 Phaser Registry 统一管理所有游戏状态：

```typescript
import { GameStateManager } from '@/game/managers/GameStateManager'

// 获取状态管理器实例
const gameState = GameStateManager.getInstance()

// 获取当前状态
const state = gameState.getState()

// 更新状态
gameState.startGame()
gameState.updateLTeamScore(10)

// 订阅状态变化
const unsubscribe = gameState.onStateChange((state) => {
  console.log('游戏状态:', state.gameStarted)
})
```

### 游戏流程状态

流程：`loading → ready → playing → ended`

```typescript
// 发送流程事件
GameStateManager.sendFlowEvent({ type: 'ASSETS_LOADED' })
GameStateManager.sendFlowEvent({ type: 'CONFIG_LOADED' })
GameStateManager.sendFlowEvent({ type: 'START_GAME' })
GameStateManager.sendFlowEvent({ type: 'END_GAME', winner: 'L' })
```

### 状态查询

```typescript
import { gameFlowQueries } from '@/game/managers/GameStateManager'

const state = GameStateManager.getInstance().getState()

if (gameFlowQueries.isLoading(state)) {
  console.log('正在加载...')
}
if (gameFlowQueries.isPlaying(state)) {
  console.log('游戏中...')
}
```

## E2E 自动化测试

### 测试功能

- ✅ 游戏启动测试（按空格键）
- ✅ 玩家移动测试（WASD 键控制）
- ✅ 抢旗功能测试
- ✅ 完整游戏流程测试
- ✅ 策略测试（进攻/防守）
- ✅ 压力测试和边界测试

### 运行 E2E 测试

```bash
# UI 模式（推荐，可以看到测试执行过程）
pnpm test:e2e:ui

# 命令行模式
pnpm test:e2e

# 调试模式
pnpm test:e2e:debug

# 显示浏览器运行
pnpm test:e2e:headed

# 运行特定测试文件
npx playwright test game-automation.spec.ts

# 运行特定测试用例
npx playwright test -g "应该能够启动游戏"
```

### 测试配置

- **测试目录**: `./e2e`
- **基础 URL**: `http://localhost:8000`
- **自动启动开发服务器**: 测试会自动启动 `pnpm dev`
- **浏览器**: 支持 Chromium、Firefox 和 WebKit

### 测试结果

- **HTML 报告**: `playwright-report/index.html`
- **截图**: `test-results/screenshots/`
- **视频**: `test-results/`（失败时）

查看 HTML 报告：
```bash
npx playwright show-report
```

### 注意事项

1. **后端服务器**: 确保后端服务器正在运行（默认端口 34712）
2. **游戏加载**: 测试包含适当的等待时间，确保游戏完全加载
3. **画布聚焦**: 测试会自动聚焦游戏画布以接收键盘输入
4. **移动序列**: 抢旗测试中的移动序列可能需要根据实际地图布局调整

## 开发说明

### 模块间协作

1. **InputManager** → 处理玩家输入，通知观察者
2. **UIManager** → 管理所有 UI 组件，响应状态变化
3. **MapManager** → 管理地图渲染和碰撞检测
4. **SocketManager** → 处理网络通信，发布事件
5. **GameStateManager** → 统一管理游戏状态和流程

### Game 场景整合

`Game.ts` 作为主游戏场景，整合了所有管理器模块：
- 初始化各个管理器
- 协调各模块之间的协作
- 处理游戏逻辑和状态更新

## 配置说明

### 游戏配置

`public/game_config.json` 包含：
- 队伍配置（名称、服务器地址）
- 游戏设置（玩家数量、旗帜数量、地图大小）
- WebSocket 服务器地址

### 注意事项

1. 确保 `game_config.json` 文件存在于 `public` 目录
2. WebSocket 服务器地址在 `game_config.json` 中配置
3. 游戏资源文件需要放在 `public/assets` 目录下

## 故障排除

### E2E 测试问题

**测试超时**: 增加 `playwright.config.ts` 中的 `timeout` 配置

**游戏未加载**: 确保开发服务器和后端服务器正在运行

**键盘输入无效**: 确保画布已聚焦、游戏已完全加载、游戏未暂停

**找不到浏览器**: 运行 `npx playwright install`

### 开发问题

**端口被占用**: 检查是否有其他进程占用 8000 端口，或修改配置

**资源加载失败**: 检查 `public/assets` 目录下的资源文件是否存在

## 相关文档

- [Playwright 官方文档](https://playwright.dev)
- [Phaser 3 文档](https://phaser.io/docs)
- [Vue 3 文档](https://vuejs.org)
- [Vite 文档](https://vitejs.dev)
