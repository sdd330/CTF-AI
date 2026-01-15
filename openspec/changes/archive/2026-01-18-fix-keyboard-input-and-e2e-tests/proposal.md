# Change: 修复前端重构后键盘输入bug并增加e2e测试

## Why
在 OOP 重构过程中，前端从 `fejs` 的简单实现迁移到模块化的 `frontend` 实现。经过对比分析发现：

1. **键盘输入bug**: fejs 原始实现支持 L 队使用 WASD 键，R 队使用方向键进行独立控制。重构后所有玩家共享一个 `InputManager` 实例，导致键盘输入无法区分不同队伍的玩家。

2. **输入优先级变化**: fejs 中键盘输入优先于远程控制，重构后变成远程控制优先于键盘输入，这可能影响游戏调试体验。

3. **测试覆盖不足**: 现有 e2e 测试（`game-automation.spec.ts`）只有基础的游戏启动和移动测试，没有全面测试键盘输入、团队独立控制、优先级等关键功能。

## What Changes
### 核心修复
- **修复 InputManager 共享问题**: 创建独立的 InputManager 实例用于键盘控制的玩家，支持 L 队和 R 队使用不同键盘
- **恢复输入优先级**: 将键盘输入优先级调整为高于远程控制（与 fejs 保持一致），便于调试和手动测试
- **修复 Player 构造函数**: 根据 `useAWSD` 参数决定使用 WASD 还是方向键

### E2E 测试增强
- 新增键盘输入流完整测试（WASD 和方向键）
- 新增多玩家独立控制测试
- 新增输入优先级测试（键盘 vs 远程控制）
- 新增游戏状态流转测试（启动、暂停、结束）
- 新增边界条件和错误处理测试

## Impact
- **受影响的规范**: frontend, input-manager, game-testing
- **受影响的代码**: 
  - `frontend/src/game/managers/InputManager.ts` - 支持配置按键绑定
  - `frontend/src/game/objects/Player.ts` - 接受 useAWSD 参数
  - `frontend/src/game/managers/game-state/TeamInitializer.ts` - 为不同队伍创建独立 InputManager
  - `frontend/e2e/` - 新增全面的键盘输入测试
- **破坏性变更**: 无，这是修复 bug 恢复原有功能
- **测试影响**: 需要更新现有测试并新增 e2e 测试用例
