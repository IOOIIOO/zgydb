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
            '{"education":"博士|硕士|本科|大专|中专|高中","school":"学校","major":"专业",'
            '"skills":["技能1","技能2"],'
            '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
            '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"描述"}]}\n'
            "education 字段必须从 博士/硕士/本科/大专/中专/高中 中选一个最匹配的值。"
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
    return client.chat_json([
        {"role": "system", "content": (
            "从用户描述提取简历信息，返回JSON：\n"
            '{"education":"博士|硕士|本科|大专|中专|高中","skills":["技能"],'
            '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
            '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"简述"}]}\n'
            "education 必须从 博士/硕士/本科/大专/中专/高中 选一个。缺失用空值。"
        )},
        {"role": "user", "content": description[:800]},
    ], temperature=0.1, max_tokens=600)


# ==================== M2-2: 三维度评分 ====================

def score_abilities(skills: list, education: str = "", projects: list = None, competitions: list = None) -> dict:
    """基于技能清单 + 学历/项目/竞赛背景综合评分"""
    client = get_client()
    context_parts = [f"技能：{', '.join(skills[:10]) if skills else '无'}"]
    if education:
        context_parts.append(f"学历：{education}")
    if projects:
        proj_names = [p.get("name", "") for p in projects if isinstance(p, dict)][:3]
        if proj_names:
            context_parts.append(f"项目：{', '.join(proj_names)}")
    if competitions:
        comp_names = [c.get("name", "") for c in competitions if isinstance(c, dict)][:3]
        if comp_names:
            context_parts.append(f"竞赛：{', '.join(comp_names)}")
    context = "；".join(context_parts)

    return client.chat_json([
        {"role": "system", "content": (
            "根据学生背景评三维分数(0-100)，返回JSON：\n"
            '{"knowledge_score":数字,"tool_score":数字,"project_score":数字,'
            '"scoring_basis":{"knowledge":"依据","tool":"依据","project":"依据"}}\n'
            "标准：60下=薄弱，60-75=中等，76-85=良好，86-100=优秀。依据20字内。"
        )},
        {"role": "user", "content": context[:400]},
    ], temperature=0.2, max_tokens=400)


# ==================== M2-4: 推荐理由 ====================

def write_recommendation(user_profile: dict, position: dict) -> str:
    """撰写个性化岗位推荐理由（单个，保留向后兼容）"""
    client = get_client()
    return client.chat([
        {"role": "system", "content": "为大学生写50字内岗位推荐理由，结合能力画像和岗位要求，诚恳具体。"},
        {"role": "user", "content": f"画像：{json.dumps(user_profile, ensure_ascii=False)[:200]}\n岗位：{position.get('title','')}"},
    ], temperature=0.7, max_tokens=150)


def batch_write_recommendations(user_profile: dict, positions: list[dict]) -> dict[int, str]:
    """批量生成推荐理由：一次 LLM 调用为所有岗位生成理由"""
    if not positions:
        return {}

    client = get_client()
    pos_summaries = []
    for p in positions:
        pos_summaries.append({
            "position_id": p.get("position_id") or p.get("id"),
            "title": p.get("title", ""),
            "description": (p.get("description", "") or "")[:100],
        })

    result = client.chat_json([
        {"role": "system", "content": (
            "为每个岗位写40字内推荐理由，结合用户技能。返回JSON：\n"
            '{"reasons":[{"position_id":数字,"reason":"理由"}]}'
        )},
        {"role": "user", "content": (
            f"画像：{json.dumps(user_profile, ensure_ascii=False)[:200]}\n"
            f"岗位：{json.dumps(pos_summaries, ensure_ascii=False)}"
        )},
    ], temperature=0.7, max_tokens=600)
    reasons = result.get("reasons", []) if result else []

    reason_map: dict[int, str] = {}
    for r in reasons:
        pid = r.get("position_id")
        if pid is not None:
            reason_map[int(pid)] = r.get("reason", "")

    for p in positions:
        pid = p.get("position_id") or p.get("id")
        if pid not in reason_map:
            reason_map[pid] = ""

    return reason_map


# ==================== M2-4ext: 岗位匹配分析 ====================

def analyze_position_match(user_portrait: dict, position: dict) -> dict:
    """逐维度分析用户与岗位匹配度（定性分析，不负责整体打分）"""
    client = get_client()
    return client.chat_json([
        {"role": "system", "content": (
            "对比用户画像和岗位，返回JSON：\n"
            '{"knowledge_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},'
            '"tool_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},'
            '"project_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},'
            '"recommendation_reason":"50字内推荐理由",'
            '"skill_gaps":[{"skill":"技能","importance":"重要|加分","suggestion":"建议"}],'
            '"strength_points":[{"skill":"技能","level":"熟练|良好|精通"}],'
            '"education_match":{"user_education":"学历","required_education":"学历","verdict":"match|mismatch"}}'
        )},
        {"role": "user", "content": f"画像：{json.dumps(user_portrait, ensure_ascii=False)[:200]}\n岗位：{position.get('title','')[:50]}"},
    ], temperature=0.2, max_tokens=600)


# ==================== M2-5: 报告润色 ====================

def polish_report(draft: str) -> str:
    """润色综合报告语言"""
    client = get_client()
    try:
        return client.chat([
            {"role": "system", "content": "精简润色报告，修正语病，保持原意，删除冗余表述。"},
            {"role": "user", "content": draft[:1500]},
        ], temperature=0.5, max_tokens=1024)
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
        return {
            "reply": "抱歉，AI 服务暂时不可用，请稍后重试。",
            "next_stage": _next_stage(stage),
            "portrait_ready": stage in ("ask_certificates", "file_uploaded"),
        }

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
    """搜索行业趋势，返回包含6个命名维度字段 + trends数组 + resources的完整结构"""
    client = get_client()
    try:
        text = client.chat_with_search([
            {"role": "system", "content": (
                "分析职业方向趋势，返回JSON：\n"
                '{"overview":"3-5年走向60字内",'
                '"tech_impact":"技术冲击60字内",'
                '"regional_demand":"地域差异60字内",'
                '"salary_trend":"薪资走向60字内",'
                '"entry_barrier":"门槛变化60字内",'
                '"personal_analysis":"个体影响60字内",'
                '"risk_warnings":["风险1","风险2","风险3"],'
                '"resources":[{"title":"标题","url":"真实链接"}]}\n'
                "url必须是搜索结果中的真实链接，无则留空。"
            )},
            {"role": "user", "content": f"分析'{direction_name}'方向的最新趋势"},
        ], temperature=0.3, max_tokens=1024)
    except Exception:
        return _empty_trends(direction_name)

    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return _empty_trends(direction_name)
        data = json.loads(match.group(0))
    except Exception:
        return _empty_trends(direction_name)

    # 构造 trends 数组供报告页面使用
    dim_map = [
        ("overview", "3-5年发展趋势"),
        ("tech_impact", "技术变革影响"),
        ("regional_demand", "地域需求差异"),
        ("salary_trend", "薪资走向"),
        ("entry_barrier", "入门门槛变化"),
        ("personal_analysis", "个体影响分析"),
    ]
    trends = []
    for key, label in dim_map:
        content = data.get(key, "")
        if content:
            trends.append({"dimension": label, "content": content, "score": 0})
    data["trends"] = trends

    if "risk_warnings" not in data:
        data["risk_warnings"] = []
    if "resources" not in data:
        data["resources"] = []

    return data


def _empty_trends(name: str) -> dict:
    return {
        "overview": "", "tech_impact": "", "regional_demand": "",
        "salary_trend": "", "entry_barrier": "", "personal_analysis": "",
        "risk_warnings": [],
        "resources": [],
        "trends": [],
    }


def search_resources(direction_name: str) -> list[dict]:
    """搜索学习资源推荐（签名与 FAKE_search_resources 兼容：输入 str，返回 list）"""
    client = get_client()
    try:
        text = client.chat_with_search([
            {"role": "system", "content": (
                "为方向推荐5条学习资源，返回JSON：\n"
                '{"resources":[{"name":"名称","type":"课程|书籍|项目|社区","url":"真实链接","description":"30字理由","score":数字}]}\n'
                "url必须是搜索结果真实链接，无则留空。"
            )},
            {"role": "user", "content": f"为'{direction_name}'方向推荐学习资源"},
        ], temperature=0.3, max_tokens=800)
    except Exception:
        return []

    try:
        match = re.search(r"\{[\s\S]*\}", text)
        result = json.loads(match.group(0)) if match else {"resources": []}
        resources = result.get("resources", [])
        # 兼容：如果 LLM 返回了 title 而非 name，做一次映射
        for r in resources:
            if "name" not in r and "title" in r:
                r["name"] = r.pop("title")
        return resources
    except Exception:
        return []
