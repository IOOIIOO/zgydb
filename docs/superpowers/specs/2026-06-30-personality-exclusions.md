# 岗位性格排除数据填充 设计文档

> 状态: approved | 日期: 2026-06-30

## 目标

为 seed.py 中 30 个职业方向填入 excluded_personality_types，删除从未使用的 excluded_trait_thresholds。

## 数据来源

MBTI-职业匹配研究（2024-2025），仅排除有明确证据的不适配类型。

## 变更范围

| 文件 | 操作 |
|------|------|
| `backend/app/seed.py` | 修改 DIRECTION_DEFINITIONS，30个方向填排除类型 |
| `backend/app/static/personality_constraints.json` | 删除或同步更新 |

## 排除规则（25/30方向开放，5个方向有限制）

| 方向 | excluded_personality_types |
|------|------|
| 软件测试 | ["ENFP","ENTP"] |
| 销售 | ["INTP","INFJ","INFP"] |
| 电话销售 | ["INTP","INFJ","INFP","INTJ"] |
| 客户服务 | ["INTJ","ISTP"] |
| 商务拓展 | ["INFP","ISFJ"] |
| 行政管理 | ["ENTP","ESTP"] |
| 人力资源 | ["ISTP","INTP"] |
| 法律 | ["INFP","ISFP"] |
| 质量管理 | ["ENFP","ENTP"] |
| 咨询 | ["ISFJ","ISFP"] |
| 其余20方向 | [] |

## 同步清理

- 删除 seed.py 中所有 `"excluded_trait_thresholds": {}`
- position 表中对应字段保留（不删列），种子数据填充 `{}`
