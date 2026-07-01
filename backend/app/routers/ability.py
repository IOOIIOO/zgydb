"""能力评估路由

POST /api/v1/ability/upload    — 上传简历文件
POST /api/v1/ability/describe  — 提交文字描述
GET  /api/v1/ability/portrait  — 获取已保存画像
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select

from app.database import get_session
from app.models.ability import AbilityPortrait
from app.routers.auth import _get_current_user
from app.schemas.ability import AbilityPortraitResponse, ChatRequest, ChatResponse, DescribeRequest, ResumeSummary
from app.schemas.user import UserResponse
from app.services.ability_service import process_description, process_resume_file
from app.services.real_models.unified_analyzer import chat_response_local

router = APIRouter()


@router.post("/upload", response_model=dict)
def upload_resume(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """上传简历文件（PDF/图片），返回能力画像"""
    try:
        content = file.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="无法读取文件")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")
    return process_resume_file(session, current_user.id, content)


@router.post("/describe", response_model=dict)
def describe_self(
    body: DescribeRequest,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """提交文字描述，返回能力画像"""
    if len(body.text.strip()) < 20:
        raise HTTPException(status_code=400, detail="请至少输入 20 个字描述你的经历")
    return process_description(session, current_user.id, body.text)


@router.get("/portrait")
def get_portrait(
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """获取已保存的能力画像（无数据时返回 200 null，不报 404）"""
    portrait = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == current_user.id)
    ).first()
    if portrait is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(content=None, status_code=200)

    certs = []
    comps = []
    from app.models.certificate import CertificateRecord
    from app.models.competition import CompetitionRecord
    for c in session.exec(select(CertificateRecord).where(CertificateRecord.user_id == current_user.id)).all():
        certs.append({"name": c.certificate_name, "level": c.level, "level_name": c.level_name, "score": c.score})
    for c in session.exec(select(CompetitionRecord).where(CompetitionRecord.user_id == current_user.id)).all():
        comps.append({"name": c.competition_name, "level": c.level, "level_name": c.level_name, "bonus_score": c.bonus_score})

    return AbilityPortraitResponse(
        id=portrait.id,
        education=portrait.education or "",
        knowledge_score=portrait.knowledge_score or 0,
        tool_score=portrait.tool_score or 0,
        project_score=portrait.project_score or 0,
        scoring_basis=portrait.scoring_basis or {},
        logic_label=portrait.logic_label or "",
        communication_label=portrait.communication_label or "",
        cert_competition_label=portrait.cert_competition_label or "",
        learning_label=portrait.learning_label or "",
        label_inference_basis=portrait.label_inference_basis or {},
        strengths=portrait.strengths or [],
        weaknesses=portrait.weaknesses or [],
        certificates=certs,
        competitions=comps,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """AI 引导式对话：接收用户消息，返回 AI 回复

    前端按 stage 顺序调用：
    greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis

    当 stage="file_uploaded" 时，直接返回 portrait_ready=True
    """
    result = chat_response_local(body.stage, body.message)

    return ChatResponse(
        reply=result["reply"],
        next_stage=result["next_stage"],
        portrait_ready=result["portrait_ready"],
    )
