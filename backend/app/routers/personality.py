"""
性格分析路由

GET  /api/v1/personality/questions   → 获取 MBTI 题目
POST /api/v1/personality/submit      → 提交答案，返回结果
GET  /api/v1/personality/result      → 获取已保存的结果
"""

import json
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.routers.auth import _get_current_user
from app.schemas.personality import PersonalityResultResponse, SubmitAnswersRequest
from app.schemas.user import UserResponse
from app.services.personality_service import get_existing_result, submit_answers

router = APIRouter()


def _load_questions() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "static", "mbti_questions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 返回题目时不暴露选项对应的维度方向
    return {
        "total": data["total"],
        "dimensions": data["dimensions"],
        "questions": data["questions"],
    }


@router.get("/questions")
def get_questions():
    """获取 MBTI 测评题目列表"""
    return _load_questions()


@router.post("/submit", response_model=PersonalityResultResponse)
def submit(
    body: SubmitAnswersRequest,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """提交 MBTI 答案，计算并存储结果"""
    if len(body.answers) < 20:
        raise HTTPException(status_code=400, detail="请完成至少一半的题目")

    record = submit_answers(session, current_user.id, body.answers)
    return PersonalityResultResponse(
        id=record.id,
        personality_type=record.personality_type,
        intensity_level=record.intensity_level,
        ei_score=record.ei_score,
        sn_score=record.sn_score,
        tf_score=record.tf_score,
        jp_score=record.jp_score,
        strengths=record.strengths or [],
        weaknesses=record.weaknesses or [],
        portrait_description=record.portrait_description or "",
        direction_tendencies=record.direction_tendencies or [],
        created_at=record.created_at.isoformat() if record.created_at else None,
    )


@router.get("/result")
def get_result(
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """获取当前用户已保存的性格测评结果（无数据时返回 200 null，不报 404）"""
    record = get_existing_result(session, current_user.id)
    if record is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(content=None, status_code=200)
    return PersonalityResultResponse(
        id=record.id,
        personality_type=record.personality_type,
        intensity_level=record.intensity_level,
        ei_score=record.ei_score,
        sn_score=record.sn_score,
        tf_score=record.tf_score,
        jp_score=record.jp_score,
        strengths=record.strengths or [],
        weaknesses=record.weaknesses or [],
        portrait_description=record.portrait_description or "",
        direction_tendencies=record.direction_tendencies or [],
        created_at=record.created_at.isoformat() if record.created_at else None,
    )
