# 任务计划：本地化所有不需要联网的 LLM 调用

## 目标
将岗位匹配分析、推荐理由、报告润色、发展路径生成从百炼云端迁移到本地 LM Studio，仅保留趋势搜索和资源搜索在百炼（需要联网）。

## 当前阶段
✅ **全部完成** — 2026-07-01

## 完成状态
| 功能 | 状态 | 说明 |
|------|:---:|------|
| `analyze_resume` 统一分析 | ✅ | 替代 extract_from_text + score_abilities + infer_soft_labels + 证书竞赛分级 |
| `chat_response` 对话引导 | ✅ | 本地 LM Studio 驱动 |
| `analyze_position_match` → 本地 | ✅ | 替代百炼，~10s |
| `batch_write_recommendations` → 本地 | ✅ | 函数就绪（当前流程未调用） |
| `polish_report` → 本地 | ✅ | 报告润色 ~8s |
| 发展路径生成 → 本地 | ✅ | 资源搜索保留百炼 |
| 对话收集修复 | ✅ | 上传和对话均汇总全部消息后分析 |
| 前端交互优化 | ✅ | 删除延迟、上传进度、生成按钮、loading反馈、三卡片布局 |

## 决策
- 百炼仅保留 `search_trends` 和 `search_resources`（需要联网搜索）
- 所有文本分析类 LLM 调用统一走本地 LM Studio
- 本地异常时兜底返回合理的默认值，不阻断流程
- 模型选择：Qwen2.5-7B-Instruct-1M（DeepSeek R1 推理链过长不适合）

## 全流程基准
```
注册 0.2s → MBTI 0s → 能力分析 13s → 岗位推荐 2s → 岗位详情 9s
总耗时 24.8s（零云端，全本地）
```
