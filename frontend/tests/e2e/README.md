# E2E 测试说明

## SocketManager 复杂场景测试

以下场景应该在 E2E 测试中验证（而不是单元测试）：

### 消息格式一致性
- `init` 消息格式（与 backend 一致）
- `status` 消息格式（与 backend 一致）
- `finished` 消息格式（与 backend 一致）
- 接收 `actions` 消息的处理

### 完整游戏流程
1. 连接建立 → 发送 init → 接收确认
2. 游戏循环：发送 status → 接收 actions → 更新状态
3. 游戏结束：发送 finished → 断开连接

### 异常场景
- WebSocket 断线重连
- 消息发送失败重试
- 超时处理
- 并发消息处理
- 网络延迟模拟

### 性能测试
- 高频消息发送（游戏每帧更新）
- 消息队列管理
- 内存泄漏检测

## 运行 E2E 测试

```bash
# 开发模式（可见浏览器）
pnpm test:e2e:headed

# CI 模式（headless）
pnpm test:e2e

# 调试模式
pnpm test:e2e:debug
```

## 编写建议

E2E 测试应该：
1. 启动真实的 WebSocket 服务器
2. 模拟完整的游戏会话
3. 验证前后端通信协议
4. 测试真实的网络条件
