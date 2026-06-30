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
from app.services.model_interface import analyze_position_match
from app.models.position import Position
from app.models.ability import AbilityPortrait

router = APIRouter()


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
        "knowledge_score": portrait.knowledge_score if portrait else 72,
        "tool_score": portrait.tool_score if portrait else 78,
        "project_score": portrait.project_score if portrait else 65,
        "education": portrait.education if portrait else "本科",
    }

    match_data = analyze_position_match(
        user_portrait,
        {"title": position.title, "description": position.description or ""},
    )

    return {
        "id": position.id,
        "title": position.title,
        "description": position.description or "",
        "city": position.city or "",
        "industry": position.industry or "",
        "salary_range": position.salary_range or "",
        "education_requirement": position.education_requirement or "本科",
        "match_analysis": match_data,
    }
