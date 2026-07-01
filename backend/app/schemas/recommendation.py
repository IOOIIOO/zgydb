"""岗位推荐请求/响应模型"""
from typing import Optional
from pydantic import BaseModel


class RecommendRequest(BaseModel):
    """提交方向选择请求"""
    direction_id: int


class PositionItem(BaseModel):
    """推荐岗位条目"""
    id: int
    title: str
    description: str
    city: str
    salary_range: str
    match_score: float
    recommendation_reason: str


class DimensionMatch(BaseModel):
    """单维度匹配分析"""
    user_score: int
    required_score: int
    verdict: str  # "match" | "partial" | "mismatch"
    detail: str


class SkillGap(BaseModel):
    """技能差距"""
    skill: str
    importance: str  # "重要" | "加分" | "可选"
    suggestion: str


class StrengthPoint(BaseModel):
    """优势点"""
    skill: str
    level: str


class EducationMatch(BaseModel):
    """学历匹配"""
    user_education: str
    required_education: str
    verdict: str


class MatchAnalysis(BaseModel):
    """完整匹配分析"""
    knowledge_match: DimensionMatch
    tool_match: DimensionMatch
    project_match: DimensionMatch
    overall_match_score: Optional[float] = None
    recommendation_reason: str
    skill_gaps: list[SkillGap]
    strength_points: list[StrengthPoint]
    education_match: EducationMatch


class PositionDetailResponse(BaseModel):
    """岗位详情 + 匹配分析 响应"""
    id: int
    title: str
    description: str
    city: str
    industry: str
    salary_range: str
    education_requirement: str
    match_analysis: MatchAnalysis
    embedding_match_score: Optional[float] = None
