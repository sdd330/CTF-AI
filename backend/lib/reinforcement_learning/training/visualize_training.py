"""
训练可视化脚本 - 实时显示训练进度和统计信息
"""

import os
import json
import time
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import deque

# 设置中文字体
chinese_fonts = ['PingFang SC', 'STHeiti', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
available_fonts = [f.name for f in fm.fontManager.ttflist]
selected_font = next((f for f in chinese_fonts if f in available_fonts), None)
plt.rcParams['font.sans-serif'] = [selected_font or 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class TrainingVisualizer:
    """训练可视化器"""

    def __init__(self, stats_file=None, update_interval=5):
        self.stats_file = stats_file or "/tmp/ctf-ai/training_stats.json"
        self.update_interval = update_interval
        self.stats_history = {'episodes': [], 'rewards': deque(maxlen=100),
                              'losses': deque(maxlen=100), 'epsilon': deque(maxlen=100)}
        self.last_episode = 0

    def load_stats(self):
        """加载训练统计"""
        if not os.path.exists(self.stats_file):
            return None
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None

    def update_history(self, stats):
        """更新历史数据"""
        if stats is None:
            return
        episodes = stats.get('episode', 0)
        if episodes > self.last_episode:
            new_episodes = episodes - self.last_episode
            self.last_episode = episodes
            for key, src_key in [('rewards', 'episode_rewards'), ('losses', 'losses'), ('epsilon', 'epsilon_history')]:
                src = stats.get(src_key, [])
                if len(src) > len(self.stats_history[key]):
                    self.stats_history[key].extend(src[-new_episodes:])

    def _plot_curve(self, ax, data, color, title, xlabel, ylabel):
        """绘制带移动平均的曲线"""
        if not data:
            return
        values = list(data)
        window = min(20, len(values))
        moving_avg = [np.mean(values[max(0, i - window + 1):i + 1]) for i in range(len(values))]
        ax.plot(range(len(values)), values, alpha=0.3, color=color, label='原始值')
        ax.plot(range(len(moving_avg)), moving_avg, color='red', linewidth=2, label=f'{window}期移动平均')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def plot_stats(self, stats):
        """绘制统计图表"""
        if stats is None:
            print("等待训练数据...")
            return None
        self.update_history(stats)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('DQN训练进度监控', fontsize=16, fontweight='bold')

        self._plot_curve(axes[0, 0], self.stats_history['rewards'], 'blue', 'Episode奖励趋势', 'Episode', '奖励')
        self._plot_curve(axes[0, 1], self.stats_history['losses'], 'orange', '训练损失趋势', '训练步数', '损失')
        self._plot_curve(axes[1, 0], self.stats_history['epsilon'], 'green', '探索率趋势', 'Episode', 'Epsilon')

        ax4 = axes[1, 1]
        ax4.axis('off')
        recent_rewards = list(self.stats_history['rewards'])[-10:]
        recent_losses = list(self.stats_history['losses'])[-10:]
        info_text = f"""
训练统计信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总Episode数: {stats.get('episode', 0)}
平均奖励 (全部): {stats.get('avg_reward', 0):.2f}
平均奖励 (最近10局): {np.mean(recent_rewards) if recent_rewards else 0:.2f}
最佳奖励: {stats.get('best_reward', 0):.2f}
平均损失: {np.mean(recent_losses) if recent_losses else 0:.4f}
当前探索率: {stats.get('epsilon_history', [0])[-1]:.4f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
训练建议:
{self.get_training_advice(stats)}
        """
        ax4.text(0.1, 0.5, info_text, fontsize=11, verticalalignment='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt.tight_layout()
        return fig

    def get_training_advice(self, stats):
        """获取训练建议"""
        if stats is None or stats.get('episode', 0) == 0:
            return "训练刚开始，继续观察..."

        advice = []
        avg_reward = stats.get('avg_reward', 0)
        avg_reward_recent = stats.get('avg_reward_recent', 0)
        episodes = stats.get('episode', 0)
        recent_rewards = stats.get('episode_rewards', [])[-20:]

        if avg_reward_recent > avg_reward * 1.1:
            advice.append("✓ 奖励呈上升趋势")
        elif avg_reward_recent < avg_reward * 0.9:
            advice.append("⚠ 奖励呈下降趋势")
        else:
            advice.append("○ 奖励趋势稳定")

        if len(recent_rewards) >= 10:
            if np.std(recent_rewards) < 10 and episodes > 50:
                advice.append("✓ 奖励趋于稳定，可能已收敛")
            elif np.std(recent_rewards) > 50:
                advice.append("⚠ 奖励波动较大")

        if episodes < 50:
            advice.append("○ 建议至少训练100个episode")
        elif episodes >= 200:
            advice.append("✓ 训练已进行较长时间")

        return "\n".join(advice)

    def run(self, save_plot=True):
        """运行可视化"""
        print(f"{'='*60}\n训练可视化监控\n{'='*60}")
        print(f"监控文件: {self.stats_file}\n更新间隔: {self.update_interval}秒\n按 Ctrl+C 停止")
        try:
            while True:
                stats = self.load_stats()
                if stats:
                    fig = self.plot_stats(stats)
                    if fig and save_plot:
                        fig.savefig("lib/models/training_plot.png", dpi=150, bbox_inches='tight')
                    plt.show(block=False)
                    plt.pause(0.1)
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            print("\n监控已停止")
            plt.close('all')


def main():
    import sys
    stats_file = sys.argv[1] if len(sys.argv) > 1 else None
    update_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    TrainingVisualizer(stats_file, update_interval).run()


if __name__ == "__main__":
    main()
