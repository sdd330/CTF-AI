# Change: 重构前端代码以符合文件大小规范

## Why
前端代码有5个文件超过200行限制，违反代码风格规范：
- `Game.ts`: 410行 (2.05x限制)
- `GameStateManager.ts`: 325行 (1.63x限制)
- `InputManager.ts`: 273行 (1.37x限制)
- `GameInitializer.ts`: 245行 (1.23x限制)
- `debug.ts`: 225行 (1.13x限制)

虽然之前的重构已经对大部分模块进行了拆分，但这些核心文件仍然过大，违反了单一职责原则，需要进一步重构为更小、更专注的模块。

## What Changes
- **拆分 Game.ts (410行)**：
  - 提取游戏对象管理到 `game/GameObjectManager.ts` (~80行)
  - 提取游戏流程控制到 `game/GameFlowController.ts` (~100行)
  - 提取分数和旗帜管理到 `game/ScoreManager.ts` (~60行)
  - 保留核心场景生命周期方法在 `Game.ts` (~150行)

- **拆分 GameStateManager.ts (325行)**：
  - 将公共API方法分组到 `game-state/GameStateAPI.ts` (~150行)
  - 保留核心状态管理在 `GameStateManager.ts` (~180行)

- **拆分 InputManager.ts (273行)**：
  - 提取键盘输入处理到 `input/KeyboardInputHandler.ts` (~90行)
  - 提取远程控制到 `input/RemoteInputHandler.ts` (~50行)
  - 提取观察者管理到 `input/InputObserverManager.ts` (~60行)
  - 保留主协调逻辑在 `InputManager.ts` (~120行)

- **拆分 GameInitializer.ts (245行)**：
  - 提取管理器工厂到 `game/ManagerFactory.ts` (~100行)
  - 提取事件设置到 `game/EventSetup.ts` (~90行)
  - 保留主初始化流程在 `GameInitializer.ts` (~100行)

- **拆分 debug.ts (225行)**：
  - 分离 PerformanceMonitor 到 `debug/PerformanceMonitor.ts` (~70行)
  - 分离 Logger 到 `debug/Logger.ts` (~80行)
  - 分离 DebugTools 到 `debug/DebugTools.ts` (~70行)

- 应用 OOP 设计原则：
  - **单一职责**：每个类/文件只负责一个方面
  - **组合优于继承**：使用组合模式而非深度继承
  - **封装**：使用 private 修饰符隐藏内部实现
  - **依赖注入**：通过构造函数传递依赖

- 更新 frontend 规范以记录新的模块结构

## Impact
- 影响规范: `frontend/spec.md` (添加新模块结构要求)
- 影响代码: 5个前端 TypeScript 文件需要重构，创建约13个新文件
- 破坏性变更: 无（内部重构，保留公共 API）
- 测试: 需要更新相关测试以导入新模块
