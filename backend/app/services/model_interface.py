"""
模型接口抽象层（中间层）

所有 AI 模型调用通过此层统一管理。
.env 中 MODEL_MODE=real → 全部真实模型
.env 中 MODEL_MODE=fake → 全部假数据

业务代码只需：from app.services.model_interface import extract_from_pdf
"""

from app.config import settings

# ========== 统一开关 ==========
_is_real = settings.MODEL_MODE.lower().strip() == "real"

# ---- 假数据 ----
from app.services.fake_data.multimodal import FAKE_extract_from_pdf
from app.services.fake_data.general_llm import (
    FAKE_extract_from_text, FAKE_score_abilities, FAKE_infer_soft_labels,
    FAKE_write_recommendation, FAKE_polish_report, FAKE_analyze_position_match,
    FAKE_chat_response,
)
from app.services.fake_data.classifier import FAKE_classify_certificate, FAKE_classify_competition
from app.services.fake_data.embedding import FAKE_vectorize_and_match
from app.services.fake_data.search import FAKE_search_trends, FAKE_search_resources

# ---- 真实模型 ----
from app.services.real_models.classifier import (
    classify_certificate as _real_cert, classify_competition as _real_comp,
)
from app.services.real_models.embedding import vectorize_and_match as _real_vec
from app.services.real_models.soft_labels import infer_soft_labels as _real_labels
from app.services.real_models.bailian_llm import (
    extract_from_pdf as _real_extract_pdf,
    extract_from_text as _real_extract_text,
    score_abilities as _real_score,
    write_recommendation as _real_recommend,
    analyze_position_match as _real_match,
    polish_report as _real_polish,
    chat_response as _real_chat,
    search_trends as _real_trends,
    search_resources as _real_resources,
)

# ========== 对外接口 ==========
extract_from_pdf = _real_extract_pdf if _is_real else FAKE_extract_from_pdf
extract_from_text = _real_extract_text if _is_real else FAKE_extract_from_text
score_abilities = _real_score if _is_real else FAKE_score_abilities
infer_soft_labels = _real_labels  # 本地 Qwen2.5-7B，始终真实
write_recommendation = _real_recommend if _is_real else FAKE_write_recommendation
polish_report = _real_polish if _is_real else FAKE_polish_report
classify_certificate = _real_cert  # 本地 Qwen2.5-7B，始终真实
classify_competition = _real_comp  # 本地 Qwen2.5-7B，始终真实
vectorize_and_match = _real_vec  # 本地 bge-large-zh-v1.5，始终真实
search_trends = _real_trends if _is_real else FAKE_search_trends
search_resources = _real_resources if _is_real else FAKE_search_resources
analyze_position_match = _real_match if _is_real else FAKE_analyze_position_match
chat_response = _real_chat if _is_real else FAKE_chat_response
