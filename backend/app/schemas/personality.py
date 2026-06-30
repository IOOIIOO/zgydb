"""性格分析请求/响应模型"""
from pydantic import BaseModel


class SubmitAnswersRequest(BaseModel):
    """提交答案请求"""
    answers: dict[int, str]  # {question_id: "a"|"b"}


class PersonalityResultResponse(BaseModel):
    """性格测评结果响应"""
    id: int | None = None
    personality_type: str
    intensity_level: int
    ei_score: int
    sn_score: int
    tf_score: int
    jp_score: int
    strengths: list[str] = []
    weaknesses: list[str] = []
    portrait_description: str = ""
    direction_tendencies: list[str] = []
    created_at: str | None = None

    class Config:
        from_attributes = True
