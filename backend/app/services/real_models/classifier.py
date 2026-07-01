"""
真实分类模型 — 通过 LM Studio 本地部署的 Qwen2.5-7B-Instruct-1M

替代文件: app/services/fake_data/classifier.py
模型来源: LM Studio @ http://localhost:1234/v1
"""

import json
import re
import requests

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct-1m"

CERT_SYSTEM_PROMPT = """你是证书/资质分级分类器。根据证书名称判断其级别和含金量。

级别定义:
- 1: 国际顶级认证 (如CFA、CPA、PMP、ACCA、AWS Solutions Architect)
- 2: 国家级认证 (如大学英语四六级、全国计算机等级、软考、法律职业资格)
- 3: 省级/行业认证
- 4: 校级/地方认证
- 5: 其他/低含金量

分数 (1-10): 含金量评分，1=最低，10=最高

严格只返回 JSON，不要任何解释:
{"level": 数字, "level_name": "国际/顶级"|"国家级"|"省级"|"校级"|"其他", "score": 数字}"""

COMPETITION_SYSTEM_PROMPT = """你是竞赛分级分类器。根据竞赛名称判断其级别和加分值。

级别定义:
- 1: 国际级 (如ACM-ICPC、美赛数学建模、Kaggle Grandmaster)
- 2: 国家级 (如全国大学生数学建模、挑战杯、互联网+)
- 3: 省级 (如蓝桥杯省赛、省部级竞赛)
- 4: 校级
- 5: 院级/其他

加分值 (1-10): 含金量评分，1=最低，10=最高

严格只返回 JSON，不要任何解释:
{"level": 数字, "level_name": "国际级"|"国家级"|"省级"|"校级"|"院级/其他", "bonus_score": 数字}"""


def _call_classifier(system_prompt: str, user_input: str) -> dict:
    """调用 LM Studio 本地模型进行文本分类"""
    resp = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"待分类: {user_input}"},
            ],
            "temperature": 0.0,
            "max_tokens": 150,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LM Studio 分类模型调用失败: HTTP {resp.status_code}")

    text = resp.json()["choices"][0]["message"]["content"].strip()
    # 提取 JSON 块（可能被 markdown 代码块包裹）
    json_match = re.search(r'\{[^{}]*\}', text)
    if not json_match:
        raise RuntimeError("LM Studio 分类模型返回内容无法解析为JSON")
    return json.loads(json_match.group(0))


def classify_certificate(name: str) -> dict:
    """真实模型: 证书分级"""
    result = _call_classifier(
        CERT_SYSTEM_PROMPT,
        f"证书名称：{name}"
    )
    if "level" not in result or "score" not in result:
        raise RuntimeError(f"LM Studio 证书分类结果缺少字段: {result}")

    # 标准化 level_name
    valid_names = {"国际/顶级", "国家级", "省级", "校级", "其他"}
    if result.get("level_name") not in valid_names:
        level = result["level"]
        if level == 1:
            result["level_name"] = "国际/顶级"
        elif level == 2:
            result["level_name"] = "国家级"
        elif level == 3:
            result["level_name"] = "省级"
        elif level == 4:
            result["level_name"] = "校级"
        else:
            result["level_name"] = "其他"
    return {
        "level": result["level"],
        "level_name": result["level_name"],
        "score": result["score"],
    }


def classify_competition(name: str) -> dict:
    """真实模型: 竞赛分级"""
    result = _call_classifier(
        COMPETITION_SYSTEM_PROMPT,
        f"竞赛名称：{name}"
    )
    if "level" not in result or "bonus_score" not in result:
        raise RuntimeError(f"LM Studio 竞赛分类结果缺少字段: {result}")

    valid_names = {"国际级", "国家级", "省级", "校级", "院级/其他"}
    if result.get("level_name") not in valid_names:
        level = result["level"]
        if level == 1:
            result["level_name"] = "国际级"
        elif level == 2:
            result["level_name"] = "国家级"
        elif level == 3:
            result["level_name"] = "省级"
        elif level == 4:
            result["level_name"] = "校级"
        else:
            result["level_name"] = "院级/其他"
    return {
        "level": result["level"],
        "level_name": result["level_name"],
        "bonus_score": result["bonus_score"],
    }
