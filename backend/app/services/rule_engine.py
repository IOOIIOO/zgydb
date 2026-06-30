"""
规则引擎 — 纯代码逻辑，不调用任何模型

功能：
1. 根据答案计算四维度得分
2. 判定人格类型和强度档次
3. 匹配 48 套 MBTI 描述模板
"""

import json
import os


def _load_json(filename: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "static", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_scores(answers: dict[int, str]) -> dict[str, int]:
    """
    根据用户答案计算四维度原始得分。

    Args:
        answers: {question_id: "a"|"b"}

    Returns:
        {"E": 7, "I": 3, "S": 5, "N": 5, "T": 6, "F": 4, "J": 8, "P": 2}
    """
    questions_data = _load_json("mbti_questions.json")
    questions = {q["id"]: q for q in questions_data["questions"]}

    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    for qid, choice in answers.items():
        q = questions.get(qid)
        if q is None or choice not in ("a", "b"):
            continue

        dim = q["dimension"]  # "EI", "SN", "TF", "JP"
        if dim == "EI":
            scores["E" if choice == "a" else "I"] += 1
        elif dim == "SN":
            scores["S" if choice == "a" else "N"] += 1
        elif dim == "TF":
            scores["T" if choice == "a" else "F"] += 1
        elif dim == "JP":
            scores["J" if choice == "a" else "P"] += 1

    return scores


def determine_type_and_intensity(scores: dict[str, int]) -> dict:
    """
    从四维度得分判定人格类型与强度档。

    强度：|A-B| 在 1-3 → 1档, 4-6 → 2档, 7+ → 3档
    """
    mappings = [
        ("E", "I", "ei_score"),
        ("S", "N", "sn_score"),
        ("T", "F", "tf_score"),
        ("J", "P", "jp_score"),
    ]

    type_chars = []
    intensity_scores = {}

    for left, right, key in mappings:
        left_v = scores[left]
        right_v = scores[right]
        diff = abs(left_v - right_v)

        if diff <= 3:
            intensity = 1
        elif diff <= 6:
            intensity = 2
        else:
            intensity = 3

        type_chars.append(left if left_v >= right_v else right)
        intensity_scores[key] = diff

    personality_type = "".join(type_chars)

    # 整体强度取四维度差的均值
    avg_diff = sum(intensity_scores.values()) / 4
    if avg_diff <= 3:
        overall_intensity = 1
    elif avg_diff <= 6:
        overall_intensity = 2
    else:
        overall_intensity = 3

    return {
        "personality_type": personality_type,
        "intensity_level": overall_intensity,
        "ei_score": scores["E"],
        "sn_score": scores["S"],
        "tf_score": scores["T"],
        "jp_score": scores["J"],
    }


def match_template(personality_type: str, intensity_level: int) -> dict:
    """匹配 48 套 MBTI 模板中对应的一套"""
    templates_data = _load_json("mbti_templates.json")
    templates = templates_data["templates"]
    key = f"{personality_type}_{intensity_level}"
    return templates.get(key, {})
