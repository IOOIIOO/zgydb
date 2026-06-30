"""
M2 — 通用大模型：文本处理类任务（5个功能点）

调用位置：
- M2-1: 能力评估 — 对话描述提取结构化信息
- M2-2: 能力评估 — 三维度评分
- M2-3: 能力评估 — 四软能力标签推断
- M2-4: 岗位推荐 — 撰写个性化推荐理由
- M2-5: 报告生成 — 报告语言润色

TODO: 替换为真实通用大模型 API（如 GPT-4 / DeepSeek / 文心一言 / 通义千问）
预期模型类型：通用大语言模型（LLM）
"""


def FAKE_extract_from_text(description: str) -> dict:
    """
    M2-1: 从用户自由文本描述中提取结构化信息。

    Args:
        description: 用户输入的对话文本（当前不用）

    Returns:
        模拟的结构化提取结果
    """
    return {
        "education": "本科",
        "skills": ["Python", "SQL", "Excel高级", "沟通能力"],
        "certificates": [{"name": "英语四级 CET-4", "level": 2, "level_name": "国家级", "score": 4}],
        "competitions": [],
        "projects": [
            {
                "name": "课程设计项目",
                "role": "组长",
                "tech_stack": ["Python", "数据分析"],
                "description": "带领小组完成数据采集、清洗和可视化分析",
                "duration": "1个月",
            }
        ],
        "social_experience": [],
    }


def FAKE_score_abilities(skills: list) -> dict:
    """
    M2-2: 基于技能清单，对知识/工具/项目三维度打分。

    Args:
        skills: 技能名称列表（当前不用）

    Returns:
        三维度评分及依据
    """
    return {
        "knowledge_score": 72,
        "tool_score": 78,
        "project_score": 65,
        "scoring_basis": {
            "knowledge": "掌握计算机科学基础理论，对数据结构、算法、数据库有系统学习，但对前沿技术了解有限",
            "tool": "熟练使用 Python、SQL 等主流工具，具备一定的开发环境配置能力，Docker 等容器化工具尚在入门阶段",
            "project": "有校园级项目实践经验，能够独立完成中小规模功能开发，但缺乏企业级复杂系统经验",
        },
    }


def FAKE_infer_soft_labels(projects: list) -> dict:
    """
    M2-3: 根据项目经历推断四软能力标签。

    Args:
        projects: 项目经历列表（当前不用）

    Returns:
        四个软能力标签及推断依据
    """
    return {
        "logic_label": "良好",
        "communication_label": "良好",
        "cert_competition_label": "中等",
        "learning_label": "较强",
        "label_inference_basis": {
            "logic": "项目描述中出现'独立开发''系统设计'等动作词，表明具备一定的问题分析和方案设计能力",
            "communication": "有团队项目经验和学生会经历，具备基本的协作沟通能力",
            "cert_competition": "持有英语六级和计算机二级证书，竞赛获奖为校级，含金量中等",
            "learning": "掌握多种编程语言且能自学 Docker 等新技术，学习意愿和能力较强",
        },
    }


def FAKE_write_recommendation(user_profile: dict, position: dict) -> str:
    """
    M2-4: 为大模型撰写个性化岗位推荐理由。

    Args:
        user_profile: 用户能力画像（当前不用）
        position: 岗位信息（当前不用）

    Returns:
        个性化推荐理由文本
    """
    return (
        "根据你的能力画像分析，你的 Python 编程能力和数据分析基础与此岗位的核心要求高度匹配。"
        "你在校园项目中积累的后端开发经验表明你具备独立完成功能模块的能力，"
        "而数学建模竞赛的经历则体现了你的逻辑思维和团队协作能力。"
        "建议入职后重点提升企业级开发规范和系统架构设计能力，"
        "这将帮助你在该岗位上快速成长。"
    )


def FAKE_analyze_position_match(user_portrait: dict, position: dict) -> dict:
    """
    M2-4扩展: 分析用户能力画像与单个岗位的详细匹配度。

    功能描述: 基于用户3硬维度评分（知识/工具/项目）与岗位要求进行逐维度对比，
              给出差距分析、匹配理由、技能缺口和优势点。
    TODO: 替换为真实通用大模型（如 GPT-4 / DeepSeek / 文心一言 / 通义千问），
          传入用户完整能力画像和岗位描述，让模型生成逐维度分析和个性化匹配理由。
    预期模型类型: 通用大语言模型（LLM）
    调用位置: GET /recommendation/positions/{id}/detail — 岗位详情与匹配分析接口

    Args:
        user_portrait: 用户能力画像，含 knowledge_score/tool_score/project_score（当前用固定值）
        position: 岗位信息字典，含 title/description（当前用固定值）

    Returns:
        逐维度匹配分析、综合匹配度、推荐理由、技能差距、优势点
    """
    return {
        "knowledge_match": {
            "user_score": 72,
            "required_score": 70,
            "verdict": "match",
            "detail": "你的计算机基础理论知识（72分）达到了该岗位的知识要求（70分），数据结构、算法、数据库等方面储备充足。"
        },
        "tool_match": {
            "user_score": 78,
            "required_score": 80,
            "verdict": "partial",
            "detail": "你的工具熟练度（78分）略低于岗位要求（80分），Python和SQL已达标，但Docker等容器化工具尚需加强。"
        },
        "project_match": {
            "user_score": 65,
            "required_score": 60,
            "verdict": "match",
            "detail": "你的项目经验（65分）高于岗位要求（60分），校园项目虽规模有限但体现了独立开发能力。"
        },
        "overall_match_score": 85,
        "recommendation_reason": (
            "你的整体能力画像与该岗位匹配度较高（85%）。"
            "Python编程能力和数据分析基础是核心竞争力，校园项目中的后端开发经验表明你具备独立完成功能模块的能力。"
            "建议入职后重点提升容器化工具（Docker/K8s）的使用和微服务架构理解，这将帮助你快速适应企业级开发环境。"
        ),
        "skill_gaps": [
            {"skill": "Docker", "importance": "重要", "suggestion": "建议通过 Docker 官方文档和实战项目快速入门"},
            {"skill": "Kubernetes", "importance": "加分", "suggestion": "可在掌握 Docker 后学习，推荐《Kubernetes in Action》"},
            {"skill": "微服务架构", "importance": "重要", "suggestion": "建议阅读《微服务设计》并结合 Spring Cloud 实践"},
        ],
        "strength_points": [
            {"skill": "Python", "level": "熟练"},
            {"skill": "SQL", "level": "熟练"},
            {"skill": "数据分析", "level": "良好"},
        ],
        "education_match": {
            "user_education": "本科",
            "required_education": "本科",
            "verdict": "match",
        },
    }


def FAKE_chat_response(stage: str, user_message: str) -> dict:
    """
    M2-6: AI 引导式对话回复，用于能力评估聊天流程。

    功能描述: 根据当前对话阶段和用户输入，返回 AI 的引导性回复。
             流转: greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis
             当用户上传简历文件时（stage="file_uploaded"），直接返回 portrait_ready=True。
    TODO: 替换为真实通用大模型（如 GPT-4 / DeepSeek / 文心一言 / 通义千问），
          传入完整对话历史和当前阶段，让模型自然地引导用户完成能力信息收集。
    预期模型类型: 通用大语言模型（LLM）
    调用位置: POST /ability/chat — 能力评估对话接口

    Args:
        stage: 当前对话阶段 (greeting | ask_education | ask_skills | ask_projects | ask_certificates | file_uploaded)
        user_message: 用户最新消息内容

    Returns:
        AI 回复文本、下一步阶段、画像是否就绪
    """
    replies = {
        "greeting": {
            "reply": (
                "你好！我是你的 AI 能力评估助手 👋\n\n"
                "接下来我会问你几个问题，帮你全面分析能力画像。准备好了吗？\n\n"
                "首先，请告诉我你的**最高学历**是什么？（比如：本科、硕士、博士、大专等）"
            ),
            "next_stage": "ask_education",
            "portrait_ready": False,
        },
        "ask_education": {
            "reply": (
                f"了解了，你的学历是 **{user_message}**。\n\n"
                "接下来，请告诉我你掌握哪些**技术技能和工具**？\n"
                "比如编程语言、框架、办公软件等，越详细越好。"
            ),
            "next_stage": "ask_skills",
            "portrait_ready": False,
        },
        "ask_skills": {
            "reply": (
                "技能很全面！这些工具能力在职场上很有竞争力 💪\n\n"
                "再来说说你做过的**项目经历**吧。可以是课程设计、竞赛项目、实习项目等，"
                "描述一下你负责的内容和用到的技术。"
            ),
            "next_stage": "ask_projects",
            "portrait_ready": False,
        },
        "ask_projects": {
            "reply": (
                "很有价值的项目经验！这些实践经历对求职帮助很大。\n\n"
                "最后一个问题：你是否有**证书或竞赛经历**？\n"
                "英语等级、计算机等级、专业技能认证、数学建模等都可以。"
            ),
            "next_stage": "ask_certificates",
            "portrait_ready": False,
        },
        "ask_certificates": {
            "reply": "信息收集完毕！我正在根据你提供的信息生成能力画像，请稍等... 🎯",
            "next_stage": "analysis",
            "portrait_ready": True,
        },
        "file_uploaded": {
            "reply": "简历已收到！我正在分析你的简历内容并生成能力画像，请稍等... 📄✨",
            "next_stage": "analysis",
            "portrait_ready": True,
        },
    }
    return replies.get(stage, replies["greeting"])


def FAKE_polish_report(draft: str) -> str:
    """
    M2-5: 用大模型润色综合报告的语言表达。

    Args:
        draft: 原始报告文本（当前直接返回，不做真实润色）

    Returns:
        润色后的报告文本
    """
    # 假数据阶段直接返回原文，后续替换为 LLM 润色
    return draft
