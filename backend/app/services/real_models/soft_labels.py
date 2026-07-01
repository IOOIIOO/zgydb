"""
真实软标签推断 — Qwen2.5-7B-Instruct-1M (LM Studio)

替代文件: app/services/fake_data/general_llm.py 中的 FAKE_infer_soft_labels
模型来源: LM Studio @ http://localhost:1234/v1
"""

import json
import re
import requests

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct-1m"

SYSTEM_PROMPT = """你是学生能力评估专家。根据学生的项目经历，推断其三项软能力等级。

输入：学生的项目经历列表（项目名称、角色、技术栈、描述）

输出规则：
1. 逻辑思维 (logic) — 评估维度：项目技术复杂度、是否有架构设计、问题拆解、算法优化
   可选值: 优秀 / 良好 / 中等 / 一般 / 较弱

2. 沟通协作 (communication) — 评估维度：是否担任组长/负责人、团队规模、跨角色协调
   可选值: 优秀 / 良好 / 中等 / 一般 / 较弱

3. 学习能力 (learning) — 评估维度：技术栈多样性、是否自学新技术、跨领域能力
   可选值: 强 / 较强 / 良好 / 中等 / 一般

严格只返回 JSON，不要任何解释：
{"logic_label": "良好", "communication_label": "中等", "learning_label": "较强",
 "logic_reason": "一句话依据", "communication_reason": "一句话依据", "learning_reason": "一句话依据"}"""


def infer_soft_labels(projects: list[dict]) -> dict:
    """真实模型: 根据项目经历推断软能力标签"""
    # 构建项目描述文本
    project_texts = []
    for i, proj in enumerate(projects):
        parts = []
        if isinstance(proj, dict):
            if proj.get("name"):
                parts.append(f"项目: {proj['name']}")
            if proj.get("role"):
                parts.append(f"角色: {proj['role']}")
            if proj.get("tech_stack"):
                tech = proj["tech_stack"]
                if isinstance(tech, list):
                    parts.append(f"技术栈: {', '.join(tech)}")
                else:
                    parts.append(f"技术栈: {tech}")
            if proj.get("description"):
                parts.append(f"描述: {proj['description']}")
        else:
            parts.append(str(proj))
        if parts:
            project_texts.append(f"项目{i+1}: {' | '.join(parts)}")

    user_input = "\n".join(project_texts) if project_texts else "无项目经历记录"

    resp = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.1,
            "max_tokens": 300,
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LM Studio 软标签推断失败: HTTP {resp.status_code}")

    text = resp.json()["choices"][0]["message"]["content"].strip()
    json_match = re.search(r"\{[^{}]*\}", text)
    if not json_match:
        raise RuntimeError("LM Studio 软标签推断返回内容无法解析为JSON")

    result = json.loads(json_match.group(0))
    # 验证并规范化
    return {
        "logic_label": _normalize_label(result.get("logic_label", "良好"), ["优秀", "良好", "中等", "一般", "较弱"]),
        "communication_label": _normalize_label(result.get("communication_label", "良好"), ["优秀", "良好", "中等", "一般", "较弱"]),
        "learning_label": _normalize_label(result.get("learning_label", "较强"), ["强", "较强", "良好", "中等", "一般"]),
        "label_inference_basis": {
            "logic": result.get("logic_reason", ""),
            "communication": result.get("communication_reason", ""),
            "cert_competition": "已通过 M4 分类模型单独评估",
            "learning": result.get("learning_reason", ""),
        },
    }


def _normalize_label(value: str, valid: list[str]) -> str:
    """确保返回值在合法范围内"""
    if value in valid:
        return value
    return valid[len(valid) // 2]  # 默认取中间值
