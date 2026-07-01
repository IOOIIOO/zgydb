"""发展路径服务：调用联网搜索 + LLM个性化 + 写DB"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from sqlmodel import Session, select
from app.models.development import DevelopmentPath
from app.models.direction import Direction
from app.models.progress import UserProgress
from app.services.model_interface import search_resources
from app.services.real_models.unified_analyzer import generate_development_path_local


def generate_path(session: Session, user_id: int, direction_id: int, position_id: int | None) -> dict:
    direction = session.get(Direction, direction_id)
    name = direction.name if direction else "未知方向"

    # 查用户画像用于个性化
    from app.models.ability import AbilityPortrait
    portrait = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)
    ).first()
    user_context = {
        "education": portrait.education if portrait else "",
        "knowledge_score": portrait.knowledge_score if portrait else 0,
        "tool_score": portrait.tool_score if portrait else 0,
        "project_score": portrait.project_score if portrait else 0,
        "skills": portrait.raw_extracted_data.get("skills", []) if portrait and portrait.raw_extracted_data else [],
        "strengths": portrait.strengths if portrait else [],
        "weaknesses": portrait.weaknesses if portrait else [],
    }

    # 查已有版本号
    existing = session.exec(
        select(DevelopmentPath)
        .where(DevelopmentPath.user_id == user_id)
        .order_by(DevelopmentPath.version.desc())
    ).first()
    version = (existing.version + 1) if existing else 1

    # 并行执行：联网搜索资源（百炼）+ 本地路径生成
    def _search():
        return search_resources(name)

    def _gen_path():
        return generate_development_path_local(name, user_context)

    with ThreadPoolExecutor(max_workers=2) as pool:
        resources_future = pool.submit(_search)
        path_future = pool.submit(_gen_path)
        resources = resources_future.result()
        paths = path_future.result()

    if not all(k in paths for k in ("short_term", "mid_term", "long_term")):
        raise RuntimeError("LLM 返回JSON缺少必要字段")

    record = DevelopmentPath(
        user_id=user_id,
        direction_id=direction_id,
        position_id=position_id,
        short_term_path=paths["short_term"],
        mid_term_path=paths["mid_term"],
        long_term_path=paths["long_term"],
        resource_list=resources,
        version=version,
    )
    session.add(record)

    # 更新进度
    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
    if progress:
        progress.step4_completed = True
        if progress.current_step < 5:
            progress.current_step = 5
        progress.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(record)

    return {
        "id": record.id,
        "direction_id": direction_id,
        "position_id": position_id,
        "short_term_path": record.short_term_path,
        "mid_term_path": record.mid_term_path,
        "long_term_path": record.long_term_path,
        "resource_list": record.resource_list,
        "version": record.version,
    }
