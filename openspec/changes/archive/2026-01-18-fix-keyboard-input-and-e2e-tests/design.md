# 设计文档: 修复键盘输入并增强测试

## Context
### 问题背景
前端从 `fejs` (简单 JS 实现) 重构为 `frontend` (模块化 TypeScript 实现) 过程中，键盘输入处理逻辑发生了变化，导致功能丢失。

### fejs 原始实现
```javascript
// Player.js
constructor(scene, name, x, y, team, spriteChoice = 1, useAWSD = true) {
  // L 队使用 WASD，R 队使用方向键
  if (useAWSD) {
    this.keys = this.scene.awsd_keys;
  } else {
    this.keys = this.scene.cursors;
  }
}

checkInput() {
  // 键盘输入优先
  if (this.keys.left.isDown) moveDirection.x--;
  else if (this.keys.right.isDown) moveDirection.x++;
  // ...
  // 然后才是远程控制
  else if (this.remoteControl == PlayerDirection.LEFT) moveDirection.x--;
  // ...
}
```

### frontend 重构实现
```typescript
// InputManager.ts - 单例，所有玩家共享
constructor(scene: Phaser.Scene) {
  this.cursors = scene.input.keyboard.createCursorKeys();
  this.wasdKeys = scene.input.keyboard.addKeys({ w, a, s, d });
}

// InputHandler.ts - 远程控制优先！
getMoveDirection() {
  let direction = this.inputManager.getCurrentDirection();
  // 远程控制 > 键盘输入
}
```

## Goals / Non-Goals
### Goals
1. 恢复 fejs 的键盘控制功能：L 队 WASD，R 队方向键
2. 恢复 fejs 的输入优先级：键盘输入 > 远程控制
3. 增加全面的 e2e 测试覆盖
4. 保持现有的模块化架构设计

### Non-Goals
- 不改变 InputManager 的观察者模式架构
- 不修改远程控制（WebSocket）的实现
- 不影响 AI 训练模式（纯远程控制）

## Decisions
### Decision 1: 按键绑定配置化
**方案**: 在 InputManager 中支持配置按键绑定，而不是硬编码 WASD + 方向键

```typescript
interface KeyBindings {
  up: number;    // KeyCodes
  down: number;
  left: number;
  right: number;
}

const WASD_BINDINGS: KeyBindings = {
  up: KeyCodes.W,
  left: KeyCodes.A,
  down: KeyCodes.S,
  right: KeyCodes.D
};

const ARROW_BINDINGS: KeyBindings = {
  up: KeyCodes.UP,
  left: KeyCodes.LEFT,
  down: KeyCodes.DOWN,
  right: KeyCodes.RIGHT
};
```

**理由**: 
- 更灵活，未来可支持自定义按键
- 每个 InputManager 实例可以有不同的按键绑定
- 符合 OOP 封装原则

**替代方案**: 
- 创建 `InputManagerWASD` 和 `InputManagerArrows` 子类 → 过度设计
- 在 Player 中硬编码 → 回到 fejs 的问题，违反单一职责原则

### Decision 2: 为每个队伍创建独立 InputManager
**方案**: TeamInitializer 为 L 队和 R 队创建各自的 InputManager 实例

```typescript
const lteamInputManager = new InputManager(scene, WASD_BINDINGS);
const rteamInputManager = new InputManager(scene, ARROW_BINDINGS);

// L 队玩家使用 lteamInputManager
// R 队玩家使用 rteamInputManager
```

**理由**:
- 解决输入冲突问题
- 每个队伍可以独立控制
- 不影响远程控制（AI 模式不使用 InputManager）

**替代方案**:
- 单个 InputManager 处理两套按键 → 复杂度高，职责不清
- 为每个 Player 创建 InputManager → 资源浪费，不必要

### Decision 3: 恢复键盘输入优先级
**方案**: 修改 InputManager 优先级逻辑

```typescript
// InputManager.update()
update(): void {
  // 键盘输入优先
  let newDirection = this.getKeyboardDirection();
  
  // 没有键盘输入时才使用远程控制
  if (newDirection === '' && this.remoteDirection !== '') {
    newDirection = this.remoteDirection;
  }
  
  // ...
}
```

**理由**:
- 与 fejs 保持一致
- 便于手动调试和测试
- AI 训练时不启用键盘输入，不受影响

### Decision 4: E2E 测试策略
**测试层级**:
1. **单元测试**: InputManager 的按键绑定和优先级逻辑
2. **集成测试**: Player + InputManager 的交互
3. **E2E 测试**: 完整的游戏流程，包括键盘控制

**E2E 测试场景**:
- 基础场景: 启动游戏、WASD 移动、方向键移动
- 优先级场景: 键盘输入覆盖远程控制
- 多玩家场景: L 队和 R 队独立控制
- 边界场景: 墙壁碰撞、越界处理
- 状态场景: 暂停、恢复、游戏结束

## Risks / Trade-offs
### Risks
1. **性能风险**: 每帧调用两个 InputManager.update() 而不是一个
   - **缓解**: InputManager 逻辑简单，性能影响可忽略
   - **监控**: 添加性能测试确保 60 FPS

2. **兼容性风险**: 修改输入优先级可能影响现有行为
   - **缓解**: 添加单元测试和 e2e 测试覆盖
   - **回滚**: 保留原有逻辑作为可选配置

### Trade-offs
1. **代码复杂度 vs 功能完整性**: 增加了 InputManager 实例数量，但解决了实际问题
2. **测试时间 vs 测试覆盖**: E2E 测试增加了 CI 时间，但提高了质量保证

## Migration Plan
### 步骤
1. **修复 InputManager**: 支持按键绑定配置和优先级调整
2. **修复 Player**: 接受 InputManager 参数，移除直接键盘访问
3. **修复 TeamInitializer**: 为两个队伍创建独立 InputManager
4. **更新单元测试**: 覆盖新功能
5. **新增 E2E 测试**: 全面测试键盘输入流
6. **手动测试**: 验证 L 队 WASD 和 R 队方向键
7. **部署和监控**: 观察是否有回归问题

### 回滚计划
如果发现严重问题：
1. 暂时禁用键盘输入（设置 `enableKeyboard: false`）
2. 回退到远程控制优先模式
3. 保留 AI 训练功能不受影响

## Open Questions
无
