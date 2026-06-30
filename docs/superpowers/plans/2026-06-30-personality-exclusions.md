# 岗位性格排除数据填充 实现计划

> **For agentic workers:** Use superpowers:executing-plans to implement.

**Goal:** 给 30 个方向填入 excluded_personality_types，删除 excluded_trait_thresholds

**Architecture:** 纯数据修改，改 seed.py 的 DIRECTION_DEFINITIONS 列表即可

---

### Task 1: 更新 seed.py 方向定义

**文件:** `backend/app/seed.py:122-393`

- [ ] **Step 1: 批量替换所有 excluded_personality_types 和 excluded_trait_thresholds**

将 30 个方向中 `excluded_personality_types: []` 替换为设计值，同时删除 `"excluded_trait_thresholds": {}`。

替换映射：
```
前端开发     → []
后端开发     → []
软件测试     → ["ENFP","ENTP"]
硬件测试     → []
IT 技术支持   → []
科研与研发   → []
销售        → ["INTP","INFJ","INFP"]
电话销售    → ["INTP","INFJ","INFP","INTJ"]
网络销售    → []
客户经理    → []
运营        → []
新媒体运营  → []
市场营销    → []
APP推广     → []
游戏运营    → []
游戏推广    → []
产品        → []
行政管理    → ["ENTP","ESTP"]
项目管理    → []
人力资源    → ["ISTP","INTP"]
商务拓展    → ["INFP","ISFJ"]
法律        → ["INFP","ISFP"]
客户服务    → ["INTJ","ISTP"]
质量管理    → ["ENFP","ENTP"]
管理培训生  → []
翻译        → []
教育培训    → []
数据分析    → []
咨询        → ["ISFJ","ISFP"]
后勤综合    → []
```

同时删除每行 `"excluded_trait_thresholds": {},`。

- [ ] **Step 2: 验证 JSON 格式**

```bash
cd /d/zgyd/backend && python -c "
import ast, re
with open('app/seed.py','r',encoding='utf-8') as f:
    content = f.read()
# 确保没有残留 trait_thresholds
assert 'trait_thresholds' not in content, 'FAIL: trait_thresholds still present'
# 统计有排除类型的方向数
count = len(re.findall(r'\"excluded_personality_types\":\s*\[[\"A-Z,\s]*\]', content))
empty = len(re.findall(r'\"excluded_personality_types\":\s*\[\]', content))
filled = len(re.findall(r'\"excluded_personality_types\":\s*\[[\"EIN]', content))
print(f'Total directions: {count}')
print(f'Empty exclusions: {empty}')
print(f'Filled exclusions: {filled}')
assert filled == 10, f'Expected 10 filled, got {filled}'
print('[OK] seed.py updated correctly')
"
```
Expected: 30 total, 20 empty, 10 filled

- [ ] **Step 3: 验证种子脚本可正常运行**

```bash
cd /d/zgyd/backend && python -c "from app.seed import DIRECTION_DEFINITIONS; print(f'{len(DIRECTION_DEFINITIONS)} directions loaded'); [print(f'  {d[\"name\"]}: {d[\"excluded_personality_types\"]}') for d in DIRECTION_DEFINITIONS if d['excluded_personality_types']]; print('[OK]')"
```
