"""
岗位推荐服务：学历过滤 → 相似度匹配（假数据）→ 性格约束过滤 → 推荐理由

规则引擎: 学历硬门槛过滤 + 性格约束过滤
模型调用: M5 (假数据匹配) + M2-4 (假数据推荐理由)
"""

from datetime import datetime

from sqlmodel import Session, select

from app.models.direction import Direction
from app.models.personality import PersonalityResult
from app.models.position import Position
from app.models.progress import UserProgress
from app.models.recommendation import RecommendationRecord
from app.services.model_interface import vectorize_and_match, write_recommendation


def get_direction_options(session: Session) -> list[Direction]:
    """获取可选方向列表（与快速了解同源）"""
    return list(
        session.exec(
            select(Direction).where(Direction.is_active == True).order_by(Direction.sort_order)
        ).all()
    )


def recommend(
    session: Session,
    user_id: int,
    direction_id: int,
) -> list[dict]:
    """执行岗位推荐全流程"""
    # 1. 获取用户能力画像
    from app.models.ability import AbilityPortrait
    portrait = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)
    ).first()
    user_education = portrait.education if portrait else "本科"

    # 2. 获取该方向下所有岗位
    positions = list(
        session.exec(
            select(Position).where(
                Position.direction_id == direction_id,
                Position.is_active == True,
            )
        ).all()
    )

    if not positions:
        return []

    # 3. 学历硬门槛过滤（规则引擎）
    filtered = _filter_by_education(positions, user_education)

    # 4. 性格约束过滤（规则引擎）
    personality = session.exec(
        select(PersonalityResult).where(PersonalityResult.user_id == user_id)
    ).first()
    if personality:
        direction = session.get(Direction, direction_id)
        filtered = _filter_by_personality(filtered, personality.personality_type, direction)

    # 5. 假数据相似度匹配（M5）
    pos_dicts = [
        {"id": p.id, "title": p.title, "description": p.description or ""}
        for p in filtered
    ]
    matched = vectorize_and_match({}, pos_dicts)

    # 6. 假数据推荐理由（M2-4）+ 写入推荐记录
    results = []
    old_recs = session.exec(
        select(RecommendationRecord).where(RecommendationRecord.user_id == user_id)
    ).all()
    for r in old_recs:
        session.delete(r)

    for item in matched[:10]:  # top 10
        pos = session.get(Position, item["position_id"])
        if not pos:
            continue
        reason = write_recommendation({}, {"title": pos.title})
        session.add(RecommendationRecord(
            user_id=user_id,
            position_id=pos.id,
            match_score=item["match_score"],
            recommendation_reason=reason,
        ))
        results.append({
            "id": pos.id,
            "title": pos.title,
            "description": (pos.description or "")[:300],
            "city": pos.city or "",
            "salary_range": pos.salary_range or "",
            "match_score": item["match_score"],
            "recommendation_reason": reason,
        })

    # 7. 更新进度
    progress = session.exec(
        select(UserProgress).where(UserProgress.user_id == user_id)
    ).first()
    if progress is None:
        progress = UserProgress(user_id=user_id)
        session.add(progress)
    progress.step3_completed = True
    if progress.current_step < 4:
        progress.current_step = 4
    progress.selected_direction_id = direction_id
    progress.updated_at = datetime.utcnow()

    session.commit()
    return results


def _filter_by_education(positions: list[Position], user_edu: str) -> list[Position]:
    """学历硬门槛过滤：岗位要求不低于用户学历"""
    edu_levels = {"博士": 6, "硕士": 5, "本科": 4, "大专": 3, "中专": 2, "高中": 1}
    user_level = edu_levels.get(user_edu, 4)
    return [p for p in positions if edu_levels.get(p.education_requirement or "本科", 4) <= user_level]


def _filter_by_personality(
    positions: list[Position], user_type: str, direction: Direction | None
) -> list[Position]:
    """性格约束后置过滤：排除被岗位排斥的人格类型"""
    if direction is None:
        return positions

    excluded: list[str] = direction.excluded_personality_types or []
    if user_type in excluded:
        return []  # 该方向排斥此人格，全部不推荐

    result = []
    for p in positions:
        pos_excluded: list[str] = p.excluded_personality_types or []
        if user_type not in pos_excluded:
            result.append(p)
    return result
