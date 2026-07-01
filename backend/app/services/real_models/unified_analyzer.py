"""
统一能力分析器 — LM Studio Qwen2.5-7B 一次调用完成全部分析

替代原来分散的:
- extract_from_text (百炼云端)
- score_abilities (百炼云端)
- infer_soft_labels (LM Studio)
- classify_certificate (LM Studio ×N)
- classify_competition (LM Studio ×N)

合并为一次本地推理，零网络开销。
"""

import json
import re
import requests

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct-1m"

SYSTEM_PROMPT = """你是资深HR简历分析师。根据简历文本，一次性完成：信息提取、能力评分、软标签推断、证书竞赛分级。

## 规则

### 1. 学历提取
从 博士/硕士/本科/大专/中专/高中 中选一个最匹配的。

### 2. 技能提取
提取所有专业技能、工具、编程语言、框架等，不要遗漏。

### 3. 三维度评分 (0-100)
- knowledge_score: 专业知识深度、理论基础。60以下=薄弱，60-75=中等，76-85=良好，86-100=优秀
- tool_score: 工具/技术栈掌握程度
- project_score: 项目经验丰富度、实际动手能力
每个分数给出10字内依据。

### 4. 软标签推断
- logic_label: 优秀/良好/中等/一般/较弱 —— 从项目技术复杂度、架构设计、问题拆解判断
- communication_label: 优秀/良好/中等/一般/较弱 —— 从是否担任负责人、团队协作判断
- learning_label: 强/较强/良好/中等/一般 —— 从技术栈多样性、自学能力判断
每项给出15字内依据。

### 5. 证书分级
级别: 1=国际顶级 2=国家级 3=省级 4=校级 5=其他
分数1-10，含金量越高分越高。

常见参考（同名直接匹配，近似的按级别对齐）:
- 1级/国际顶级: CFA, CPA, ACCA, PMP, FRM, AWS/Azure/GCP认证, CCIE, CISSP, 精算师, CFA特许
- 2级/国家级: CET-4/6, 英语四级/六级, 计算机等级考试, 软考, 教师资格证, 法律职业资格, 执业医师, 普通话等级, NCRE
- 3级/省级: 省级优秀毕业生, 省级三好学生, 各省专业技能证书
- 4级/校级: 校级奖学金, 校优秀学生, 学生会干部
- 5级/其他: 培训结业证, MOOC证书

### 6. 竞赛分级
级别: 1=国际级 2=国家级 3=省级 4=校级 5=院级/其他
加分值1-10，含金量越高分越高。

常见参考:
- 1级/国际级: ACM-ICPC, Kaggle, MCM/ICM(美赛), Google Code Jam, IOI/IMO
- 2级/国家级: CUMCM(国赛), 挑战杯, 互联网+, 蓝桥杯全国决赛, 电子设计大赛全国赛, 全国大学生英语竞赛
- 3级/省级: 蓝桥杯省赛, 各省数学建模, 电子设计大赛省赛, 机器人竞赛省赛
- 4级/校级: 校内编程赛, 校内创新创业大赛, 校企合作竞赛
- 5级/院级: 院系级比赛, 班级项目竞赛

### 7. 优势短板
- strengths: 2-3个具体优势
- weaknesses: 2-3个需要提升的方向

## 输出格式
严格返回一个完整 JSON，不要任何其他文字:
{
  "education": "本科",
  "school": "学校名",
  "major": "专业名",
  "skills": ["技能1", "技能2"],
  "knowledge_score": 75,
  "tool_score": 80,
  "project_score": 65,
  "scoring_basis": {"knowledge": "依据", "tool": "依据", "project": "依据"},
  "logic_label": "良好",
  "communication_label": "中等",
  "learning_label": "较强",
  "label_inference_basis": {"logic": "依据", "communication": "依据", "learning": "依据"},
  "certificates": [{"name": "证书名", "level": 2, "level_name": "国家级", "score": 7}],
  "competitions": [{"name": "竞赛名", "level": 2, "level_name": "国家级", "bonus_score": 8}],
  "projects": [{"name": "项目名", "role": "角色", "tech_stack": ["技术"], "description": "简述"}],
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["短板1", "短板2"]
}"""


def analyze_resume(text: str) -> dict:
    """一次调用 LM Studio，完成简历分析全部工作"""
    resp = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"【简历原文】\n{text[:3000]}"},
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
        },
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LM Studio 统一分析失败: HTTP {resp.status_code}")

    raw_text = resp.json()["choices"][0]["message"]["content"].strip()

    # 提取 JSON（可能被 markdown 代码块包裹）
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise RuntimeError(f"LM Studio 统一分析返回无法解析: {raw_text[:300]}")

    result = json.loads(json_match.group(0))

    # 填充缺失字段的默认值
    result.setdefault("education", "")
    result.setdefault("school", "")
    result.setdefault("major", "")
    result.setdefault("skills", [])
    result.setdefault("knowledge_score", 50)
    result.setdefault("tool_score", 50)
    result.setdefault("project_score", 50)
    result.setdefault("scoring_basis", {})
    result.setdefault("logic_label", "一般")
    result.setdefault("communication_label", "一般")
    result.setdefault("learning_label", "一般")
    result.setdefault("label_inference_basis", {})
    result.setdefault("certificates", [])
    result.setdefault("competitions", [])
    result.setdefault("projects", [])
    result.setdefault("strengths", [])
    result.setdefault("weaknesses", [])

    # 规范化证书字段
    for c in result["certificates"]:
        c.setdefault("level", 5)
        c.setdefault("level_name", "其他")
        c.setdefault("score", 1)

    # 规范化竞赛字段
    for c in result["competitions"]:
        c.setdefault("level", 4)
        c.setdefault("level_name", "校级")
        c.setdefault("bonus_score", 2)

    return result


# ==================== 本地对话引导 ====================

CHAT_SYSTEM_PROMPT = """你是大学生职业规划AI助手，正在引导用户完成能力评估对话。

对话阶段流转：greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis

规则：
- greeting: 热情打招呼，引导用户介绍自己的教育背景
- ask_education: 询问学校、专业、学历
- ask_skills: 询问掌握的技能、工具、编程语言
- ask_projects: 询问做过的项目经历
- ask_certificates: 询问证书和竞赛经历
- analysis: 告知用户画像已生成，可以查看结果
- file_uploaded: 简历已上传，回复中必须包含 [PORTRAIT_READY]
- 语气温暖专业，像学长学姐聊天
- 每次回复2-3句话，不要太长
- 当用户在 ask_certificates 阶段回复后，回复中必须包含 [PORTRAIT_READY]
- 当阶段为 file_uploaded 时，直接回复并包含 [PORTRAIT_READY]
只输出对话内容，不要输出其他解释。"""


def chat_response_local(stage: str, user_message: str) -> dict:
    """本地 LM Studio 驱动的能力评估对话"""
    try:
        resp = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"当前阶段：{stage}\n用户说：{user_message or '开始'}\n请回复："
                    )},
                ],
                "temperature": 0.7,
                "max_tokens": 256,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LM Studio chat error: {resp.status_code}")
        reply = resp.json()["choices"][0]["message"]["content"].strip()
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


# ==================== 本地岗位匹配分析 ====================

MATCH_SYSTEM_PROMPT = """你是人岗匹配分析师。对比用户画像和岗位要求，逐维度分析匹配度。

返回严格JSON：
{"knowledge_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},
 "tool_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},
 "project_match":{"user_score":数字,"required_score":数字,"verdict":"match|partial|mismatch","detail":"20字内"},
 "recommendation_reason":"50字内推荐理由",
 "skill_gaps":[{"skill":"技能","importance":"重要|加分","suggestion":"具体建议"}],
 "strength_points":[{"skill":"技能","level":"熟练|良好|精通"}],
 "education_match":{"user_education":"学历","required_education":"学历","verdict":"match|mismatch"}}

规则：
- user_score 从用户画像取，required_score 从岗位要求推断
- 匹配度判断要实事求是，不要全部写match
- 推荐理由结合用户优势和岗位需求，具体不泛泛"""


def analyze_position_match_local(user_portrait: dict, position: dict) -> dict:
    """本地模型：逐维度分析用户与岗位匹配度"""
    try:
        resp = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": MATCH_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"用户画像：{json.dumps(user_portrait, ensure_ascii=False)[:300]}\n"
                        f"岗位：{position.get('title','')}\n"
                        f"描述：{(position.get('description','') or '')[:200]}"
                    )},
                ],
                "temperature": 0.2,
                "max_tokens": 600,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LM Studio match error: {resp.status_code}")
        text = resp.json()["choices"][0]["message"]["content"].strip()
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            return json.loads(json_match.group(0))
        raise RuntimeError("无法解析JSON")
    except Exception:
        return {
            "knowledge_match": {"user_score": 50, "required_score": 50, "verdict": "partial", "detail": "分析暂不可用"},
            "tool_match": {"user_score": 50, "required_score": 50, "verdict": "partial", "detail": "分析暂不可用"},
            "project_match": {"user_score": 50, "required_score": 50, "verdict": "partial", "detail": "分析暂不可用"},
            "recommendation_reason": "该岗位与你的背景有一定匹配度，建议进一步了解岗位详情。",
            "skill_gaps": [],
            "strength_points": [],
            "education_match": {"user_education": "", "required_education": "", "verdict": "mismatch"},
        }


# ==================== 本地批量推荐理由 ====================

RECOMMEND_SYSTEM_PROMPT = """你是职业规划师。为每个岗位写40字内个性化推荐理由，结合用户技能和岗位需求。

返回严格JSON：
{"reasons":[{"position_id":数字,"reason":"40字内理由"}]}"""


def batch_write_recommendations_local(user_profile: dict, positions: list[dict]) -> dict[int, str]:
    """本地模型：批量生成推荐理由"""
    if not positions:
        return {}

    try:
        pos_summaries = [{
            "position_id": p.get("position_id") or p.get("id"),
            "title": p.get("title", ""),
            "description": (p.get("description", "") or "")[:100],
        } for p in positions]

        resp = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": RECOMMEND_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"用户画像：{json.dumps(user_profile, ensure_ascii=False)[:200]}\n"
                        f"岗位列表：{json.dumps(pos_summaries, ensure_ascii=False)}"
                    )},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LM Studio recommend error: {resp.status_code}")
        text = resp.json()["choices"][0]["message"]["content"].strip()
        json_match = re.search(r"\{[\s\S]*\}", text)
        result = json.loads(json_match.group(0)) if json_match else {}
        reasons = result.get("reasons", [])
    except Exception:
        reasons = []

    reason_map: dict[int, str] = {int(r["position_id"]): r.get("reason", "") for r in reasons if r.get("position_id")}
    for p in positions:
        pid = p.get("position_id") or p.get("id")
        if pid not in reason_map:
            reason_map[pid] = "该岗位与你的技能背景有一定的契合度。"
    return reason_map


# ==================== 本地报告润色 ====================

def polish_report_local(draft: str) -> str:
    """本地模型：精简润色报告"""
    try:
        resp = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "精简润色以下报告，修正语病，保持原意，删除冗余表述。直接输出润色后文本。"},
                    {"role": "user", "content": draft[:1500]},
                ],
                "temperature": 0.5,
                "max_tokens": 1024,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LM Studio polish error: {resp.status_code}")
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return draft


# ==================== 本地发展路径生成 ====================

PATH_SYSTEM_PROMPT = """你是职业规划师。根据用户职业方向和能力画像，生成个性化发展路径。

返回严格JSON：
{"short_term":{"duration":"6个月-1年","goal":"短期目标","skills":["技能1","技能2"]},
 "mid_term":{"duration":"1-3年","goal":"中期目标","skills":["技能"],"milestones":["里程碑"]},
 "long_term":{"duration":"3-5年","goal":"长期愿景","directions":["方向"],"advanced_skills":["高阶技能"]}}
每条内容30字内。短期结合当前水平，长期结合用户优势。"""


def generate_development_path_local(direction_name: str, user_context: dict) -> dict:
    """本地模型：生成个性化发展路径"""
    try:
        resp = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": PATH_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"方向：{direction_name}\n"
                        f"用户画像：{json.dumps(user_context, ensure_ascii=False)}"
                    )},
                ],
                "temperature": 0.5,
                "max_tokens": 600,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LM Studio path error: {resp.status_code}")
        text = resp.json()["choices"][0]["message"]["content"].strip()
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            return json.loads(json_match.group(0))
        raise RuntimeError("无法解析JSON")
    except Exception:
        return {
            "short_term": {"duration": "6个月-1年", "goal": f"打好{direction_name}基础", "skills": ["核心技能"]},
            "mid_term": {"duration": "1-3年", "goal": "成为独立贡献者", "skills": ["进阶技能"], "milestones": ["独立负责模块"]},
            "long_term": {"duration": "3-5年", "goal": "成为领域专家", "directions": ["技术深造"], "advanced_skills": ["架构设计"]},
        }
