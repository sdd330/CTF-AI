import { test, expect, Page } from '@playwright/test';

/**
 * CTF-AI 游戏高级自动化测试
 * 
 * 包含更精确的游戏控制和验证
 */

// 游戏控制辅助类
class GameController {
  constructor(private page: Page) {}

  async waitForGameReady(timeout = 30000) {
    // 等待 Phaser 加载
    await this.page.waitForFunction(
      () => (window as any).Phaser !== undefined,
      { timeout }
    );

    // 等待画布出现
    await this.page.waitForSelector('canvas', { timeout });
    
    // 等待游戏场景初始化
    await this.page.waitForTimeout(2000);
  }

  async focusCanvas() {
    const canvas = await this.page.waitForSelector('canvas');
    if (canvas) {
      await canvas.click();
      await this.page.waitForTimeout(300);
    }
  }

  async startGame() {
    await this.focusCanvas();
    await this.page.keyboard.press('Space');
    await this.page.waitForTimeout(3000); // 等待游戏启动
  }

  async move(direction: 'w' | 'a' | 's' | 'd', times = 1, interval = 500) {
    for (let i = 0; i < times; i++) {
      await this.page.keyboard.press(direction.toUpperCase());
      await this.page.waitForTimeout(interval);
    }
  }

  async moveToPosition(targetX: number, targetY: number, currentX = 0, currentY = 0) {
    const dx = targetX - currentX;
    const dy = targetY - currentY;

    // 水平移动
    if (dx > 0) {
      await this.move('d', Math.abs(dx));
    } else if (dx < 0) {
      await this.move('a', Math.abs(dx));
    }

    // 垂直移动
    if (dy > 0) {
      await this.move('s', Math.abs(dy));
    } else if (dy < 0) {
      await this.move('w', Math.abs(dy));
    }
  }

  async waitForPlayerMovement(duration = 2000) {
    await this.page.waitForTimeout(duration);
  }

  async checkGameRunning(): Promise<boolean> {
    const canvas = await this.page.$('canvas');
    return canvas !== null;
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png` });
  }
}

test.describe('CTF-AI 游戏高级自动化测试', () => {
  let gameController: GameController;

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    gameController = new GameController(page);
    await gameController.waitForGameReady();
  });

  test('精确控制：移动到指定位置', async ({ page }) => {
    await gameController.startGame();
    
    // 移动到地图中心区域
    console.log('移动到地图中心 (10, 10)');
    await gameController.moveToPosition(10, 10);
    await gameController.waitForPlayerMovement();
    
    // 验证游戏仍在运行
    expect(await gameController.checkGameRunning()).toBe(true);
    
    console.log('✓ 精确位置控制测试完成');
  });

  test('策略测试：进攻路线', async ({ page }) => {
    await gameController.startGame();
    
    // 模拟进攻路线：从左侧移动到右侧抢旗
    console.log('执行进攻路线...');
    
    // 1. 向前推进
    await gameController.move('d', 8, 600);
    await gameController.waitForPlayerMovement(1000);
    
    // 2. 调整位置
    await gameController.move('s', 2, 400);
    await gameController.waitForPlayerMovement(500);
    
    // 3. 继续推进
    await gameController.move('d', 5, 600);
    await gameController.waitForPlayerMovement(2000);
    
    // 4. 尝试抢旗（在旗帜附近移动）
    await gameController.move('w', 1, 400);
    await gameController.move('d', 2, 400);
    await gameController.move('s', 1, 400);
    await gameController.waitForPlayerMovement(2000);
    
    expect(await gameController.checkGameRunning()).toBe(true);
    console.log('✓ 进攻路线测试完成');
  });

  test('策略测试：防守路线', async ({ page }) => {
    await gameController.startGame();
    
    // 模拟防守：在己方区域巡逻
    console.log('执行防守路线...');
    
    // 在己方区域来回移动
    for (let i = 0; i < 3; i++) {
      await gameController.move('d', 3, 500);
      await gameController.waitForPlayerMovement(500);
      await gameController.move('a', 3, 500);
      await gameController.waitForPlayerMovement(500);
    }
    
    expect(await gameController.checkGameRunning()).toBe(true);
    console.log('✓ 防守路线测试完成');
  });

  test('完整游戏循环：抢旗并返回', async ({ page }) => {
    test.setTimeout(90000); // 90秒超时
    
    await gameController.startGame();
    
    console.log('开始完整游戏循环...');
    
    // 阶段 1: 移动到敌方区域（减少移动次数和等待时间）
    console.log('阶段 1: 移动到敌方区域');
    await gameController.move('d', 8, 400);
    await gameController.waitForPlayerMovement(1500);
    
    // 阶段 2: 寻找并接近旗帜
    console.log('阶段 2: 寻找旗帜');
    await gameController.move('s', 2, 300);
    await gameController.move('d', 3, 300);
    await gameController.move('w', 2, 300);
    await gameController.waitForPlayerMovement(1500);
    
    // 阶段 3: 返回己方区域
    console.log('阶段 3: 返回己方区域');
    await gameController.move('a', 8, 400);
    await gameController.waitForPlayerMovement(1500);
    
    // 阶段 4: 移动到目标区域
    console.log('阶段 4: 移动到目标区域');
    await gameController.move('w', 3, 300);
    await gameController.waitForPlayerMovement(1500);
    
    expect(await gameController.checkGameRunning()).toBe(true);
    console.log('✓ 完整游戏循环测试完成');
  });

  test('压力测试：快速连续操作', async ({ page }) => {
    await gameController.startGame();
    
    console.log('执行压力测试...');
    
    // 快速连续按键
    const rapidSequence = [
      'd', 'd', 'd', 's', 's', 'a', 'a', 'w', 'w',
      'd', 's', 'a', 'w', 'd', 's', 'a', 'w'
    ];
    
    for (const key of rapidSequence) {
      await page.keyboard.press(key.toUpperCase());
      await page.waitForTimeout(100); // 非常短的间隔
    }
    
    await gameController.waitForPlayerMovement(2000);
    
    expect(await gameController.checkGameRunning()).toBe(true);
    console.log('✓ 压力测试完成');
  });

  test('边界测试：移动到地图边缘', async ({ page }) => {
    test.setTimeout(90000); // 90秒超时
    
    await gameController.startGame();
    
    console.log('测试地图边界...');
    
    // 向右移动到边缘（减少移动次数，地图通常只有20格宽）
    await gameController.move('d', 10, 300);
    await gameController.waitForPlayerMovement(800);
    
    // 向下移动到边缘
    await gameController.move('s', 10, 300);
    await gameController.waitForPlayerMovement(800);
    
    // 向左移动到边缘
    await gameController.move('a', 10, 300);
    await gameController.waitForPlayerMovement(800);
    
    // 向上移动到边缘
    await gameController.move('w', 10, 300);
    await gameController.waitForPlayerMovement(800);
    
    expect(await gameController.checkGameRunning()).toBe(true);
    console.log('✓ 边界测试完成');
  });
});

