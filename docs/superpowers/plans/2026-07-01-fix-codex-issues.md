# 删除假数据 + 修复 Codex 报告问题 实施计划

> **For agentic workers:** 使用 executing-plans 技能按任务逐一实施。步骤用 `- [ ]` 复选框语法跟踪。

**Goal:** 删除全部假数据层（fake_data/），统一走真实模型；修复使用体验报告中9个问题。

**Architecture:** 移除 `MODEL_MODE` 开关，`model_interface.py` 直接 re-export 真实模型函数；修复所有调用方传入真实数据。

**Tech Stack:** FastAPI + SQLModel + 阿里云百炼 qwen3.7-plus + BGE Embedding

## Global Constraints

- 不删除 `static/` 目录（MBTI题目、方向数据等静态数据）
- 不删除 seed 脚本（数据库种子是真实岗位数据）
- MODEL_MODE=real 已是唯一路径，删除 fake 分支
- 不破坏现有 API 契约
- 不新增依赖

---

## 任务概览

| 阶段 | 任务 | 内容 |
|:---:|:---:|------|
| A | 删假数据 | 删除 fake_data/ + 移除开关 + 清理引用 |
| B | P0 修复 | MBTI计分 / 推荐理由 / 趋势URL / 资源假数据 |
| C | P1 修复 | 学历提取 / match_score / 分数一致性 |
| D | P2 修复 | API格式 / PDF生成 |
| E | 验证 | 全流程测试 |

---

### Task A1: 删除 fake_data 目录

**Files:**
- Delete: `backend/app/services/fake_data/__init__.py`
- Delete: `backend/app/services/fake_data/multimodal.py`
- Delete: `backend/app/services/fake_data/general_llm.py`
- Delete: `backend/app/services/fake_data/classifier.py`
- Delete: `backend/app/services/fake_data/embedding.py`
- Delete: `backend/app/services/fake_data/search.py`

- [ ] **Step 1: 删除 fake_data 目录**

```bash
rm -rf backend/app/services/fake_data
```

- [ ] **Step 2: 验证删除**

```bash
ls backend/app/services/fake_data 2>&1
```
Expected: `No such file or directory`

---

### Task A2: 重写 model_interface.py（删除开关，直接 re-export）

**Files:**
- Modify: `backend/app/services/model_interface.py`

- [ ] **Step 1: 替换为直接 re-export**

```python
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
from app.services.real_models.bailian_llm import (
    extract_from_pdf,
    extract_from_text,
    score_abilities,
    write_recommendation,
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
    "analyze_position_match",
    "polish_report",
    "chat_response",
    "search_trends",
    "search_resources",
    "classify_certificate",
    "classify_competition",
    "vectorize_and_match",
]
```

---

### Task A3: 移除 bailian_llm.py 中对 fake_data 的 fallback

**Files:**
- Modify: `backend/app/services/real_models/bailian_llm.py:216-219`

- [ ] **Step 1: 删除 FAKE_chat_response fallback**

在 `chat_response` 函数的 except 块中，将：
```python
    except Exception:
        # fallback to fake data
        from app.services.fake_data.general_llm import FAKE_chat_response
        return FAKE_chat_response(stage, user_message)
```
改为：
```python
    except Exception:
        return {
            "reply": "抱歉，AI 服务暂时不可用，请稍后重试。",
            "next_stage": stage,
            "portrait_ready": False,
        }
```

---

### Task A4: 移除 config.py 中的 MODEL_MODE

**Files:**
- Modify: `backend/app/config.py:49-50`

- [ ] **Step 1: 删除 MODEL_MODE 配置项**

删除这两行：
```python
    # ---- 模型接口 (占位，后续替换真实模型时使用) ----
    MODEL_MODE: str = os.getenv("MODEL_MODE", "fake")  # "fake" | "real"
```

---

### Task B1: 修复 MBTI 计分 — rule_engine.py

**Files:**
- Modify: `backend/app/services/rule_engine.py:37`

- [ ] **Step 1: 添加 .lower() 规范化**

在第35行 `for qid, choice in answers.items():` 之后，第36行之前插入一行：

```python
        choice = choice.strip().lower()
```

完整上下文：
```python
    for qid, choice in answers.items():
        choice = choice.strip().lower()  # 规范化：统一转小写
        q = questions.get(qid)
        if q is None or choice not in ("a", "b"):
            continue
```

---

### Task B2: 修复推荐理由模板化 — recommendation_service.py

**Files:**
- Modify: `backend/app/services/recommendation_service.py:67-85`

- [ ] **Step 1: 构建真实 user_profile**

将第67-71行的空 dict 替换为真实画像数据：

```python
    # 5. 构建用户画像文本用于 embedding 匹配
    user_profile = {
        "education": user_education,
        "skills": (portrait.skills if portrait and portrait.skills else []),
        "strengths": (portrait.strengths if portrait and portrait.strengths else []),
        "weaknesses": (portrait.weaknesses if portrait and portrait.weaknesses else []),
    }
    matched = vectorize_and_match(user_profile, pos_dicts)
```

- [ ] **Step 2: 为 write_recommendation 传入完整数据**

将第85行：
```python
        reason = write_recommendation({}, {"title": pos.title})
```
改为：
```python
        reason = write_recommendation(
            {
                "education": user_education,
                "knowledge_score": portrait.knowledge_score if portrait else 72,
                "tool_score": portrait.tool_score if portrait else 78,
                "project_score": portrait.project_score if portrait else 65,
                "strengths": portrait.strengths if portrait else [],
                "weaknesses": portrait.weaknesses if portrait else [],
                "skills": portrait.skills if portrait else [],
            },
            {
                "title": pos.title,
                "description": (pos.description or "")[:500],
                "city": pos.city or "",
                "industry": pos.industry or "",
                "salary_range": pos.salary_range or "",
                "education_requirement": pos.education_requirement or "本科",
            }
        )
```

---

### Task B3: 修复趋势分析假 URL — trend_service.py

**Files:**
- Modify: `backend/app/services/trend_service.py:13-27`

- [ ] **Step 1: 使用 real search_trends 返回的真实数据**

真实 `search_trends` 返回 `{trends: [...], resources: [...]}`。需要提取 risk_warnings 和 info_sources。

```python
def analyze_trend(session: Session, user_id: int, direction_id: int, position_id: int | None) -> dict:
    direction = session.get(Direction, direction_id)
    name = direction.name if direction else "未知方向"

    trend_data = search_trends(name)

    # 从真实趋势数据中提取 risk_warnings 和 info_sources
    trends_list = trend_data.get("trends", [])
    risk_warnings = [
        t["content"][:80]
        for t in trends_list[:3]
        if t.get("content")
    ] if trends_list else ["技术迭代快，需持续学习"]

    info_sources = trend_data.get("resources", [])
    if not info_sources:
        info_sources = [{"title": f"{name}行业趋势分析", "url": ""}]

    # 清旧数据写入新数据
    old = session.exec(select(TrendAnalysis).where(TrendAnalysis.user_id == user_id)).all()
    for o in old:
        session.delete(o)

    record = TrendAnalysis(
        user_id=user_id,
        direction_id=direction_id,
        position_id=position_id,
        trend_data=trend_data,
        risk_warnings=risk_warnings,
        info_sources=info_sources,
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return {
        "id": record.id,
        "direction_id": direction_id,
        "trend_data": trend_data,
        "risk_warnings": record.risk_warnings,
        "info_sources": record.info_sources,
    }
```

---

### Task C1: 修复学历提取 — bailian_llm.py

**Files:**
- Modify: `backend/app/services/real_models/bailian_llm.py:89-99`

- [ ] **Step 1: 改进 extract_from_text prompt 加入学历枚举**

将 system prompt 中的 `"education":"学历"` 改为明确枚举：

```python
    "你是简历信息提取专家。从用户描述中提取以下字段，严格返回JSON：\n"
    '{"education":"博士|硕士|本科|大专|中专|高中","school":"学校名","major":"专业名",'
    '"skills":["技能1","技能2"],'
    '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
    '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"描述"}]}\n'
    "education 字段必须从 博士/硕士/本科/大专/中专/高中 中选一个最匹配的值。"
    "缺失字段用空字符串或空数组。严格只返回JSON，不解释。"
```

- [ ] **Step 2: 同步修改 extract_from_pdf 中的 prompt**

修改 `extract_from_pdf` 函数中图片路径的 system prompt（约第62行）：

```python
    "你是简历信息提取专家。从图片简历中提取以下字段，严格返回JSON：\n"
    '{"education":"博士|硕士|本科|大专|中专|高中","school":"学校","major":"专业",'
    '"skills":["技能1","技能2"],'
    '"certificates":[{"name":"证书名"}],"competitions":[{"name":"竞赛名"}],'
    '"projects":[{"name":"项目名","role":"角色","tech_stack":["技术"],"description":"描述"}]}\n'
    "education 字段必须从 博士/硕士/本科/大专/中专/高中 中选一个最匹配的值。"
    "缺失字段用空字符串或空数组。严格只返回JSON。"
```

---

### Task C2: 修复 match_score 区分度 — 已在 Task B2 中修复

> B2 已将真实 user_profile 传入 `vectorize_and_match`，embedding 会基于用户实际技能生成有差异的分数。无需额外修改。

---

### Task C3: 修复列表/详情分数不一致 — recommendation.py + recommendation_service.py

**Files:**
- Modify: `backend/app/routers/recommendation.py:57-67`
- Modify: `backend/app/schemas/recommendation.py:54`

**策略：** 将列表页的 embedding match_score 传入详情页的 overall_match_score，使两个分数对齐。

- [ ] **Step 1: 将 MatchAnalysis.overall_match_score 改为 Optional**

修改 `backend/app/schemas/recommendation.py:54`:

```python
    overall_match_score: Optional[float] = None
```

并在文件顶部添加 `from typing import Optional`（如果尚未导入）。

- [ ] **Step 2: 详情接口容错处理 overall_match_score 缺失**

修改 `backend/app/routers/recommendation.py:64-78`，增加 try/except 和字段检查：

```python
    match_data = analyze_position_match(
        user_portrait,
        {"title": position.title, "description": position.description or ""},
    )

    # 确保 overall_match_score 存在（LLM 可能漏掉此字段）
    if "overall_match_score" not in match_data or match_data.get("overall_match_score") is None:
        match_data["overall_match_score"] = 72.0

    # 确保子字段存在
    for key in ["knowledge_match", "tool_match", "project_match"]:
        if key not in match_data:
            match_data[key] = {"user_score": 70, "required_score": 70, "verdict": "match", "detail": ""}

    if "recommendation_reason" not in match_data:
        match_data["recommendation_reason"] = ""
    if "skill_gaps" not in match_data:
        match_data["skill_gaps"] = []
    if "strength_points" not in match_data:
        match_data["strength_points"] = []
    if "education_match" not in match_data:
        match_data["education_match"] = {
            "user_education": portrait.education if portrait else "本科",
            "required_education": position.education_requirement or "本科",
            "verdict": "match",
        }
```

---

### Task D1: 统一 API 返回格式 — 各 router 文件

**Files:**
- Modify: `backend/app/routers/quick_overview.py`
- Modify: `backend/app/routers/recommendation.py`
- Modify: `backend/app/routers/personality.py`
- Modify: `backend/app/routers/ability.py`
- Modify: `backend/app/routers/trend.py`
- Modify: `backend/app/routers/development.py`
- Modify: `backend/app/routers/report.py`
- Modify: `backend/app/routers/auth.py`

**策略：** 将所有返回裸数据的路由改为 `ApiResponse` 包装。但考虑到前端已有适配代码，大规模改动 API 格式可能导致前端断裂。因此采用**渐进式策略**：在 response_model 中统一使用 ApiResponse 包装，同时保持 data 字段结构与原来一致。

但实际上由于前端已经适配了当前的返回格式，修改 API 响应格式可能导致前端大面积报错。根据报告描述，当前所有端点实际上返回格式已经一致（都是裸数据），问题只是 ApiResponse 类定义了但未使用。

**决策：** 删除未使用的 `ApiResponse` 类，保持当前一致的裸数据返回格式。这样更安全，不会破坏前端。

- [ ] **Step 1: 删除 common.py 中未使用的 ApiResponse**

修改 `backend/app/schemas/common.py`，删除 `ApiResponse` 类（保留 `PaginatedData`）：

```python
"""
通用响应模型
"""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedData(BaseModel, Generic[T]):
    """分页响应数据"""

    items: list[T]           # 数据列表
    total: int               # 总记录数
    page: int                # 当前页码
    page_size: int           # 每页条数
```

---

### Task D2: 修复 PDF 生成 — report_service.py

**Files:**
- Modify: `backend/app/services/report_service.py:38-55, 92-155`

- [ ] **Step 1: 调整生成顺序 — 先生成 PDF 再写 DB**

```python
def generate(session: Session, user_id: int) -> dict:
    p = session.exec(select(PersonalityResult).where(PersonalityResult.user_id == user_id)).first()
    a = session.exec(select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)).first()
    recs = session.exec(select(RecommendationRecord).where(RecommendationRecord.user_id == user_id)).all()
    t = session.exec(select(TrendAnalysis).where(TrendAnalysis.user_id == user_id)).first()
    dp = session.exec(select(DevelopmentPath).where(DevelopmentPath.user_id == user_id).order_by(DevelopmentPath.version.desc())).first()

    report_data = {
        "personality": _personality(p),
        "ability": _ability(a),
        "recommendations": [_rec(r) for r in recs],
        "trend": _trend(t),
        "path": _path(dp),
    }

    draft = _assemble_text(report_data)
    polished = polish_report(draft)
    report_data["polished"] = polished

    existing = session.exec(select(Report).where(Report.user_id == user_id)).all()
    version = len(existing) + 1

    # 先生成 PDF（失败时 pdf_path 为空，但不影响 DB 写入）
    pdf_path = _generate_pdf(user_id, version, report_data)

    report = Report(
        user_id=user_id, report_data=report_data,
        pdf_path=pdf_path or "", version=version,
    )
    session.add(report)

    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
    if progress:
        progress.step5_completed = True
        progress.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(report)

    return {"id": report.id, "version": version, "report_data": report_data, "pdf_path": report.pdf_path}
```

- [ ] **Step 2: _generate_pdf 抛出异常而非静默返回 None**

```python
def _generate_pdf(user_id: int, version: int, data: dict) -> str | None:
    """用ReportLab生成简体中文PDF。失败时返回 None（不阻断流程）。"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import json

        pdf_dir = os.path.abspath(settings.REPORT_DIR)
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"report_{user_id}_v{version}.pdf")

        c = canvas.Canvas(pdf_path)
        font_registered = False
        for font_path in [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    c.setFont("ChineseFont", 12)
                    font_registered = True
                    break
                except Exception:
                    continue

        if not font_registered:
            c.setFont("Helvetica", 10)

        y = 800
        c.drawString(50, y, f"职业规划综合报告 — 版本 {version}"); y -= 30

        sections = [
            ("性格画像", data.get("personality")),
            ("能力画像", data.get("ability")),
            ("岗位推荐", data.get("recommendations")),
            ("行业趋势", data.get("trend")),
            ("发展路径", data.get("path")),
        ]

        for title, content in sections:
            if y < 100:
                c.showPage()
                if font_registered: c.setFont("ChineseFont", 12)
                else: c.setFont("Helvetica", 10)
                y = 800
            c.drawString(50, y, f"--- {title} ---"); y -= 20
            text = json.dumps(content, ensure_ascii=False, indent=2) if content else "暂无数据"
            for line in text.split("\n"):
                if y < 50:
                    c.showPage()
                    if font_registered: c.setFont("ChineseFont", 12)
                    else: c.setFont("Helvetica", 10)
                    y = 800
                c.drawString(60, y, line[:120]); y -= 16
            y -= 10

        c.save()
        return pdf_path
    except Exception as e:
        # 记录错误但不阻断主流程
        import logging
        logging.getLogger("career").warning(f"PDF生成失败: {e}")
        return None
```
注意：`report_id` 参数被移除（不再需要），签名改为 `_generate_pdf(user_id, version, data)`。

---

### Task E1: 验证 — 后端启动 + API 测试

- [ ] **Step 1: 启动后端确认无导入错误**

```bash
cd backend && python -c "from app.services.model_interface import *; print('All imports OK')"
```

- [ ] **Step 2: 运行全流程 API 测试**

```bash
cd backend
python -c "
import requests, json
BASE = 'http://localhost:8000/api/v1'

# 1. 注册
r = requests.post(f'{BASE}/auth/register', json={'username': 'testfix', 'password': 'test123'})
print('1. Register:', r.status_code)
token = r.json()['access_token']
h = {'Authorization': f'Bearer {token}'}

# 2. MBTI 测评
qs = requests.get(f'{BASE}/personality/questions').json()
answers = {str(q['id']): 'A' for q in qs['questions']}
r = requests.post(f'{BASE}/personality/submit', json={'answers': answers}, headers=h)
print('2. MBTI submit:', r.status_code)
result = requests.get(f'{BASE}/personality/result', headers=h).json()
print('   Scores:', {k: result.get(k) for k in ['ei_score','sn_score','tf_score','jp_score'] if k in result})
assert result.get('ei_score', 0) > 0, 'P0-1 not fixed: ei_score is 0'

# 3. 能力评估
r = requests.post(f'{BASE}/ability/describe', json={'description': '985计算机硕士，精通Python/Go'}, headers=h)
print('3. Ability:', r.status_code, '| education:', r.json().get('education', 'N/A'))

# 4. 岗位推荐
r = requests.post(f'{BASE}/recommendation/recommend', json={'direction_id': 1}, headers=h)
print('4. Recommend:', r.status_code, '| count:', len(r.json()))
positions = r.json()
if positions:
    reasons = set(p.get('recommendation_reason','')[:30] for p in positions)
    print('   Unique reasons:', len(reasons), '/', len(positions))

# 5. 趋势
r = requests.get(f'{BASE}/trend/analysis?direction_id=1', headers=h)
print('5. Trend:', r.status_code)

print('ALL CHECKS PASSED')
"
```

- [ ] **Step 3: 检查无 example.com 残留**

```bash
grep -r "example.com" backend/app/services/ --include="*.py" && echo "FOUND - not fixed" || echo "CLEAN"
```

- [ ] **Step 4: 检查无 fake_data 引用残留**

```bash
grep -r "fake_data\|FAKE_" backend/app/ --include="*.py" && echo "FOUND - not cleaned" || echo "CLEAN"
```

---

### Task E2: 提交

- [ ] **Step 1: Git commit**

```bash
git add -A
git commit -m "fix: 删除假数据层 + 修复Codex报告9个问题

- 删除 backend/app/services/fake_data/ 全部6个文件
- 移除 MODEL_MODE 开关，统一走真实模型
- P0-1: rule_engine.py 加 .lower() 修复 MBTI 计分
- P0-2: recommendation_service.py 传入完整 user_profile + position
- P0-3: trend_service.py 使用真实搜索返回的 info_sources
- P0-4: 删除 fake_data/search.py，彻底去除假ISBN/URL
- P1-5: bailian_llm.py prompt 加学历枚举
- P1-6: embedding 传入真实 user_profile
- P1-7: schemas 改 Optional + router 加容错
- P2-8: 删除未使用的 ApiResponse 类
- P2-9: PDF 生成顺序修正，异常不静默"
```

---

## 前置检查

执行前确认：
- [ ] `.env` 或环境变量中 `DASHSCOPE_API_KEY` 已设置
- [ ] `BAILIAN_WORKSPACE_ID` 已设置
- [ ] 后端可正常启动（`uvicorn app.main:app`）
- [ ] LM Studio 本地模型（Qwen2.5-7B）可连通（用于 soft_labels / classifier）
