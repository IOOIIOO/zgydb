"""发展路径服务：调用 M3 假数据 + 写DB"""

from datetime import datetime
from sqlmodel import Session, select
from app.models.development import DevelopmentPath
from app.models.direction import Direction
from app.models.progress import UserProgress
from app.services.model_interface import search_resources


def generate_path(session: Session, user_id: int, direction_id: int, position_id: int | None) -> dict:
    direction = session.get(Direction, direction_id)
    name = direction.name if direction else "未知方向"
    resources = search_resources(name)

    # 查已有版本号
    existing = session.exec(
        select(DevelopmentPath)
        .where(DevelopmentPath.user_id == user_id)
        .order_by(DevelopmentPath.version.desc())
    ).first()
    version = (existing.version + 1) if existing else 1

    record = DevelopmentPath(
        user_id=user_id,
        direction_id=direction_id,
        position_id=position_id,
        short_term_path={
            "duration": "6个月-1年",
            "goal": f"掌握{name}核心入门技能，能独立完成基础工作",
            "skills": ["核心工具链", "基础理论", "行业术语", "基本工作流程"],
            "resources": resources[:3],
        },
        mid_term_path={
            "duration": "1-3年",
            "goal": f"在{name}领域形成专业深度，负责中等复杂度项目",
            "skills": ["高级专业技能", "项目管理", "跨部门协作", "技术方案设计"],
            "milestones": ["独立负责项目模块", "获得相关认证", "积累行业人脉"],
        },
        long_term_path={
            "duration": "3-5年",
            "goal": f"成为{name}领域资深专家或技术管理者",
            "directions": ["技术专家", "管理路线", "创业路线", "咨询培训"],
            "advanced_skills": ["架构设计", "团队领导", "行业影响力", "商业思维"],
        },
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
