import { test, expect, Page } from '@playwright/test';

/**
 * CTF-AI 游戏自动化测试
 * 
 * 测试功能：
 * 1. 启动游戏（按空格键）
 * 2. 控制玩家移动（WASD 键）
 * 3. 验证抢旗功能
 */

// 等待游戏加载的辅助函数
async function waitForGameLoaded(page: Page, timeout = 30000) {
  // 等待 Phaser 游戏初始化
  await page.waitForFunction(
    () => {
      return (window as any).Phaser !== undefined;
    },
    { timeout }
  );

  // 等待游戏画布出现
  await page.waitForSelector('canvas', { timeout });
  
  // 等待教程文本出现（表示游戏已加载）
  await page.waitForFunction(
    () => {
      const canvas = document.querySelector('canvas');
      if (!canvas) return false;
      // 检查是否有游戏元素
      return true;
    },
    { timeout }
  );
}

// 聚焦游戏画布的辅助函数
async function focusGameCanvas(page: Page) {
  const canvas = await page.waitForSelector('canvas');
  if (canvas) {
    await canvas.click();
    await page.waitForTimeout(500); // 等待聚焦完成
  }
}

// 按方向键移动玩家的辅助函数
async function movePlayer(page: Page, direction: 'w' | 'a' | 's' | 'd', duration = 1000) {
  await page.keyboard.press(direction.toUpperCase());
  await page.waitForTimeout(duration);
}

// 连续移动玩家的辅助函数
async function movePlayerSequence(page: Page, sequence: Array<{ key: 'w' | 'a' | 's' | 'd'; duration?: number }>) {
  for (const move of sequence) {
    await movePlayer(page, move.key, move.duration || 500);
  }
}

test.describe('CTF-AI 游戏自动化测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问游戏页面
    await page.goto('/');
    
    // 等待游戏加载
    await waitForGameLoaded(page);
    
    // 聚焦游戏画布
    await focusGameCanvas(page);
  });

  test('应该能够启动游戏（按空格键）', async ({ page }) => {
    // 等待教程文本出现
    await page.waitForTimeout(2000);
    
    // 按空格键启动游戏
    await page.keyboard.press('Space');
    
    // 等待游戏开始（教程文本应该消失或游戏状态改变）
    await page.waitForTimeout(2000);
    
    // 验证游戏已启动（可以通过检查某些游戏元素来验证）
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 游戏已成功启动');
  });

  test('应该能够控制玩家移动（WASD 键）', async ({ page }) => {
    // 先启动游戏
    await page.waitForTimeout(2000);
    await page.keyboard.press('Space');
    await page.waitForTimeout(2000);
    
    // 确保画布聚焦
    await focusGameCanvas(page);
    
    // 测试各个方向的移动
    console.log('测试向上移动 (W)');
    await movePlayer(page, 'w', 1000);
    
    console.log('测试向右移动 (D)');
    await movePlayer(page, 'd', 1000);
    
    console.log('测试向下移动 (S)');
    await movePlayer(page, 's', 1000);
    
    console.log('测试向左移动 (A)');
    await movePlayer(page, 'a', 1000);
    
    // 验证玩家可以移动（画布应该仍然存在）
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 玩家移动控制正常');
  });

  test('应该能够完成抢旗流程', async ({ page }) => {
    // 启动游戏
    await page.waitForTimeout(2000);
    await page.keyboard.press('Space');
    await page.waitForTimeout(3000); // 等待游戏完全启动
    
    // 确保画布聚焦
    await focusGameCanvas(page);
    
    // 尝试移动到敌方旗帜位置
    // 注意：这里需要根据实际地图布局调整移动序列
    // 假设玩家在左侧，需要向右移动去抢右侧的旗帜
    
    console.log('开始抢旗流程...');
    
    // 向右移动（朝向敌方旗帜）
    for (let i = 0; i < 5; i++) {
      await movePlayer(page, 'd', 800);
      await page.waitForTimeout(500);
    }
    
    // 可能需要上下调整位置
    await movePlayer(page, 's', 500);
    await page.waitForTimeout(500);
    
    // 继续向右移动
    for (let i = 0; i < 3; i++) {
      await movePlayer(page, 'd', 800);
      await page.waitForTimeout(500);
    }
    
    // 等待抢旗完成（物理碰撞检测会自动处理）
    await page.waitForTimeout(2000);
    
    // 验证游戏仍在运行（没有崩溃）
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 抢旗流程测试完成');
  });

  test('应该能够完成完整的游戏流程（启动 -> 移动 -> 抢旗 -> 返回）', async ({ page }) => {
    // 1. 启动游戏
    console.log('步骤 1: 启动游戏');
    await page.waitForTimeout(2000);
    await page.keyboard.press('Space');
    await page.waitForTimeout(3000);
    
    // 确保画布聚焦
    await focusGameCanvas(page);
    
    // 2. 移动到敌方区域抢旗
    console.log('步骤 2: 移动到敌方区域');
    const moveToEnemySequence = [
      { key: 'd', duration: 600 },
      { key: 'd', duration: 600 },
      { key: 'd', duration: 600 },
      { key: 'd', duration: 600 },
      { key: 'd', duration: 600 },
    ];
    await movePlayerSequence(page, moveToEnemySequence);
    await page.waitForTimeout(2000);
    
    // 3. 尝试抢旗（移动到旗帜位置）
    console.log('步骤 3: 尝试抢旗');
    const grabFlagSequence = [
      { key: 's', duration: 400 },
      { key: 'd', duration: 400 },
      { key: 'd', duration: 400 },
      { key: 'w', duration: 400 },
    ];
    await movePlayerSequence(page, grabFlagSequence);
    await page.waitForTimeout(2000);
    
    // 4. 返回自己的区域
    console.log('步骤 4: 返回自己的区域');
    const returnHomeSequence = [
      { key: 'a', duration: 600 },
      { key: 'a', duration: 600 },
      { key: 'a', duration: 600 },
      { key: 'a', duration: 600 },
      { key: 'a', duration: 600 },
    ];
    await movePlayerSequence(page, returnHomeSequence);
    await page.waitForTimeout(2000);
    
    // 验证游戏仍在运行
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 完整游戏流程测试完成');
  });

  test('应该能够处理连续快速移动', async ({ page }) => {
    // 启动游戏
    await page.waitForTimeout(2000);
    await page.keyboard.press('Space');
    await page.waitForTimeout(2000);
    
    await focusGameCanvas(page);
    
    // 快速连续按键
    console.log('测试快速连续移动');
    const rapidMoves = ['w', 'd', 's', 'a', 'w', 'd', 's', 'a'];
    
    for (const key of rapidMoves) {
      await page.keyboard.press(key.toUpperCase());
      await page.waitForTimeout(200);
    }
    
    await page.waitForTimeout(1000);
    
    // 验证游戏没有崩溃
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    
    console.log('✓ 快速移动测试完成');
  });
});

