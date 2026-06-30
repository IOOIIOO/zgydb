"""
M3 — 通用大模型 + 联网搜索：行业趋势搜索 + 学习资源搜索

调用位置：
- 趋势分析模块 — 行业趋势搜索
- 发展路径模块 — 学习资源搜索

TODO: 替换为真实搜索增强模型（如 GPT-4 + Bing Search / Perplexity API / 联网版大模型）
预期模型类型：LLM + Search API 组合
"""


def FAKE_search_trends(direction_name: str) -> dict:
    """
    M3-1: 搜索指定方向的行业趋势数据。

    Args:
        direction_name: 职业方向名称（当前不影响结果）

    Returns:
        含6个必含维度的趋势数据
    """
    return {
        "overview": f"随着数字化转型的深入推进，{direction_name}领域在未来3-5年将持续保持增长态势。"
                    "企业对相关人才的需求量稳步上升，同时对人才的综合素质要求也在不断提高。",
        "tech_impact": "人工智能和大数据技术正在深刻改变该领域的工作方式。"
                       "自动化工具替代了部分重复性工作，但同时也催生了新的高价值岗位。"
                       "从业者需要持续学习新技术以保持竞争力。",
        "regional_demand": "一线城市（北上广深）需求最为集中，占全国招聘量的55%以上。"
                           "新一线城市（杭州、成都、武汉、南京）需求增速最快，年均增长约20%。"
                           "二三线城市需求相对分散，但生活成本优势逐渐吸引人才回流。",
        "salary_trend": "应届生起薪约8-15K/月，3-5年经验可达15-30K/月。"
                        "头部企业及一线城市薪资上浮30-50%。"
                        "整体薪资水平年均增长5-8%，高于社会平均水平。",
        "entry_barrier": "学历门槛以本科为主（约占70%的岗位要求），部分研发岗位要求硕士及以上。"
                         "实习经验和项目经历在求职中越来越重要，已成为事实上的隐性门槛。"
                         "证书要求因细分领域而异，部分领域持证上岗是硬性要求。",
        "personal_analysis": (
            f"基于你的能力画像，你具备进入{ direction_name}领域的基本条件。"
            "建议重点补充以下方面的能力：1）行业专用的工具和技术栈；"
            "2）实际项目经验（可通过实习或个人项目积累）；"
            "3）软技能的持续提升（沟通、团队协作、时间管理）。"
            "预计经过6-12个月的系统学习和实践，你将具备较强的竞争力。"
        ),
    }


def FAKE_search_resources(direction_name: str) -> list[dict]:
    """
    M3-2: 搜索指定方向的学习资源。

    Args:
        direction_name: 职业方向名称（当前不影响结果）

    Returns:
        学习资源列表（含 URL 或 ISBN）
    """
    return [
        {
            "name": f"《{direction_name}从入门到实践》",
            "type": "书籍",
            "isbn": "978-7-115-00000-0",
            "url": "",
            "description": "适合初学者的系统性入门书籍，涵盖核心概念和实践案例",
        },
        {
            "name": f"{direction_name}实战课程",
            "type": "在线课程",
            "isbn": "",
            "url": "https://www.bilibili.com/video/example",
            "description": "B站上的免费实战教程，配合项目练习效果更好",
        },
        {
            "name": f"{direction_name}官方文档",
            "type": "官方文档",
            "isbn": "",
            "url": "https://example.com/docs",
            "description": "最权威的技术参考，建议熟练掌握查阅方法",
        },
        {
            "name": f"LeetCode 算法练习（{direction_name}方向）",
            "type": "在线平台",
            "isbn": "",
            "url": "https://leetcode.cn",
            "description": "适合准备技术面试，建议每天刷1-2题保持手感",
        },
        {
            "name": f"GitHub 开源项目合集 - {direction_name}",
            "type": "代码仓库",
            "isbn": "",
            "url": "https://github.com/topics/example",
            "description": "通过阅读优秀开源项目代码提升工程能力",
        },
    ]
