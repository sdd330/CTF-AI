"""
Capture the Flag 游戏主程序
使用 pygame 实现的 Python 版本
采用场景系统设计
使用 SceneManager 统一管理所有游戏场景
"""

import sys
import os
from pathlib import Path

# 添加 native 目录的父目录到路径，使 native 可以作为包导入
native_dir = Path(__file__).parent
parent_dir = native_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import pygame
from native.scenes import SceneManager, BootScene, PreloaderScene, GameScene, GameOverScene
from native.utils import get_config, get_logger
from native.utils.constants import FPS, TILE_SIZE


def setup_scenes(screen: pygame.Surface, clock: pygame.time.Clock) -> SceneManager:
    """
    设置并注册所有游戏场景
    
    Args:
        screen: pygame Surface对象
        clock: pygame Clock对象
    
    Returns:
        配置好的场景管理器
    """
    # 获取场景管理器实例（单例模式）
    scene_manager = SceneManager()
    scene_manager.set_screen_and_clock(screen, clock)
    
    # 创建所有场景实例
    boot_scene = BootScene(scene_manager)
    preloader_scene = PreloaderScene(scene_manager)
    game_scene = GameScene(scene_manager)
    game_over_scene = GameOverScene(scene_manager)
    
    # 批量注册场景
    scene_manager.register_scenes([
        boot_scene,
        preloader_scene,
        game_scene,
        game_over_scene,
    ])
    
    logger = get_logger()
    logger.info(f"已注册 {len(scene_manager.get_all_scene_keys())} 个场景: {scene_manager.get_all_scene_keys()}")
    
    return scene_manager


def main():
    """主函数"""
    # 获取配置
    config = get_config()
    logger = get_logger()
    
    # 初始化pygame（包括所有模块）
    pygame.init()
    
    # 显式初始化字体模块（解决循环导入问题）
    try:
        pygame.font.init()
    except:
        logger.warning("字体模块初始化失败，将使用系统字体")
    
    # 确保图像模块可用
    try:
        pygame.image.get_extended()
    except:
        logger.warning("pygame 图像扩展不可用，PNG 图片可能无法加载")
    
    # 从配置获取地图大小，窗口大小等于地图大小
    map_width = config.map_width
    map_height = config.map_height
    screen_width = map_width * TILE_SIZE
    screen_height = map_height * TILE_SIZE
    
    logger.info(f"地图大小: {map_width}x{map_height}")
    logger.info(f"窗口大小: {screen_width}x{screen_height}")
    
    # 创建屏幕（不再支持全屏，窗口大小固定为地图大小）
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Capture the Flag - Pygame")
    
    # 创建时钟
    clock = pygame.time.Clock()
    
    # 设置场景管理器并注册所有场景
    scene_manager = setup_scenes(screen, clock)
    
    # 启动 Boot 场景（游戏入口）
    scene_manager.start_scene('Boot')
    
    logger.info("=" * 60)
    logger.info("游戏启动！")
    logger.info("=" * 60)
    logger.info(f"场景流程: Boot -> Preloader -> Game -> GameOver")
    logger.info(f"已注册场景: {scene_manager.get_all_scene_keys()}")
    logger.info(f"当前场景: {scene_manager.get_current_scene_key()}")
    logger.info("")
    logger.info("控制说明：")
    logger.info("  WASD - 控制L0玩家")
    logger.info("  方向键 - 控制R0玩家")
    logger.info("  SPACE - 开始/暂停游戏")
    logger.info("  P - 暂停/继续")
    logger.info("  R - 游戏结束后重新开始")
    logger.info("  L - 游戏结束后重新加载")
    logger.info("  ESC - 退出")
    logger.info("=" * 60)
    
    # 游戏循环
    running = True
    last_time = pygame.time.get_ticks()
    frame_count = 0
    fps_timer = pygame.time.get_ticks()
    current_fps = 0
    
    try:
        while running:
            # 计算时间增量
            current_time = pygame.time.get_ticks()
            delta_time = current_time - last_time
            last_time = current_time
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # 将事件传递给场景管理器，由管理器分发给当前场景
                    scene_manager.handle_event(event)
            
            # 更新场景（由场景管理器统一管理）
            scene_manager.update(delta_time)
            
            # 渲染场景（由场景管理器统一管理）
            scene_manager.render()
            
            # 显示 FPS（如果启用）
            if config.show_fps:
                frame_count += 1
                if current_time - fps_timer >= 1000:  # 每秒更新一次
                    current_fps = frame_count
                    frame_count = 0
                    fps_timer = current_time
                
                # 在屏幕上显示 FPS
                try:
                    font = pygame.font.Font(None, 36)
                    fps_text = font.render(f"FPS: {current_fps}", True, (255, 255, 255))
                    screen.blit(fps_text, (10, 10))
                except (NotImplementedError, AttributeError):
                    # 字体不可用时跳过 FPS 显示
                    pass
            
            pygame.display.flip()
            
            # 控制帧率（从配置获取）
            clock.tick(config.fps)
    
    except KeyboardInterrupt:
        logger.warning("收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        logger.exception("详细错误信息:")
    finally:
        # 清理资源
        logger.info("清理资源...")
        scene_manager.clear_all_scenes()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()

