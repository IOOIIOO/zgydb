"""
阿里云百炼 qwen3.7-plus — 业务函数层

替代:
- fake_data/multimodal.py: extract_from_pdf
- fake_data/general_llm.py: extract_from_text, score_abilities, write_recommendation, analyze_position_match, polish_report, chat_response
- fake_data/search.py: search_trends, search_resources
"""

import base64
import json
import re
from app.services.real_models.bailian_client import get_client


# ==================== M1: PDF/图片提取 ====================

def _bytes_to_b64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode()


def _guess_mime(file_bytes: bytes) -> str:
    """根据文件头判断 MIME 类型"""
    if file_bytes[:4] == b'%PDF':
        return "application/pdf"
    elif file_bytes[:4] == b'\x89PNG':
        return "image/png"
    elif file_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    return "image/png"  # 默认


def extract_from_pdf(file_bytes: bytes) -> dict:
    """从 PDF/图片简历中提取结构化信息
    - PDF: 本地提取文字 → LLM 结构化
    - 图片: 多模态直接识别
    """
    mime = _guess_mime(file_bytes)

    if mime == "application/pdf":
        try:
            from pypdf import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            full_text = "\n".join(text_parts)
            if full_text.strip():
                return extract_from_text(full_text)
        except Exception:
            pass
        return _empty_extract()

    # 图片 → 多模态（用括号计数提取嵌套JSON）
    client = get_client()
    b64 = _bytes_to_b64(file_bytes)
    text = client.chat([
        {"role": "system", "content": (
            "你是简历信息提取专家。从图片简历中提取以下字段，严格返回JSON：\n"
            '{"education":"学历","school":"学校","major":"专业",'
            '"skills":["技能1","技能2"],'
            '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
            '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"描述"}]}\n'
            "缺失字段用空字符串或空数组。严格只返回JSON。"
        )},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": "请提取这份图片简历的结构化信息，返回JSON"},
        ]},
    ], temperature=0.1, max_tokens=2048)

    try:
        json_str = client._extract_json(text)
        return json.loads(json_str) if json_str else _empty_extract()
    except Exception:
        return _empty_extract()


def _empty_extract() -> dict:
    return {"education": "", "school": "", "major": "", "skills": [],
            "certificates": [], "competitions": [], "projects": []}


# ==================== M2-1: 文本提取 ====================

def extract_from_text(description: str) -> dict:
    """从用户自由文本中提取结构化能力信息"""
    client = get_client()
    try:
        return client.chat_json([
            {"role": "system", "content": (
                "你是简历信息提取专家。从用户描述中提取以下字段，严格返回JSON：\n"
                '{"education":"学历","skills":["技能1","技能2"],'
                '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
                '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"描述"}]}\n'
                "缺失字段用空字符串或空数组。严格只返回JSON，不解释。"
            )},
            {"role": "user", "content": description},
        ], temperature=0.1)
    except Exception:
        return _empty_extract()


# ==================== M2-2: 三维度评分 ====================

def score_abilities(skills: list) -> dict:
    """基于技能清单评分"""
    client = get_client()
    try:
        return client.chat_json([
            {"role": "system", "content": (
                "你是大学生能力评估专家。根据技能清单对三个维度评分(0-100)并给出依据，严格返回JSON：\n"
                '{"knowledge_score":数字,"tool_score":数字,"project_score":数字,'
                '"scoring_basis":{"knowledge":"依据","tool":"依据","project":"依据"}}\n'
                "评分标准：60以下=薄弱，60-75=中等，76-85=良好，86-100=优秀。只返回JSON。"
            )},
            {"role": "user", "content": f"技能清单：{', '.join(skills) if skills else '无记录'}"},
        ], temperature=0.2)
    except Exception:
        return {"knowledge_score": 72, "tool_score": 78, "project_score": 65,
                "scoring_basis": {"knowledge": "", "tool": "", "project": ""}}


# ==================== M2-4: 推荐理由 ====================

def write_recommendation(user_profile: dict, position: dict) -> str:
    """撰写个性化岗位推荐理由"""
    client = get_client()
    try:
        return client.chat([
            {"role": "system", "content": (
                "你是职业规划顾问。为大学生写一段100-200字的岗位推荐理由，"
                "结合其能力画像和岗位要求，语言诚恳具体。"
            )},
            {"role": "user", "content": f"学生画像：{user_profile}\n岗位：{position}"},
        ], temperature=0.7, max_tokens=400)
    except Exception:
        return f"根据你的能力画像分析，{position.get('title', '该岗位')}与你的技能匹配度较高，建议重点关注。"


# ==================== M2-4ext: 岗位匹配分析 ====================

def analyze_position_match(user_portrait: dict, position: dict) -> dict:
    """逐维度分析用户与岗位匹配度"""
    client = get_client()
    try:
        return client.chat_json([
            {"role": "system", "content": (
                "你是岗位匹配分析专家。根据用户能力画像和岗位描述，进行三维度对比分析，严格返回JSON：\n"
                '{\n'
                '  "knowledge_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"分析"},\n'
                '  "tool_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"分析"},\n'
                '  "project_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"分析"},\n'
                '  "overall_match_score":数字,\n'
                '  "recommendation_reason":"综合推荐理由",\n'
                '  "skill_gaps":[{"skill":"技能名","importance":"重要|加分","suggestion":"学习建议"}],\n'
                '  "strength_points":[{"skill":"技能名","level":"熟练|良好|精通"}],\n'
                '  "education_match":{"user_education":"学历","required_education":"学历","verdict":"match|mismatch"}\n'
                '}\n'
                "只返回JSON，不解释。"
            )},
            {"role": "user", "content": f"用户画像：{user_portrait}\n岗位：{position}"},
        ], temperature=0.2)
    except Exception:
        return {
            "knowledge_match": {"user_score": 70, "required_score": 70, "verdict": "match", "detail": ""},
            "tool_match": {"user_score": 75, "required_score": 75, "verdict": "match", "detail": ""},
            "project_match": {"user_score": 60, "required_score": 60, "verdict": "match", "detail": ""},
            "overall_match_score": 72,
            "recommendation_reason": "综合能力匹配",
            "skill_gaps": [], "strength_points": [],
            "education_match": {"user_education": "本科", "required_education": "本科", "verdict": "match"},
        }


# ==================== M2-5: 报告润色 ====================

def polish_report(draft: str) -> str:
    """润色综合报告语言"""
    client = get_client()
    try:
        return client.chat([
            {"role": "system", "content": (
                "你是文字编辑。润色以下报告，修正语病、统一风格、提升专业感，"
                "保持原意和结构不变，不缩写内容。"
            )},
            {"role": "user", "content": draft},
        ], temperature=0.5, max_tokens=4096)
    except Exception:
        return draft  # 失败时返回原文


# ==================== M2-6: 对话引导 ====================

def chat_response(stage: str, user_message: str) -> dict:
    """AI引导式能力评估对话"""
    client = get_client()
    try:
        reply = client.chat([
            {"role": "system", "content": (
                "你是大学生职业规划AI助手，正在引导用户完成能力评估对话。\n"
                "对话阶段：greeting→ask_education→ask_skills→ask_projects→ask_certificates→analysis\n"
                f"当前阶段：{stage}\n"
                "规则：\n"
                "- 每个阶段友好地提出一个问题，引导用户描述相关信息\n"
                "- 语气温暖专业，像学长学姐在聊天，不要过于正式\n"
                "- 当用户回答了ask_certificates阶段后，回复中必须包含'[PORTRAIT_READY]'标记\n"
                "- file_uploaded阶段：表示简历已上传，回复中包含'[PORTRAIT_READY]'\n"
                "只输出对话内容，不要输出其他解释。"
            )},
            {"role": "user", "content": user_message or "开始"},
        ], temperature=0.7, max_tokens=500)
    except Exception:
        # fallback to fake data
        from app.services.fake_data.general_llm import FAKE_chat_response
        return FAKE_chat_response(stage, user_message)

    portrait_ready = "[PORTRAIT_READY]" in reply or stage in ("ask_certificates", "file_uploaded")
    reply_clean = reply.replace("[PORTRAIT_READY]", "").strip()

    return {
        "reply": reply_clean,
        "next_stage": _next_stage(stage),
        "portrait_ready": portrait_ready,
    }


def _next_stage(current: str) -> str:
    stages = ["greeting", "ask_education", "ask_skills", "ask_projects", "ask_certificates", "analysis"]
    if current == "file_uploaded":
        return "analysis"
    try:
        idx = stages.index(current)
        return stages[min(idx + 1, len(stages) - 1)]
    except ValueError:
        return "greeting"


# ==================== M3: 搜索 ====================

def search_trends(direction_name: str) -> dict:
    """搜索行业趋势（签名与 FAKE_search_trends 兼容）"""
    client = get_client()
    text = client.chat_with_search([
        {"role": "system", "content": (
            "你是行业趋势分析师。搜索并分析指定职业方向的最新发展趋势，严格返回JSON：\n"
            '{"trends":[{"dimension":"维度名","content":"分析内容（100字内）","score":数字}],"resources":[]}\n'
            "至少返回6个维度。只返回JSON，不解释。"
        )},
        {"role": "user", "content": f"分析'{direction_name}'职业方向的最新行业趋势，包括技术发展、市场需求、薪资水平、技能要求等维度"},
    ], temperature=0.3, max_tokens=4096)

    try:
        match = re.search(r"\{[\s\S]*\}", text)
        return json.loads(match.group(0)) if match else {"trends": [], "resources": []}
    except Exception:
        return {"trends": [], "resources": []}


def search_resources(direction_name: str) -> list[dict]:
    """搜索学习资源推荐（签名与 FAKE_search_resources 兼容：输入 str，返回 list）"""
    client = get_client()
    text = client.chat_with_search([
        {"role": "system", "content": (
            "你是学习资源规划师。根据职业方向搜索推荐学习资源，严格返回JSON：\n"
            '{"resources":[{"title":"资源名称","type":"课程|书籍|项目|社区","url":"","description":"推荐理由（80字内）","score":数字}]}\n'
            "至少返回5条资源。只返回JSON。"
        )},
        {"role": "user", "content": f"为'{direction_name}'方向的大学生推荐学习资源"},
    ], temperature=0.3, max_tokens=2048)

    try:
        match = re.search(r"\{[\s\S]*\}", text)
        result = json.loads(match.group(0)) if match else {"resources": []}
        return result.get("resources", [])
    except Exception:
        return []
