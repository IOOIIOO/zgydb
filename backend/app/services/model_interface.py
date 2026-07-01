"""
模型接口抽象层

所有 AI 模型调用通过此层统一管理。
业务代码只需：from app.services.model_interface import extract_from_pdf

第13轮检修：删除 MODEL_MODE 开关，统一走真实模型。
"""

# ---- 真实模型 ----
from app.services.real_models.classifier import (
    classify_certificate, classify_competition,
)
from app.services.real_models.embedding import vectorize_and_match
from app.services.real_models.soft_labels import infer_soft_labels
from app.services.real_models.unified_analyzer import (
    analyze_resume,
    analyze_position_match_local,
    batch_write_recommendations_local,
    polish_report_local,
    generate_development_path_local,
)
from app.services.real_models.bailian_llm import (
    extract_from_pdf,
    extract_from_text,
    score_abilities,
    write_recommendation,
    batch_write_recommendations,
    analyze_position_match,
    polish_report,
    chat_response,
    search_trends,
    search_resources,
)

__all__ = [
    "extract_from_pdf",
    "extract_from_text",
    "score_abilities",
    "infer_soft_labels",
    "write_recommendation",
    "batch_write_recommendations",
    "analyze_position_match",
    "polish_report",
    "chat_response",
    "search_trends",
    "search_resources",
    "classify_certificate",
    "classify_competition",
    "vectorize_and_match",
    "analyze_resume",
    "analyze_position_match_local",
    "batch_write_recommendations_local",
    "polish_report_local",
    "generate_development_path_local",
]
