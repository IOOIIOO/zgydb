"""
M1 — 多模态大模型：从 PDF/图片提取结构化信息

调用位置：能力评估模块 — 用户上传简历文件

TODO: 替换为真实多模态模型（如 GPT-4V / Claude Vision / Gemini Pro Vision）
预期模型类型：多模态大模型（Vision-Language Model）
"""


def FAKE_extract_from_pdf(file_bytes: bytes) -> dict:
    """
    模拟从简历 PDF/图片中提取结构化信息。

    Args:
        file_bytes: 上传文件的原始字节（当前不用）

    Returns:
        模拟的简历结构化数据
    """
    return {
        "education": "本科",
        "school": "某某大学",
        "major": "计算机科学与技术",
        "graduation_year": "2025",
        "skills": [
            "Python", "Java", "MySQL", "Linux",
            "Git", "Docker基础", "数据分析基础",
        ],
        "certificates": [
            {"name": "大学英语六级 CET-6", "level": 2, "level_name": "国家级", "score": 6},
            {"name": "全国计算机等级考试二级 Python", "level": 2, "level_name": "国家级", "score": 4},
        ],
        "competitions": [
            {"name": "全国大学生数学建模竞赛", "level": 2, "level_name": "国家级", "bonus_score": 8},
            {"name": "校级程序设计大赛", "level": 4, "level_name": "校级", "bonus_score": 2},
        ],
        "projects": [
            {
                "name": "校园二手交易平台",
                "role": "后端开发",
                "tech_stack": ["Python", "Flask", "MySQL"],
                "description": "独立开发后端 API，实现用户认证、商品发布、搜索和交易功能。使用 JWT 做身份验证，Redis 做缓存。",
                "duration": "3个月",
            },
            {
                "name": "数据分析课程项目",
                "role": "数据分析",
                "tech_stack": ["Python", "Pandas", "Matplotlib"],
                "description": "对某电商平台用户行为数据进行分析，包括用户画像、购买转化率、RFM 模型分群。",
                "duration": "2个月",
            },
        ],
        "social_experience": [
            {"role": "学生会技术部干事", "description": "负责学院公众号维护和技术支持", "duration": "1年"},
        ],
    }
