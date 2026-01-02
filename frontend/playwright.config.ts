import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置文件
 * 用于自动化测试 CTF-AI 游戏
 */
export default defineConfig({
  testDir: './e2e',
  /* 测试超时时间（60秒） */
  timeout: 60 * 1000,
  /* 并行运行测试 */
  fullyParallel: true,
  /* 失败时重试 */
  retries: process.env.CI ? 2 : 0,
  /* 并行工作进程数 */
  workers: process.env.CI ? 1 : undefined,
  /* 报告配置 */
  reporter: 'html',
  /* 共享测试配置 */
  use: {
    /* 基础 URL */
    baseURL: 'http://localhost:8000',
    /* 收集跟踪信息 */
    trace: 'on-first-retry',
    /* 截图配置 */
    screenshot: 'only-on-failure',
    /* 视频配置 */
    video: 'retain-on-failure',
  },

  /* 配置项目 - 只测试 Chromium */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* 运行本地开发服务器 */
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});

