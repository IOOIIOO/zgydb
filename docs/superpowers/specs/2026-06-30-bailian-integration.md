# 阿里云百炼 qwen3.7-plus 全面接入 设计文档

> 状态: approved | 日期: 2026-06-30

## 目标

将 qwen3.7-plus 接入项目，替换全部剩余假数据函数。已在本地部署的 Qwen2.5-7B (M2-3/M4) 和 bge-large-zh-v1.5 (M5) 保持不变。

## 架构

```
config.py (env: MODEL_MODE=real, DASHSCOPE_API_KEY, BAILIAN_WORKSPACE_ID)
        ↓
model_interface.py (统一开关)
        ↓
bailian_client.py          ← 共享 HTTP 客户端
  • chat()                  ← 通用对话
  • chat_json()             ← 对话 + 强制 JSON 输出
  • chat_with_search()      ← 联网搜索 (enable_search=true)
        ↓
bailian_llm.py              ← 7 个业务函数
  • extract_from_text()     ← M2-1
  • score_abilities()       ← M2-2
  • write_recommendation()  ← M2-4
  • analyze_position_match()← M2-4ext
  • polish_report()         ← M2-5
  • chat_response()         ← M2-6
  • search_trends()         ← M3
  • search_resources()      ← M3
```

## 切换方式

`.env` 改一行：`MODEL_MODE=real`

全部 11 个模型任务切换到真实模型，业务代码零改动。

## 文件变更

| 文件 | 操作 | 预计行数 |
|------|:--:|:--:|
| `real_models/bailian_client.py` | 新建 | ~80 |
| `real_models/bailian_llm.py` | 新建 | ~350 |
| `model_interface.py` | 重写 | 开关区 |
| `.env.example` | 更新 | +3 行 |

## 函数签名（与现假数据完全兼容）

| 函数 | 输入 | 输出 |
|------|------|------|
| extract_from_text | text: str | dict |
| score_abilities | skills: list | dict |
| write_recommendation | user_profile: dict, position: dict | str |
| analyze_position_match | user_portrait: dict, position: dict | dict |
| polish_report | draft: str | str |
| chat_response | stage: str, user_message: str | dict |
| search_trends | direction_id: int | dict |
| search_resources | ability_scores: dict | dict |

## 假数据标注铁律

- 所有 BAILIAN_ 前缀函数保留 TODO 注释（标记模型类型 + 调用位置）
- 通过 model_interface.py 中间层暴露，后续可无缝替换为其他模型
