"""报告生成路由"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
import os
from app.database import get_session
from app.routers.auth import _get_current_user
from app.models.progress import UserProgress
from app.schemas.user import UserResponse
from app.services.report_service import generate, get_history, get_detail
from app.config import settings

router = APIRouter()

@router.post("/generate")
def gen(current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    progress = session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id)).first()
    if not progress or not progress.step4_completed:
        raise HTTPException(status_code=400, detail="请先完成趋势与发展（第四步）")
    return generate(session, current_user.id)

@router.get("/list")
def list_reports(current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    return get_history(session, current_user.id)

@router.get("/{report_id}")
def detail(report_id: int, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    r = get_detail(session, report_id)
    if not r: raise HTTPException(status_code=404, detail="报告不存在")
    return r

@router.get("/{report_id}/pdf")
def download(report_id: int, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    r = get_detail(session, report_id)
    if not r: raise HTTPException(status_code=404, detail="报告不存在")
    pdf_dir = os.path.abspath(settings.REPORT_DIR)
    pdf_path = os.path.join(pdf_dir, f"report_{current_user.id}_v{r['version']}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, filename=f"report_v{r['version']}.pdf", media_type="application/pdf")
    raise HTTPException(status_code=404, detail="PDF文件尚未生成")
