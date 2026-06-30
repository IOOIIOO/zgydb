# M2-3 软标签推断接入本地模型 实现计划

> **For agentic workers:** Use superpowers:executing-plans to implement.

**Goal:** 将 soft_labels 从假数据切换为本地 Qwen2.5-7B 真实推理

**Architecture:** `real_models/soft_labels.py`(已创建) → `model_interface.py`(接线) → `ability_service.py`(自动生效)

## 文件变更

| 文件 | 操作 |
|------|------|
| `real_models/soft_labels.py` | ✅ 已创建 |
| `model_interface.py` | 修改 — 加开关+导入+导出 |

---

### Task 1: model_interface.py 接线

**修改:** `backend/app/services/model_interface.py`

- [ ] **Step 1: 加开关**

在已有开关区域追加：
```python
USE_REAL_SOFT_LABELS = True   # True=本地Qwen2.5-7B推断, False=假数据固定值
```

- [ ] **Step 2: 加导入**

在真实模型导入区追加：
```python
if USE_REAL_SOFT_LABELS:
    from app.services.real_models.soft_labels import (
        infer_soft_labels as real_infer_soft_labels,
    )
else:
    real_infer_soft_labels = None
```

- [ ] **Step 3: 改导出**

```python
# 改前: infer_soft_labels = FAKE_infer_soft_labels
# 改后:
infer_soft_labels = real_infer_soft_labels if USE_REAL_SOFT_LABELS else FAKE_infer_soft_labels
```

- [ ] **Step 4: 验证**

```bash
cd /d/zgyd/backend && python -c "
from app.services.model_interface import infer_soft_labels
r = infer_soft_labels([
  {'name': '电商平台', 'role': '组长', 'tech_stack': ['Python', 'Vue', 'MySQL'],
   'description': '带领3人团队从零搭建全栈电商系统，设计了微服务架构'},
  {'name': '数据分析课设', 'role': '成员', 'tech_stack': ['Python', 'Pandas'],
   'description': '自学Pandas完成数据清洗和可视化'}
])
print(r)
"
```

Expected: 本地模型返回真实的 logic/communication/learning 标签及依据，而非固定值 "良好/良好/较强"

---

### Task 2: 更新文档

- [ ] **Step 1: 更新 findings.md** — M2-3 行标记为"真实 Qwen2.5-7B"
- [ ] **Step 2: 更新 progress.md** — 记录 M2-3 接入完成
