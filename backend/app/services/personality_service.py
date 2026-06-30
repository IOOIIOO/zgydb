"""
性格分析业务流程编排

submit_answers: 答案→计分→类型判定→模板匹配→写入DB→更新进度
"""

from datetime import datetime

from sqlmodel import Session, select

from app.models.personality import PersonalityResult
from app.models.progress import UserProgress
from app.services.rule_engine import (
    calculate_scores,
    determine_type_and_intensity,
    match_template,
)


def get_existing_result(session: Session, user_id: int) -> PersonalityResult | None:
    """获取用户已有的测评结果"""
    return session.exec(
        select(PersonalityResult).where(PersonalityResult.user_id == user_id)
    ).first()


def submit_answers(
    session: Session,
    user_id: int,
    answers: dict[int, str],
) -> PersonalityResult:
    """提交 MBTI 答案，计算并存储结果"""
    # 1. 计分
    scores = calculate_scores(answers)

    # 2. 类型判定
    result = determine_type_and_intensity(scores)

    # 3. 模板匹配
    template = match_template(result["personality_type"], result["intensity_level"])

    # 4. 写入 personality_results（先删旧结果，支持重测）
    existing = get_existing_result(session, user_id)
    if existing:
        session.delete(existing)
        session.flush()

    record = PersonalityResult(
        user_id=user_id,
        personality_type=result["personality_type"],
        intensity_level=result["intensity_level"],
        ei_score=result["ei_score"],
        sn_score=result["sn_score"],
        tf_score=result["tf_score"],
        jp_score=result["jp_score"],
        strengths=template.get("strengths", []),
        weaknesses=template.get("weaknesses", []),
        portrait_description=template.get("portrait_description", ""),
        direction_tendencies=template.get("direction_tendencies", []),
    )
    session.add(record)
    session.flush()

    # 5. 更新用户进度
    progress = session.exec(
        select(UserProgress).where(UserProgress.user_id == user_id)
    ).first()

    if progress is None:
        progress = UserProgress(user_id=user_id)
        session.add(progress)

    progress.step1_completed = True
    if progress.current_step < 2:
        progress.current_step = 2
    progress.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(record)
    return record
