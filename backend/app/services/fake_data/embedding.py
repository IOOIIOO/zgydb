"""
M5 — Embedding 模型：文本向量化 + 余弦相似度排序

调用位置：岗位推荐模块 — 匹配环节

TODO: 替换为真实 Embedding 模型（如 text-embedding-3 / bge-large-zh / m3e）
预期模型类型：文本嵌入模型（Text Embedding Model）
"""

import random


def FAKE_vectorize_and_match(user_profile: dict, positions: list[dict]) -> list[dict]:
    """
    模拟将用户画像与岗位列表进行向量化匹配并排序。

    Args:
        user_profile: 用户能力画像（当前不影响结果）
        positions: 岗位列表，每个岗位含 id、title 等字段

    Returns:
        带 match_score 的岗位列表，按分数降序排列
    """
    results = []
    for pos in positions:
        # 生成 60-95 之间的随机匹配分数
        score = round(random.uniform(60.0, 95.0), 1)
        results.append({
            "position_id": pos.get("id", 0),
            "position_title": pos.get("title", ""),
            "match_score": score,
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
