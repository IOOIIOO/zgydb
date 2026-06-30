"""
应用配置模块

所有配置项从环境变量读取，提供合理的默认值。
生产环境通过 .env 文件或系统环境变量覆盖。
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件到环境变量


class Settings:
    """应用配置类"""

    # ---- 应用 ----
    APP_NAME: str = "Career Planning System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # ---- 数据库 ----
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/career_planning",
    )

    # ---- 安全 ----
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-string-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # ---- 文件上传 ----
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # ---- 报告 ----
    REPORT_DIR: str = os.getenv("REPORT_DIR", "reports")

    # ---- CORS ----
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # ---- 模型接口 (占位，后续替换真实模型时使用) ----
    MODEL_MODE: str = os.getenv("MODEL_MODE", "fake")  # "fake" | "real"
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")  # 阿里云百炼 API Key
    BAILIAN_WORKSPACE_ID: str = os.getenv("BAILIAN_WORKSPACE_ID", "")  # 百炼业务空间 ID
    BAILIAN_MODEL: str = os.getenv("BAILIAN_MODEL", "qwen3.7-plus")  # 默认模型

    @property
    def BAILIAN_BASE_URL(self) -> str:
        """百炼 OpenAI 兼容端点（带空间 ID 的专属域名）"""
        if self.BAILIAN_WORKSPACE_ID:
            return f"https://{self.BAILIAN_WORKSPACE_ID}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 兜底


settings = Settings()
