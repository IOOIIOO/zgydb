"""
M4 — 分类模型：证书分级 + 竞赛分级

调用位置：能力评估模块 — 简历/对话提取后的分级环节

TODO: 替换为真实分类模型或规则引擎+知识库
预期模型类型：文本分类模型（可用规则引擎 + 知识库替代）
"""

# 常见证书预定义分级
_CERT_DB = {
    "大学英语六级": {"level": 2, "level_name": "国家级", "score": 6},
    "cet-6": {"level": 2, "level_name": "国家级", "score": 6},
    "大学英语四级": {"level": 2, "level_name": "国家级", "score": 4},
    "cet-4": {"level": 2, "level_name": "国家级", "score": 4},
    "全国计算机等级考试": {"level": 2, "level_name": "国家级", "score": 4},
    "软考": {"level": 2, "level_name": "国家级", "score": 7},
    "注册会计师": {"level": 1, "level_name": "国际/顶级", "score": 10},
    "cpa": {"level": 1, "level_name": "国际/顶级", "score": 10},
    "法律职业资格": {"level": 1, "level_name": "国际/顶级", "score": 10},
    "pmp": {"level": 1, "level_name": "国际/顶级", "score": 9},
    "驾驶证": {"level": 5, "level_name": "其他", "score": 1},
}

# 常见竞赛预定义分级
_COMPETITION_DB = {
    "全国大学生数学建模竞赛": {"level": 2, "level_name": "国家级", "bonus_score": 8},
    "美国大学生数学建模竞赛": {"level": 1, "level_name": "国际级", "bonus_score": 10},
    "acm": {"level": 1, "level_name": "国际级", "bonus_score": 10},
    "蓝桥杯": {"level": 3, "level_name": "省级", "bonus_score": 5},
    "挑战杯": {"level": 2, "level_name": "国家级", "bonus_score": 7},
    "互联网+": {"level": 2, "level_name": "国家级", "bonus_score": 8},
    "校级": {"level": 4, "level_name": "校级", "bonus_score": 2},
    "院级": {"level": 5, "level_name": "院级/其他", "bonus_score": 1},
}


def FAKE_classify_certificate(name: str) -> dict:
    """
    对证书名称进行分级判定。

    Args:
        name: 证书名称

    Returns:
        {level: int, level_name: str, score: int}
    """
    name_lower = name.lower()
    for key, val in _CERT_DB.items():
        if key in name_lower:
            return val
    # 默认：无法识别 → 最低档
    return {"level": 5, "level_name": "其他", "score": 1}


def FAKE_classify_competition(name: str) -> dict:
    """
    对竞赛名称进行分级判定。

    Args:
        name: 竞赛名称

    Returns:
        {level: int, level_name: str, bonus_score: int}
    """
    name_lower = name.lower()
    for key, val in _COMPETITION_DB.items():
        if key in name_lower:
            return val
    # 默认：无法识别 → 校级
    return {"level": 4, "level_name": "校级", "bonus_score": 2}
