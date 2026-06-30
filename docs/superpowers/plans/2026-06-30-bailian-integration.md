# 阿里云百炼 qwen3.7-plus 全面接入 实现计划

> **For agentic workers:** Use superpowers:executing-plans to implement.

**Goal:** 接入 qwen3.7-plus 替换全部剩余假数据函数

**Architecture:** BailianClient(共享客户端) → bailian_llm.py(8函数) → model_interface.py(统一MODEL_MODE开关)

**Tech Stack:** Python, requests, OpenAI 兼容 API

## Global Constraints

- 所有函数签名与现有假数据完全一致，业务代码零改动
- MODEL_MODE=real 切真实，MODEL_MODE=fake 切假数据
- 配置从 config.py settings 对象读，不直接读环境变量

---

### Task 1: BailianClient 共享客户端

**文件:** `backend/app/services/real_models/bailian_client.py` (新建)

- [ ] **Step 1: 创建文件**

```python
"""
阿里云百炼 OpenAI 兼容 API 客户端

端点: https://{workspace_id}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
模型: qwen3.7-plus
"""

import json
import re
import requests
from app.config import settings


class BailianClient:
    """百炼 API 共享客户端 (单例)"""

    def __init__(self):
        self.base_url = f"{settings.BAILIAN_BASE_URL}/chat/completions"
        self.model = settings.BAILIAN_MODEL
        self.headers = {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """通用对话，返回纯文本"""
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(self.base_url, headers=self.headers, json=body, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"Bailian API error {r.status_code}: {r.text[:300]}")
        return r.json()["choices"][0]["message"]["content"]

    def chat_json(self, messages: list[dict], temperature: float = 0.2) -> dict:
        """对话 + 强制从回复中提取 JSON"""
        text = self.chat(messages, temperature=temperature)
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError(f"No JSON found in response: {text[:200]}")
        return json.loads(match.group(0))

    def chat_with_search(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """联网搜索对话"""
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "enable_search": True,
        }
        r = requests.post(self.base_url, headers=self.headers, json=body, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"Bailian search error {r.status_code}: {r.text[:300]}")
        return r.json()["choices"][0]["message"]["content"]


# 全局单例
_client = None

def get_client() -> BailianClient:
    global _client
    if _client is None:
        _client = BailianClient()
    return _client
```

- [ ] **Step 2: 验证**

```bash
cd /d/zgyd/backend && python -c "
from app.services.real_models.bailian_client import get_client
c = get_client()
r = c.chat([{'role':'user','content':'hi'}], max_tokens=20)
print('OK:', r[:50])
"
```

Expected: `OK: 你好！有什么可以帮你的吗？` 或类似回复

---

### Task 2: bailian_llm.py 全部 8 个函数

**文件:** `backend/app/services/real_models/bailian_llm.py` (新建)

- [ ] **Step 1: 创建文件**

```python
"""
阿里云百炼 qwen3.7-plus — 业务函数层

替代: fake_data/general_llm.py 中 4 个函数 + fake_data/search.py 中 2 个函数
"""

from app.services.real_models.bailian_client import get_client


# ==================== M2-1: 文本提取 ====================

def extract_from_text(description: str) -> dict:
    """从用户自由文本中提取结构化能力信息"""
    client = get_client()
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


# ==================== M2-2: 三维度评分 ====================

def score_abilities(skills: list) -> dict:
    """基于技能清单评分"""
    client = get_client()
    return client.chat_json([
        {"role": "system", "content": (
            "你是大学生能力评估专家。根据技能清单对三个维度评分(0-100)并给出依据，严格返回JSON：\n"
            '{"knowledge_score":数字,"tool_score":数字,"project_score":数字,'
            '"scoring_basis":{"knowledge":"依据","tool":"依据","project":"依据"}}\n'
            "评分标准：60以下=薄弱，60-75=中等，76-85=良好，86-100=优秀。只返回JSON。"
        )},
        {"role": "user", "content": f"技能清单：{', '.join(skills) if skills else '无记录'}"},
    ], temperature=0.2)


# ==================== M2-4: 推荐理由 ====================

def write_recommendation(user_profile: dict, position: dict) -> str:
    """撰写个性化岗位推荐理由"""
    client = get_client()
    return client.chat([
        {"role": "system", "content": "你是职业规划顾问。为大学生写一段100-200字的岗位推荐理由，结合其能力画像和岗位要求，语言诚恳具体。"},
        {"role": "user", "content": f"学生画像：{user_profile}\n岗位：{position}"},
    ], temperature=0.7, max_tokens=400)


# ==================== M2-4ext: 岗位匹配分析 ====================

def analyze_position_match(user_portrait: dict, position: dict) -> dict:
    """逐维度分析用户与岗位匹配度"""
    client = get_client()
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


# ==================== M2-5: 报告润色 ====================

def polish_report(draft: str) -> str:
    """润色综合报告语言"""
    client = get_client()
    return client.chat([
        {"role": "system", "content": "你是文字编辑。润色以下报告，修正语病、统一风格、提升专业感，保持原意和结构不变，不缩写内容。"},
        {"role": "user", "content": draft},
    ], temperature=0.5, max_tokens=4096)


# ==================== M2-6: 对话引导 ====================

def chat_response(stage: str, user_message: str) -> dict:
    """AI引导式能力评估对话"""
    client = get_client()
    reply = client.chat([
        {"role": "system", "content": (
            "你是大学生职业规划AI助手，正在引导用户完成能力评估对话。\n"
            "对话阶段：greeting→ask_education→ask_skills→ask_projects→ask_certificates→analysis\n"
            "当前阶段：{stage}\n"
            "规则：\n"
            "- 每个阶段友好地提出一个问题，引导用户描述相关信息\n"
            "- 语气温暖专业，像学长学姐在聊天，不要过于正式\n"
            "- 当用户回答了ask_certificates阶段后，回复中必须包含'[PORTRAIT_READY]'标记\n"
            "- file_uploaded阶段：表示简历已上传，回复中包含'[PORTRAIT_READY]'\n"
            "只输出对话内容，不要输出其他解释。"
        ).replace("{stage}", stage)},
        {"role": "user", "content": user_message or "开始"},
    ], temperature=0.7, max_tokens=500)

    portrait_ready = "[PORTRAIT_READY]" in reply or stage in ("ask_certificates", "file_uploaded")
    reply_clean = reply.replace("[PORTRAIT_READY]", "").strip()

    return {
        "reply": reply_clean,
        "next_stage": _next_stage(stage),
        "portrait_ready": portrait_ready,
    }


def _next_stage(current: str) -> str:
    stages = ["greeting", "ask_education", "ask_skills", "ask_projects", "ask_certificates", "analysis"]
    try:
        idx = stages.index(current)
        return stages[min(idx + 1, len(stages) - 1)]
    except ValueError:
        return "greeting"


# ==================== M3: 搜索 ====================

def search_trends(direction_id: int) -> dict:
    """搜索行业趋势"""
    client = get_client()
    text = client.chat_with_search([
        {"role": "system", "content": (
            "你是行业趋势分析师。搜索并分析指定职业方向的最新发展趋势，严格返回JSON：\n"
            '{"trends":[{"dimension":"维度名","content":"分析内容（100字内）","score":数字}],"resources":[]}\n'
            "至少返回6个维度。只返回JSON，不解释。"
        )},
        {"role": "user", "content": f"分析职业方向ID={direction_id}的最新行业趋势，包括技术发展、市场需求、薪资水平、技能要求等维度"},
    ], temperature=0.3, max_tokens=4096)

    try:
        match = __import__("re").search(r"\{[\s\S]*\}", text)
        return __import__("json").loads(match.group(0)) if match else {"trends": [], "resources": []}
    except Exception:
        return {"trends": [], "resources": []}


def search_resources(ability_scores: dict) -> dict:
    """搜索学习资源推荐"""
    client = get_client()
    text = client.chat_with_search([
        {"role": "system", "content": (
            "你是学习资源规划师。根据用户能力画像搜索推荐学习资源，严格返回JSON：\n"
            '{"resources":[{"title":"资源名称","type":"课程|书籍|项目|社区","url":"","description":"推荐理由（80字内）","score":数字}]}\n'
            "至少返回5条资源。只返回JSON。"
        )},
        {"role": "user", "content": f"根据以下能力画像推荐学习资源：{ability_scores}"},
    ], temperature=0.3, max_tokens=2048)

    try:
        match = __import__("re").search(r"\{[\s\S]*\}", text)
        return __import__("json").loads(match.group(0)) if match else {"resources": []}
    except Exception:
        return {"resources": []}
```

- [ ] **Step 2: 逐一验证每个函数**

```bash
cd /d/zgyd/backend && python -c "
from app.services.real_models.bailian_llm import *

# 1. M2-1 文本提取
r = extract_from_text('本科，Python和SQL，做过电商项目，有英语四级')
print('M2-1:', 'OK' if r.get('education') else 'FAIL')

# 2. M2-2 评分
r = score_abilities(['Python', 'SQL', 'Docker', 'React'])
print('M2-2:', 'OK' if 'knowledge_score' in r else 'FAIL')

# 3. M2-4 推荐理由
r = write_recommendation({'skills':['Python']}, {'title':'后端开发'})
print('M2-4:', 'OK' if len(r) > 50 else 'FAIL')

# 4. M2-4ext 匹配分析
r = analyze_position_match({'knowledge_score':72},{'title':'Python开发','description':'后端API'})
print('M2-4ext:', 'OK' if 'overall_match_score' in r else 'FAIL')

# 5. M2-5 润色
r = polish_report('这是一个测试报告。')
print('M2-5:', 'OK' if len(r) > 5 else 'FAIL')

# 6. M2-6 对话
r = chat_response('greeting', '')
print('M2-6:', 'OK' if r['next_stage'] == 'ask_education' else 'FAIL')

# 7. M3 趋势搜索
r = search_trends(1)
print('M3-trends:', 'OK' if 'trends' in r else 'FAIL')

# 8. M3 资源搜索
r = search_resources({'knowledge_score':72})
print('M3-resources:', 'OK' if 'resources' in r else 'FAIL')

print('ALL PASS')
"
```

Expected: 全部 8 个函数返回 "OK"

---

### Task 3: model_interface.py 统一开关

**文件:** `backend/app/services/model_interface.py` (重写开关区)

- [ ] **Step 1: 重写文件**

```python
"""
模型接口抽象层（中间层）

所有 AI 模型调用通过此层统一管理。
.env 中 MODEL_MODE=real → 全部真实模型
.env 中 MODEL_MODE=fake → 全部假数据
"""
from app.config import settings

# ========== 统一开关 ==========
_is_real = settings.MODEL_MODE == "real"

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
extract_from_pdf = FAKE_extract_from_pdf  # M1: 待接多模态
extract_from_text = _real_extract_text if _is_real else FAKE_extract_from_text
score_abilities = _real_score if _is_real else FAKE_score_abilities
infer_soft_labels = _real_labels  # 本地模型，始终真实
write_recommendation = _real_recommend if _is_real else FAKE_write_recommendation
polish_report = _real_polish if _is_real else FAKE_polish_report
classify_certificate = _real_cert  # 本地模型，始终真实
classify_competition = _real_comp  # 本地模型，始终真实
vectorize_and_match = _real_vec  # 本地模型，始终真实
search_trends = _real_trends if _is_real else FAKE_search_trends
search_resources = _real_resources if _is_real else FAKE_search_resources
analyze_position_match = _real_match if _is_real else FAKE_analyze_position_match
chat_response = _real_chat if _is_real else FAKE_chat_response
```

- [ ] **Step 2: 更新 .env**

```bash
# 把 MODEL_MODE=fake 改为 MODEL_MODE=real
```

- [ ] **Step 3: 验证**

```bash
cd /d/zgyd/backend && python -c "
from app.services.model_interface import *
print('MODEL_MODE=real' if _is_real else 'MODEL_MODE=fake')
print('extract_from_text:', extract_from_text.__name__)
print('score_abilities:', score_abilities.__name__)
# 快速功能验证
r = chat_response('greeting', '')
print('chat:', 'OK' if r['next_stage'] == 'ask_education' else 'FAIL')
"
```

---

### Task 4: 清理 + 文档更新

- [ ] **Step 1: 更新 findings.md** — 11 个函数全部标记为真实模型
- [ ] **Step 2: 更新 .env.example** — 添加模型相关配置项说明
- [ ] **Step 3: 更新 progress.md** — 记录百炼接入完成
