"""
真实 Embedding 模型 — BAAI/bge-large-zh-v1.5 (本地 Python 部署)

替代文件: app/services/fake_data/embedding.py
模型来源: HuggingFace — BAAI/bge-large-zh-v1.5
"""

import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")  # 模型已缓存，不联网检查更新

from sentence_transformers import SentenceTransformer
import numpy as np

_model = None


def _get_model() -> SentenceTransformer:
    """延迟加载，只初始化一次"""
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
    return _model


def vectorize_and_match(user_profile: dict, positions: list[dict]) -> list[dict]:
    """
    将用户画像与岗位列表进行向量化匹配并排序（GPU加速）。

    Args:
        user_profile: 含 education/skills/strengths/weaknesses 等字段
        positions: 岗位列表 [{id, title, description, ...}]

    Returns:
        带 match_score 的岗位列表，按分数降序排列
    """
    model = _get_model()

    # 构建用户画像文本（只 encode 一次）
    user_text = _build_user_text(user_profile)

    # 批量编码：用户 + 所有岗位一次性 encode（GPU加速）
    pos_texts = [_build_position_text(pos) for pos in positions]
    all_texts = [user_text] + pos_texts
    all_embs = model.encode(all_texts, batch_size=32, normalize_embeddings=True)
    user_emb = all_embs[0]
    pos_embs = all_embs[1:]

    results = []
    for i, pos in enumerate(positions):
        # 余弦相似度 → 映射到 0-100
        similarity = float(np.dot(user_emb, pos_embs[i]))
        score = round(max(0.0, min(100.0, similarity * 100)), 1)
        results.append({
            "position_id": pos.get("id", 0),
            "position_title": pos.get("title", ""),
            "match_score": score,
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def _build_user_text(profile: dict) -> str:
    """将用户画像拼接为一段文本用于检索"""
    parts = []
    if profile.get("education"):
        parts.append(f"学历: {profile['education']}")
    skills = profile.get("skills", [])
    if skills:
        parts.append(f"技能: {', '.join(skills)}")
    strengths = profile.get("strengths", [])
    if strengths:
        parts.append(f"优势: {', '.join(strengths)}")
    weaknesses = profile.get("weaknesses", [])
    if weaknesses:
        parts.append(f"短板: {', '.join(weaknesses)}")
    return "；".join(parts) if parts else ""


def _build_position_text(pos: dict) -> str:
    """将岗位信息拼接为一段文本用于检索"""
    parts = []
    if pos.get("title"):
        parts.append(pos["title"])
    if pos.get("description"):
        parts.append(pos["description"])
    return "：".join(parts) if parts else pos.get("title", "未知岗位")
