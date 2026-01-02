import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      // Mock phaser3spectorjs 模块（Phaser 的可选依赖）
      'phaser3spectorjs': resolve(__dirname, 'src/test/mocks/phaser3spectorjs.ts')
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/e2e/**', // 排除 E2E 测试（使用 Playwright）
      '**/*.config.*',
      '**/*.d.ts'
    ],
    // 减少测试输出日志
    silent: false, // 设置为 true 会完全静默，但会隐藏错误信息
    logLevel: 'warn', // 只显示 warn 和 error 级别的日志
    outputTruncateLength: 80, // 限制输出长度
    outputDiffLines: 5, // 限制 diff 显示行数
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/dist/**',
        '**/e2e/**'
      ]
    },
    server: {
      deps: {
        inline: ['phaser']
      }
    }
  }
})

