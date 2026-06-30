"""
数据库引擎与会话管理

使用 SQLModel，兼容 SQLAlchemy。
开发阶段使用 MySQL，通过 .env 中的 DATABASE_URL 配置。
"""

from sqlmodel import Session, SQLModel, create_engine
from app.config import settings

# 创建数据库引擎
# echo=settings.DEBUG 可在开发时打印 SQL 语句
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,   # 连接池健康检查
    pool_recycle=3600,    # 每小时回收连接
)


def create_db_and_tables() -> None:
    """
    创建所有表。

    开发阶段调用此函数自动建表。
    生产环境建议使用 Alembic 迁移。
    """
    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Session:
    """
    获取数据库会话的依赖注入函数。

    用法:
        @app.get("/example")
        def example(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
