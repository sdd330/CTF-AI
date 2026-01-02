# 单元测试说明

## Player类测试

`test_player.py` 包含了对 `Player` 类的全面单元测试，确保所有功能正常工作。

### 运行测试

```bash
cd backend
python3 -m unittest tests.test_player -v
```

### 测试覆盖

测试覆盖了以下方面：

1. **对象创建**
   - ✅ 正常创建（L队和R队）
   - ✅ 参数验证（空名称、错误类型、无效team）
   - ✅ `belongs_to` 属性正确设置

2. **归属属性（belongs_to）**
   - ✅ `belongs_to` 属性始终存在
   - ✅ `belongs_to` 与 `team` 保持一致
   - ✅ 所有方法都正确使用 `belongs_to`
   - ✅ 在各种状态下（自由、携带旗帜、在监狱）`belongs_to` 都正确

3. **队伍关系方法**
   - ✅ `belongs_to_team()` - 检查是否属于指定队伍
   - ✅ `is_enemy_of()` - 检查是否是敌人
   - ✅ `is_teammate_of()` - 检查是否是队友
   - ✅ `is_enemy_team()` - 检查是否是敌方队伍
   - ✅ `is_my_team()` - 检查是否是己方队伍

4. **状态管理**
   - ✅ 初始状态（FREE）
   - ✅ 拾取旗帜（CARRYING_FLAG）
   - ✅ 放下旗帜
   - ✅ 送入监狱（IN_PRISON）
   - ✅ 救援

5. **其他功能**
   - ✅ 移动功能
   - ✅ `to_dict()` 方法
   - ✅ `__repr__()` 方法
   - ✅ 多个Player对象的正确性

### 关键测试

最重要的测试是确保 `belongs_to` 属性：
- ✅ 在创建时总是被设置
- ✅ 始终存在（不会缺失）
- ✅ 与 `team` 保持一致
- ✅ 在所有方法中正确使用

### 运行所有测试

```bash
cd backend
python3 -m unittest discover tests -v
```

