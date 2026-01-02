"""
游戏常量定义
集中管理所有魔法数字和配置常量
"""

# 游戏配置
DEFAULT_PRISON_DURATION = 20000  # 监狱持续时间（毫秒）
DEFAULT_SHOW_GAP_MSEC = 1000.0  # 显示间隔（毫秒）

# 寻路配置
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # 上、下、左、右
DIRECTION_NAMES = {
    (0, -1): "up",
    (0, 1): "down",
    (-1, 0): "left",
    (1, 0): "right"
}

# 强化学习配置
DEFAULT_STATE_DIM = 19  # 5(玩家) + 6(目标) + 4(对手) + 4(全局) = 19
DEFAULT_ACTION_DIM = 3  # defence, scoring, saving
DEFAULT_BATCH_SIZE = 64
DEFAULT_REPLAY_BUFFER_SIZE = 10000
DEFAULT_LEARNING_RATE = 0.0005
DEFAULT_GAMMA = 0.99
DEFAULT_EPSILON_START = 1.0
DEFAULT_EPSILON_END = 0.01
DEFAULT_EPSILON_DECAY = 0.998
DEFAULT_TARGET_UPDATE_FREQ = 50

# 奖励配置
REWARD_STEP_PENALTY = -0.05  # 步惩罚
REWARD_PICK_FLAG = 15.0      # 拾旗奖励
REWARD_LOSE_FLAG = -40.0     # 失去旗帜惩罚
REWARD_GET_CAUGHT = -30.0    # 被抓惩罚
REWARD_SCORE_FLAG = 100.0    # 得分奖励（主要目标）
REWARD_DEFENCE = 15.0        # 防御奖励
REWARD_DEFENCE_CLOSE = 5.0   # 防御接近奖励
REWARD_SAVING_SINGLE = 20.0  # 救援奖励（单玩家）
REWARD_SAVING_MULTIPLE = 10.0 # 救援奖励（多玩家）

