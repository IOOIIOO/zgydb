"""能力评估请求/响应模型"""
from pydantic import BaseModel


class ResumeSummary(BaseModel):
    """提取的信息摘要"""
    education: str = ""
    school: str = ""
    major: str = ""
    skills: list[str] = []
    certificates: list[dict] = []
    competitions: list[dict] = []
    projects: list[dict] = []
    social_experience: list[dict] = []


class AbilityPortraitResponse(BaseModel):
    """完整能力画像"""
    id: int | None = None
    education: str = ""
    knowledge_score: int = 0
    tool_score: int = 0
    project_score: int = 0
    scoring_basis: dict = {}
    logic_label: str = ""
    communication_label: str = ""
    cert_competition_label: str = ""
    learning_label: str = ""
    label_inference_basis: dict = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    certificates: list[dict] = []
    competitions: list[dict] = []

    class Config:
        from_attributes = True


class DescribeRequest(BaseModel):
    """文字描述请求"""
    text: str


class ChatRequest(BaseModel):
    """对话消息请求"""
    message: str
    stage: str = "greeting"


class ChatResponse(BaseModel):
    """对话消息响应"""
    reply: str
    next_stage: str
    portrait_ready: bool = False
