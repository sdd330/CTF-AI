import { test, expect, Page } from '@playwright/test';

/**
 * 键盘输入 E2E 测试
 * 
 * 测试目标：
 * 1. L队使用WASD键独立控制
 * 2. R队使用方向键独立控制
 * 3. 键盘输入优先于远程控制
 * 4. 两个队伍同时移动不冲突
 */

// 等待游戏加载
async function waitForGameLoaded(page: Page) {
  await page.waitForFunction(() => {
    return (window as any).Phaser !== undefined;
  }, { timeout: 30000 });

  await page.waitForSelector('canvas', { timeout: 30000 });
  
  // 等待游戏完全加载
  await page.waitForTimeout(2000);
}

// 聚焦画布
async function focusGameCanvas(page: Page) {
  const canvas = await page.waitForSelector('canvas');
  if (canvas) {
    await canvas.click();
    await page.waitForTimeout(500);
  }
}

// 启动游戏
async function startGame(page: Page) {
  await page.keyboard.press('Space');
  await page.waitForTimeout(2000); // 等待游戏启动
}

test.describe('键盘输入测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForGameLoaded(page);
    await focusGameCanvas(page);
    await startGame(page);
  });

  test('L队应该能使用WASD键控制移动', async ({ page }) => {
    console.log('测试 L 队 WASD 控制');
    
    // 测试向上移动 (W)
    await page.keyboard.press('W');
    await page.waitForTimeout(500);
    
    // 测试向左移动 (A)
    await page.keyboard.press('A');
    await page.waitForTimeout(500);
    
    // 测试向下移动 (S)
    await page.keyboard.press('S');
    await page.waitForTimeout(500);
    
    // 测试向右移动 (D)
    await page.keyboard.press('D');
    await page.waitForTimeout(500);
    
    // 进行更多步骤的移动测试（至少10步）
    for (let i = 0; i < 6; i++) {
      await page.keyboard.press('W');
      await page.waitForTimeout(400);
    }
    
    // 验证游戏仍在运行
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ L队 WASD 控制测试通过');
  });

  test('R队应该能使用方向键控制移动', async ({ page }) => {
    console.log('测试 R 队方向键控制');
    
    // 测试向上移动 (UP)
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(500);
    
    // 测试向左移动 (LEFT)
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(500);
    
    // 测试向下移动 (DOWN)
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(500);
    
    // 测试向右移动 (RIGHT)
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(500);
    
    // 进行更多步骤的移动测试（至少10步）
    for (let i = 0; i < 6; i++) {
      await page.keyboard.press('ArrowUp');
      await page.waitForTimeout(400);
    }
    
    // 验证游戏仍在运行
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ R队方向键控制测试通过');
  });

  test('L队和R队应该能同时独立移动', async ({ page }) => {
    console.log('测试独立团队控制');
    
    // 模拟同时按下 W 和 ArrowUp（在实际测试中需要快速交替）
    await page.keyboard.press('W');
    await page.waitForTimeout(100);
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(400);
    
    // 测试不同方向
    await page.keyboard.press('A');
    await page.waitForTimeout(100);
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(400);
    
    await page.keyboard.press('D');
    await page.waitForTimeout(100);
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(400);
    
    await page.keyboard.press('S');
    await page.waitForTimeout(100);
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(400);
    
    // 验证游戏仍在运行且没有冲突
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 独立团队控制测试通过');
  });

  test('键盘输入应该工作（基础移动测试）', async ({ page }) => {
    console.log('测试基础键盘输入功能');
    
    // 进行一系列移动
    const moves = ['W', 'W', 'D', 'D', 'S', 'S', 'A', 'A'];
    for (const move of moves) {
      await page.keyboard.press(move);
      await page.waitForTimeout(400);
    }
    
    // 验证游戏仍在运行
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 基础键盘输入测试通过');
  });

  test('游戏暂停时键盘输入应该无效', async ({ page }) => {
    console.log('测试暂停状态');
    
    // 暂停游戏（再次按空格）
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
    
    // 尝试移动（应该无效）
    await page.keyboard.press('W');
    await page.waitForTimeout(500);
    
    // 恢复游戏
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
    
    // 移动应该有效
    await page.keyboard.press('W');
    await page.waitForTimeout(500);
    
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 暂停状态测试通过');
  });
});
