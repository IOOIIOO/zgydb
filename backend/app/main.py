"""
FastAPI 应用入口

注册路由、配置 CORS、启动事件。
开发环境自动建表。
"""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables

logger = logging.getLogger(__name__)


def _preload_embedding_model():
    """后台预加载 Embedding 模型，避免首次推荐时阻塞 ~10-15s"""
    try:
        from app.services.real_models.embedding import _get_model
        _get_model()
        logger.info("Embedding 模型预加载完成")
    except Exception as e:
        logger.warning(f"Embedding 模型预加载失败（首次推荐时再加载）: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时尝试自动建表 + 后台预加载模型"""
    if settings.DEBUG:
        try:
            create_db_and_tables()
            logger.info("数据库表创建/检查完成")
        except Exception as e:
            logger.warning(f"数据库不可用，跳过自动建表: {e}")
    # 后台预加载 Embedding 模型（不阻塞启动）
    import threading
    threading.Thread(target=_preload_embedding_model, daemon=True).start()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于多模态大模型的大学生专业能力分析与职业规划系统",
    lifespan=lifespan,
)

# ---- CORS 配置 ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- 根路径 ----
@app.get("/", tags=["Health"])
def root():
    """健康检查"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


# ---- 认证路由（第3.5轮） ----
from app.routers import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])

# ---- 快速了解（第4轮） ----
from app.routers import quick_overview
app.include_router(quick_overview.router, prefix="/api/v1/overview", tags=["快速了解"])

# ---- 性格分析（第5轮） ----
from app.routers import personality
app.include_router(personality.router, prefix="/api/v1/personality", tags=["性格分析"])

# ---- 能力评估（第7轮） ----
from app.routers import ability
app.include_router(ability.router, prefix="/api/v1/ability", tags=["能力评估"])

# ---- 岗位推荐（第8轮） ----
from app.routers import recommendation
app.include_router(recommendation.router, prefix="/api/v1/recommendation", tags=["岗位推荐"])

# ---- 趋势与发展（第9轮） ----
from app.routers import trend, development
app.include_router(trend.router, prefix="/api/v1/trend", tags=["趋势分析"])
app.include_router(development.router, prefix="/api/v1/development", tags=["发展路径"])

# ---- 报告生成（第10轮） ----
from app.routers import report
app.include_router(report.router, prefix="/api/v1/report", tags=["报告生成"])

# ---- 用户进度（Dashboard） ----
from app.routers import progress
app.include_router(progress.router, prefix="/api/v1/progress", tags=["用户进度"])
