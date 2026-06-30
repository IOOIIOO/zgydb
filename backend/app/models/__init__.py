"""
数据模型汇总

导入所有 SQLModel 表模型，确保 create_all() 能发现全部表。
"""

from app.models.user import User
from app.models.direction import Direction
from app.models.position import Position
from app.models.personality import PersonalityResult
from app.models.ability import AbilityPortrait
from app.models.certificate import CertificateRecord
from app.models.competition import CompetitionRecord
from app.models.recommendation import RecommendationRecord
from app.models.trend import TrendAnalysis
from app.models.development import DevelopmentPath
from app.models.report import Report
from app.models.progress import UserProgress

__all__ = [
    "User",
    "Direction",
    "Position",
    "PersonalityResult",
    "AbilityPortrait",
    "CertificateRecord",
    "CompetitionRecord",
    "RecommendationRecord",
    "TrendAnalysis",
    "DevelopmentPath",
    "Report",
    "UserProgress",
]
