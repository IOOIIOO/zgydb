"""岗位推荐路由

GET  /api/v1/recommendation/directions  → 方向列表
POST /api/v1/recommendation/recommend    → 提交方向，返回推荐岗位
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.routers.auth import _get_current_user
from app.schemas.direction import DirectionBrief
from app.schemas.recommendation import RecommendRequest, PositionItem, PositionDetailResponse
from app.schemas.user import UserResponse
from app.services.recommendation_service import get_direction_options, recommend
from app.services.model_interface import analyze_position_match_local, vectorize_and_match
from app.models.position import Position
from app.models.ability import AbilityPortrait
from app.models.progress import UserProgress

router = APIRouter()


def _require_step(session: Session, user_id: int, required_step: int, step_name: str) -> None:
    """校验上一步是否完成，未完成返回 400"""
    progress = session.exec(
        select(UserProgress).where(UserProgress.user_id == user_id)
    ).first()
    checks = {2: "step1_completed", 3: "step2_completed", 4: "step3_completed", 5: "step4_completed"}
    field = checks.get(required_step)
    if field and (not progress or not getattr(progress, field, False)):
        raise HTTPException(status_code=400, detail=f"请先完成{step_name}")


@router.get("/directions", response_model=list[DirectionBrief])
def list_directions(session: Session = Depends(get_session)):
    """获取可选方向列表"""
    return get_direction_options(session)


@router.post("/recommend", response_model=list[PositionItem])
def recommend_positions(
    body: RecommendRequest,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """提交选定的方向，返回推荐岗位列表"""
    _require_step(session, current_user.id, 2, "能力评估（第二步）")
    results = recommend(session, current_user.id, body.direction_id)
    if not results:
        raise HTTPException(status_code=404, detail="该方向下没有匹配的岗位")
    return results


@router.get("/positions/{position_id}/detail", response_model=PositionDetailResponse)
def get_position_detail(
    position_id: int,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """获取单个岗位的详细信息及用户匹配分析"""
    position = session.get(Position, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="岗位不存在")

    portrait = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == current_user.id)
    ).first()

    user_portrait = {
        "knowledge_score": portrait.knowledge_score if portrait else 0,
        "tool_score": portrait.tool_score if portrait else 0,
        "project_score": portrait.project_score if portrait else 0,
        "education": portrait.education if portrait else "",
        "skills": portrait.raw_extracted_data.get("skills", []) if portrait and portrait.raw_extracted_data else [],
        "strengths": portrait.strengths if portrait else [],
        "weaknesses": portrait.weaknesses if portrait else [],
    }

    # 计算 embedding 语义相似度（先算，作为 overall_match_score）
    emb_result = vectorize_and_match(
        user_portrait,
        [{"id": position.id, "title": position.title, "description": position.description or ""}],
    )
    embedding_score = emb_result[0]["match_score"] if emb_result else 0.0

    # 本地模型做定性分析（不再独立打分）
    match_data = analyze_position_match_local(
        user_portrait,
        {"title": position.title, "description": position.description or ""},
    )

    # overall_match_score 直接从 embedding 取，保证列表/详情分数一致
    match_data["overall_match_score"] = embedding_score

    # 确保必要子字段存在
    for key in ["knowledge_match", "tool_match", "project_match"]:
        if key not in match_data:
            match_data[key] = {"user_score": 0, "required_score": 0, "verdict": "mismatch", "detail": ""}

    if "recommendation_reason" not in match_data:
        match_data["recommendation_reason"] = ""
    if "skill_gaps" not in match_data:
        match_data["skill_gaps"] = []
    if "strength_points" not in match_data:
        match_data["strength_points"] = []
    if "education_match" not in match_data:
        match_data["education_match"] = {
            "user_education": portrait.education if portrait else "",
            "required_education": position.education_requirement or "",
            "verdict": "mismatch",
        }

    return {
        "id": position.id,
        "title": position.title,
        "description": position.description or "",
        "city": position.city or "",
        "industry": position.industry or "",
        "salary_range": position.salary_range or "",
        "education_requirement": position.education_requirement or "本科",
        "match_analysis": match_data,
        "embedding_match_score": embedding_score,
    }
