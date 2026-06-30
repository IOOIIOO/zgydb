"""
种子数据脚本

用法：
    cd backend
    python -m app.seed

功能：
1. 创建 ~25 个职业发展方向（directions 表）
2. 从 positions_cleaned.csv 导入清洗后的岗位数据（positions 表）
3. 自动将 51 种岗位名称映射到对应方向

可重复运行：先清空 directions 和 positions 表，再重新导入。
"""

import os
import sys
from datetime import datetime

import pandas as pd
from sqlmodel import Session

# 确保 backend 目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, create_db_and_tables
from app.models.direction import Direction
from app.models.position import Position

# ============================================================
# 岗位名称 → 方向映射（51 种岗位 → 25 个方向）
# ============================================================
JOB_TO_DIRECTION: dict[str, str] = {
    # ---- 软件开发 ----
    "前端开发": "前端开发",
    "Java": "后端开发",
    "C/C++": "后端开发",
    # ---- 测试 ----
    "软件测试": "软件测试",
    "测试工程师": "软件测试",
    "硬件测试": "硬件测试",
    # ---- IT 技术 ----
    "实施工程师": "IT 技术支持",
    "技术支持工程师": "IT 技术支持",
    "弱电工程师": "IT 技术支持",
    "风电工程师": "IT 技术支持",
    # ---- 科研 ----
    "科研人员": "科研与研发",
    # ---- 销售 ----
    "销售运营": "销售",
    "销售工程师": "销售",
    "销售助理": "销售",
    "大客户代表": "销售",
    "广告销售": "销售",
    "电话销售": "电话销售",
    "网络销售": "网络销售",
    "客户经理": "客户经理",
    # ---- 市场/运营 ----
    "运营助理/专员": "运营",
    "社区运营": "运营",
    "内容审核": "运营",
    "新媒体运营": "新媒体运营",
    "市场营销": "市场营销",
    "APP推广": "APP推广",
    "游戏运营": "游戏运营",
    "游戏推广": "游戏推广",
    "产品专员/助理": "产品",
    # ---- 行政/管理 ----
    "总助/CEO助理/董事长助理": "行政管理",
    "行政专员/助理": "行政管理",
    "前台/总机/接待": "行政管理",
    "资料管理": "行政管理",
    "档案管理": "行政管理",
    # ---- 项目管理 ----
    "项目专员/助理": "项目管理",
    "项目经理/主管": "项目管理",
    "项目投标": "项目管理",
    "项目招投标": "项目管理",
    # ---- 人力资源 ----
    "猎头顾问": "人力资源",
    "招聘专员/助理": "人力资源",
    # ---- 商务 ----
    "BD经理": "商务拓展",
    "商务拓展": "商务拓展",
    "商务专员": "商务拓展",
    # ---- 法务 ----
    "律师": "法律",
    "律师助理": "法律",
    "知识产权/专利代理": "法律",
    "法务专员/助理": "法律",
    # ---- 客服 ----
    "综合客服": "客户服务",
    "电话客服": "客户服务",
    "网络客服": "客户服务",
    "售后客服": "客户服务",
    # ---- 质量管理 ----
    "质检员": "质量管理",
    "质量管理/测试": "质量管理",
    # ---- 管培 ----
    "储备经理人": "管理培训生",
    "管理培训生": "管理培训生",
    "储备干部": "管理培训生",
    "管培生/储备干部": "管理培训生",
    # ---- 翻译 ----
    "英语翻译": "翻译",
    "日语翻译": "翻译",
    # ---- 教育 ----
    "培训师": "教育培训",
    "教务管理": "教育培训",
    # ---- 数据/统计 ----
    "统计员": "数据分析",
    "数据分析师": "数据分析",
    # ---- 咨询 ----
    "咨询顾问": "咨询",
    # ---- 综合 ----
    "商务司机": "后勤综合",
}

# ============================================================
# 25 个方向的定义数据
# ============================================================
DIRECTION_DEFINITIONS: list[dict] = [
    {
        "name": "前端开发",
        "position_examples": ["前端开发工程师", "Web前端开发", "H5开发工程师"],
        "required_skills": ["HTML/CSS", "JavaScript", "React/Vue", "TypeScript", "前端工程化"],
        "development_trend": "前端技术栈持续演进，全栈化趋势明显。WebAssembly、微前端、Serverless等新技术正在改变前端开发范式。企业对前端工程师的要求从'会写页面'转向'能参与架构设计'，TypeScript已成标配。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 1,
    },
    {
        "name": "后端开发",
        "position_examples": ["Java开发工程师", "C/C++开发工程师", "Go开发工程师", "Python开发工程师"],
        "required_skills": ["Java/Python/Go/C++", "数据库MySQL/Redis", "Spring/微服务", "Linux", "系统设计"],
        "development_trend": "云原生和微服务架构持续深化，AI大模型应用开发成为新兴方向。Java仍占据企业级市场主流，Go在云基础设施领域快速增长。后端工程师需具备系统设计能力和跨栈思维。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 2,
    },
    {
        "name": "软件测试",
        "position_examples": ["软件测试工程师", "自动化测试工程师", "测试开发工程师"],
        "required_skills": ["测试方法论", "自动化测试工具", "Python/Shell", "CI/CD", "性能测试"],
        "development_trend": "测试左移和自动化测试成为主流，AI辅助测试用例生成正在兴起。纯手工测试岗位需求下降，测试开发一体化人才更受欢迎。",
        "excluded_personality_types": ["ENFP", "ENTP"],
        "excluded_trait_thresholds": {},
        "sort_order": 3,
    },
    {
        "name": "硬件测试",
        "position_examples": ["硬件测试工程师", "可靠性测试工程师", "EMC测试工程师"],
        "required_skills": ["电路基础", "测试仪器操作", "可靠性工程", "失效分析", "质量管理"],
        "development_trend": "芯片国产化和智能硬件浪潮驱动硬件测试需求增长。对测试工程师的综合能力要求提升，需要兼具硬件基础和软件调试能力。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 4,
    },
    {
        "name": "IT 技术支持",
        "position_examples": ["实施工程师", "技术支持工程师", "弱电工程师", "运维工程师"],
        "required_skills": ["网络技术", "系统集成", "数据库运维", "客户沟通", "问题排查"],
        "development_trend": "企业数字化转型持续推动IT实施和技术支持岗位需求。云服务和SaaS产品的普及使技术支持模式从现场转向远程+现场混合模式。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 5,
    },
    {
        "name": "科研与研发",
        "position_examples": ["科研人员", "研发工程师", "实验室研究员"],
        "required_skills": ["研究能力", "数据分析", "论文写作", "专业知识", "实验设计"],
        "development_trend": "国家加大科研投入，人工智能、新能源、生物医药等前沿领域科研人才紧缺。产学研融合加深，企业对研发型人才的需求持续增长。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 6,
    },
    {
        "name": "销售",
        "position_examples": ["销售工程师", "大客户销售", "渠道销售", "销售运营"],
        "required_skills": ["商务沟通", "客户关系管理", "行业知识", "谈判技巧", "市场分析"],
        "development_trend": "从关系型销售向顾问型销售转型，技术型产品和解决方案的销售需要从业者兼具行业知识和技术理解力。数字化销售工具普及，数据驱动销售决策成为趋势。",
        "excluded_personality_types": ["INTP", "INFJ", "INFP"],
        "excluded_trait_thresholds": {},
        "sort_order": 7,
    },
    {
        "name": "电话销售",
        "position_examples": ["电话销售", "电话客服", "外呼专员"],
        "required_skills": ["电话沟通", "产品知识", "客户心理", "异议处理", "CRM工具"],
        "development_trend": "AI外呼和智能客服正在改变传统电话销售模式，基础话术型岗位需求下降。电话销售向精准营销和客户运营方向转型。",
        "excluded_personality_types": ["INTP", "INFJ", "INFP", "INTJ"],
        "excluded_trait_thresholds": {},
        "sort_order": 8,
    },
    {
        "name": "网络销售",
        "position_examples": ["网络销售", "电商运营", "在线销售顾问"],
        "required_skills": ["电商平台运营", "社交媒体营销", "数据分析", "内容创作", "客户运营"],
        "development_trend": "直播电商和社交电商持续增长，网络销售模式不断创新。从单纯卖货转向品牌运营和私域流量经营。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 9,
    },
    {
        "name": "客户经理",
        "position_examples": ["客户经理", "客户成功经理", "客户关系经理"],
        "required_skills": ["客户关系管理", "解决方案设计", "项目管理", "商务谈判", "行业洞察"],
        "development_trend": "客户经理角色从'关系维护'转向'价值创造'，需要深度理解客户业务并提供增值服务。SaaS行业的客户成功经理（CSM）成为新兴热门岗位。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 10,
    },
    {
        "name": "运营",
        "position_examples": ["运营专员", "运营助理", "内容运营", "用户运营"],
        "required_skills": ["数据分析", "内容策划", "用户洞察", "活动策划", "Excel/SQL"],
        "development_trend": "运营岗位日益细分（用户运营、内容运营、活动运营、数据运营），对数据敏感度和工具使用能力要求提升。AI工具正在改变内容生产和用户触达方式。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 11,
    },
    {
        "name": "新媒体运营",
        "position_examples": ["新媒体运营", "自媒体运营", "短视频运营", "社群运营"],
        "required_skills": ["内容创作", "短视频制作", "平台规则", "用户增长", "数据分析"],
        "development_trend": "短视频和直播持续主导流量入口，AI内容生产工具改变创作效率。从流量思维向品牌思维转变，需要兼具创意策划和数据运营能力。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 12,
    },
    {
        "name": "市场营销",
        "position_examples": ["市场营销专员", "品牌推广", "市场策划", "数字营销"],
        "required_skills": ["市场分析", "品牌策略", "数字广告", "内容营销", "效果评估"],
        "development_trend": "数字营销预算占比持续提升，MarTech工具广泛应用。效果广告竞争加剧，品牌建设和内容营销回归。AI驱动的精准营销成为标配。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 13,
    },
    {
        "name": "APP推广",
        "position_examples": ["APP推广专员", "应用商店优化师", "增长运营"],
        "required_skills": ["ASO优化", "广告投放", "数据分析", "增长策略", "渠道管理"],
        "development_trend": "移动互联网增长见顶，获客成本持续上升。从粗放投放到精细化增长运营转型，ASO和数据驱动增长能力成为核心。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 14,
    },
    {
        "name": "游戏运营",
        "position_examples": ["游戏运营", "游戏推广", "游戏社区运营"],
        "required_skills": ["游戏理解", "用户运营", "活动策划", "数据分析", "社区管理"],
        "development_trend": "版号常态化后游戏行业回暖，精品化运营趋势明显。小游戏和出海成为新增长点，对运营的全球化视野和数据能力要求提升。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 15,
    },
    {
        "name": "游戏推广",
        "position_examples": ["游戏推广专员", "游戏广告投放", "游戏渠道推广"],
        "required_skills": ["广告投放", "素材创意", "渠道对接", "效果优化", "游戏行业知识"],
        "development_trend": "游戏买量成本持续走高，精细化投放和创意素材成为核心竞争力。海外市场推广需求旺盛。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 16,
    },
    {
        "name": "产品",
        "position_examples": ["产品助理", "产品专员", "产品经理"],
        "required_skills": ["需求分析", "原型设计", "用户研究", "数据分析", "项目管理"],
        "development_trend": "产品经理岗位门槛逐步提高，对技术理解和数据驱动决策能力要求提升。AI产品经理成为新兴方向，需要理解大模型能力边界和应用场景。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 17,
    },
    {
        "name": "行政管理",
        "position_examples": ["行政专员", "行政助理", "前台/总机/接待", "资料管理员", "总经理助理"],
        "required_skills": ["办公软件", "公文写作", "沟通协调", "时间管理", "档案管理"],
        "development_trend": "行政岗位向智能化和综合管理方向转型，重复性工作被数字化工具替代。对从业者的综合协调能力和信息技术应用能力要求提高。",
        "excluded_personality_types": ["ENTP", "ESTP"],
        "excluded_trait_thresholds": {},
        "sort_order": 18,
    },
    {
        "name": "项目管理",
        "position_examples": ["项目经理", "项目专员", "项目助理", "投标专员"],
        "required_skills": ["PMP/敏捷方法", "进度管理", "风险管理", "跨部门协调", "项目工具"],
        "development_trend": "敏捷项目管理方法在各行业普及，PMP等证书含金量稳定。AI项目管理工具兴起，对项目经理的数字化管理能力和敏捷思维要求提高。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 19,
    },
    {
        "name": "人力资源",
        "position_examples": ["招聘专员", "猎头顾问", "HRBP", "薪酬福利专员"],
        "required_skills": ["招聘面试", "劳动法规", "绩效管理", "沟通能力", "HR系统"],
        "development_trend": "HR数字化转型加速，AI简历筛选和智能面试工具广泛应用。HRBP角色重要性提升，需要深入理解业务。雇主品牌建设和员工体验成为竞争焦点。",
        "excluded_personality_types": ["ISTP", "INTP"],
        "excluded_trait_thresholds": {},
        "sort_order": 20,
    },
    {
        "name": "商务拓展",
        "position_examples": ["BD经理", "商务拓展", "渠道合作", "战略合作"],
        "required_skills": ["商务谈判", "行业资源", "合同管理", "商业模式分析", "人脉拓展"],
        "development_trend": "BD岗位从单纯'拉合作'转向生态构建和战略绑定，需要深度理解产业链和商业模式创新。跨界合作和生态共赢思维日益重要。",
        "excluded_personality_types": ["INFP", "ISFJ"],
        "excluded_trait_thresholds": {},
        "sort_order": 21,
    },
    {
        "name": "法律",
        "position_examples": ["律师", "律师助理", "知识产权专员", "专利代理人", "法务专员"],
        "required_skills": ["法律专业知识", "法律文书写作", "案例分析", "法考证书", "沟通谈判"],
        "development_trend": "AI法律工具（合同审查、法律检索）正在改变律师工作方式，基础法律文书工作被AI辅助替代。知识产权和数据合规领域人才需求增长显著。",
        "excluded_personality_types": ["INFP", "ISFP"],
        "excluded_trait_thresholds": {},
        "sort_order": 22,
    },
    {
        "name": "客户服务",
        "position_examples": ["客服专员", "电话客服", "在线客服", "综合客服"],
        "required_skills": ["沟通技巧", "情绪管理", "产品知识", "CRM系统", "问题解决"],
        "development_trend": "AI客服机器人处理大部分标准化问题，人工客服转向处理复杂场景和情绪化客户。客服岗位从'接电话'向'客户体验管理'升级。",
        "excluded_personality_types": ["INTJ", "ISTP"],
        "excluded_trait_thresholds": {},
        "sort_order": 23,
    },
    {
        "name": "质量管理",
        "position_examples": ["质检员", "质量工程师", "品质管理", "QA工程师"],
        "required_skills": ["质量标准体系", "检验检测", "统计分析", "质量工具", "问题追溯"],
        "development_trend": "智能制造和工业4.0推动质量管理数字化转型，AI视觉检测和大数据分析在质量预测中广泛应用。从被动检验转向主动预防和全流程质量管控。",
        "excluded_personality_types": ["ENFP", "ENTP"],
        "excluded_trait_thresholds": {},
        "sort_order": 24,
    },
    {
        "name": "管理培训生",
        "position_examples": ["管理培训生", "储备经理人", "管培生"],
        "required_skills": ["快速学习", "领导力潜质", "跨部门轮岗", "商业思维", "沟通表达"],
        "development_trend": "企业管培生项目更加重视数字化转型能力和创新思维。优秀的管培生需要展现出快速适应变化的敏捷性和数据驱动决策的思维习惯。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 25,
    },
    {
        "name": "翻译",
        "position_examples": ["英语翻译", "日语翻译", "笔译", "口译"],
        "required_skills": ["双语能力", "专业术语", "翻译工具CAT", "文化理解", "写作能力"],
        "development_trend": "AI翻译技术（神经机器翻译）对基础翻译岗位冲击明显，简单文档翻译需求大幅下降。高端翻译（法律、医学、技术文献）和口译仍有不可替代性。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 26,
    },
    {
        "name": "教育培训",
        "position_examples": ["培训师", "教务管理", "课程顾问", "教学管理"],
        "required_skills": ["教学能力", "课程设计", "学员管理", "专业知识", "表达能力"],
        "development_trend": "AI辅助教学和在线教育持续发展，对培训师的技术融合能力和课程创新能力要求提高。企业内训向个性化和数据驱动方向转型。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 27,
    },
    {
        "name": "数据分析",
        "position_examples": ["数据分析师", "统计员", "BI分析师", "数据运营"],
        "required_skills": ["SQL/Python/R", "统计学", "数据可视化", "商业分析", "Excel高级应用"],
        "development_trend": "AI大模型让数据分析门槛降低，基础取数工作被AI替代，但数据解读和商业洞察能力更加稀缺。数据分析师需要从'做报表'转向'讲故事'和'驱动决策'。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 28,
    },
    {
        "name": "咨询",
        "position_examples": ["咨询顾问", "管理咨询", "战略咨询", "IT咨询"],
        "required_skills": ["结构化思维", "PPT/演示能力", "行业分析", "沟通表达", "快速学习"],
        "development_trend": "传统管理咨询与数字化咨询融合加深，AI辅助分析和决策工具改变咨询工作方式。细分领域专家型顾问比通才型顾问更有竞争力。",
        "excluded_personality_types": ["ISFJ", "ISFP"],
        "excluded_trait_thresholds": {},
        "sort_order": 29,
    },
    {
        "name": "后勤综合",
        "position_examples": ["司机", "后勤专员", "综合管理"],
        "required_skills": ["驾驶技能", "后勤管理", "协调能力", "责任心"],
        "development_trend": "后勤岗位向综合管理和智能化调度方向发展，专业化和精细化管理是趋势。",
        "excluded_personality_types": [],
        "excluded_trait_thresholds": {},
        "sort_order": 30,
    },
]


# ============================================================
# 主函数
# ============================================================
def seed():
    """导入种子数据"""
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "positions_cleaned.csv",
    )

    if not os.path.exists(csv_path):
        print(f"[错误] 找不到数据文件: {csv_path}")
        print("请确认 positions_cleaned.csv 在 backend/ 目录下")
        return

    # 确保表已创建
    print("[1/4] 检查数据库表...")
    create_db_and_tables()
    print("  [OK] 表结构已就绪")

    with Session(engine) as session:
        # ---- 先清空子表（FK 约束：positions → directions） ----
        print("[2/4] 清空旧数据...")
        session.query(Position).delete()
        session.query(Direction).delete()

        # ---- 先读 CSV（失败则提前退出，不污染数据库） ----
        print("[3/4] 读取岗位数据...")
        df = pd.read_csv(csv_path)

        # ---- 导入 directions ----
        print("[3/4] 导入方向数据...")
        direction_map: dict[str, int] = {}  # name → id

        for d in DIRECTION_DEFINITIONS:
            obj = Direction(
                name=d["name"],
                position_examples=d["position_examples"],
                required_skills=d["required_skills"],
                development_trend=d["development_trend"],
                excluded_personality_types=d["excluded_personality_types"],
                excluded_trait_thresholds=d["excluded_trait_thresholds"],
                sort_order=d["sort_order"],
                is_active=True,
            )
            session.add(obj)
            session.flush()
            direction_map[d["name"]] = obj.id  # type: ignore[assignment]

        print(f"  [OK] 已导入 {len(direction_map)} 个方向")

        # ---- 导入 positions ----
        print("[3/4] 导入岗位数据...")
        imported = 0
        unmapped = set()
        skipped = 0

        for _, row in df.iterrows():
            title = str(row["岗位名称"]).strip()
            direction_name = JOB_TO_DIRECTION.get(title)

            if direction_name is None:
                unmapped.add(title)
                skipped += 1
                continue

            direction_id = direction_map.get(direction_name)
            if direction_id is None:
                skipped += 1
                continue

            desc = str(row.get("岗位详情_纯文本", "")).strip()
            company_desc = str(row.get("公司详情_纯文本", "")).strip()
            full_desc = f"{desc}\n\n【公司介绍】\n{company_desc}" if company_desc else desc

            obj = Position(
                title=title,
                description=full_desc,
                direction_id=direction_id,
                city=str(row.get("城市", "")),
                industry=str(row.get("所属行业", "")),
                education_requirement="本科",
                salary_range=str(row.get("薪资范围", "")),
                is_active=True,
            )
            session.add(obj)
            imported += 1

        session.commit()
        print(f"  [OK] 已导入 {imported} 条岗位记录")
        if unmapped:
            print(f"  [WARN] 未映射的岗位名 ({len(unmapped)}种): {sorted(unmapped)}")
        if skipped:
            print(f"  [WARN] 跳过 {skipped} 条（无映射或无方向ID）")

        # ---- 验证 ----
        print("[4/4] 验证...")
        from sqlmodel import select, func

        dir_count = session.exec(select(func.count()).select_from(Direction)).one()
        pos_count = session.exec(select(func.count()).select_from(Position)).one()
        print(f"  [OK] directions: {dir_count} 条")
        print(f"  [OK] positions: {pos_count} 条")
        print("\n种子数据导入完成！")


if __name__ == "__main__":
    seed()
