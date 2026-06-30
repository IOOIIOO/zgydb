# 岗位选择+详情双栏交互重设计 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改造第4步（方向选择→岗位推荐），将页面改为左右双栏布局：左侧简要岗位列表，右侧岗位详情+匹配分析。深度规划改为基于具体岗位。

**Architecture:** 前端 DirectionSelect 页面重构为"选方向→双栏展示"，右侧调用新增的岗位详情接口获取匹配分析。后端新增 `GET /recommendation/positions/{id}/detail` 接口，新增 `FAKE_analyze_position_match` 假数据函数。Planning 页面改为接收 position_id。

**Tech Stack:** React + TypeScript + Tailwind + Framer Motion, FastAPI + SQLModel

## Global Constraints

- **假数据铁律**: 所有假数据函数以 FAKE_ 开头，放在 `backend/app/services/fake_data/` 目录，含完整注释（功能+TODO+预期模型+调用位置）
- 暗色玻璃态统一风格，参考 HeroGeometric
- PC 1920×1080，不配移动端
- 模型调用必须通过中间层 `model_interface.py`
- 所有新 API 返回 200，错误用 HTTPException

---

## 文件结构

| 操作 | 文件 | 职责 |
|:---|------|------|
| 修改 | `backend/app/services/fake_data/general_llm.py` | 新增 FAKE_analyze_position_match |
| 修改 | `backend/app/services/model_interface.py` | 导出新函数 |
| 修改 | `backend/app/routers/recommendation.py` | 新增岗位详情接口 |
| 修改 | `backend/app/schemas/recommendation.py` | 新增响应模型 |
| 修改 | `frontend/src/types/position.ts` | 新增类型定义 |
| 新增 | `frontend/src/api/positions.ts` | 新增岗位详情 API 调用 |
| 重写 | `frontend/src/pages/dashboard/DirectionSelect.tsx` | 双栏布局重构 |
| 修改 | `frontend/src/pages/dashboard/Planning.tsx` | 基于岗位而非方向 |
| 修改 | `frontend/src/api/development.ts` | position_id 改为必传 |
| 修改 | `frontend/src/api/trends.ts` | position_id 改为必传 |

---

### Task 1: 新增假数据函数 FAKE_analyze_position_match

**Files:**
- Modify: `backend/app/services/fake_data/general_llm.py`

**Interfaces:**
- Consumes: (无依赖)
- Produces: `FAKE_analyze_position_match(user_portrait: dict, position: dict) -> dict`

- [ ] **Step 1: 在 general_llm.py 末尾添加假数据函数**

在文件末尾（`FAKE_polish_report` 之后）添加：

```python
def FAKE_analyze_position_match(user_portrait: dict, position: dict) -> dict:
    """
    M2-4扩展: 分析用户能力画像与单个岗位的详细匹配度。

    功能描述: 基于用户3硬维度评分（知识/工具/项目）与岗位要求进行逐维度对比，给出差距分析和匹配理由。
    TODO: 替换为真实通用大模型（如 GPT-4 / DeepSeek），传入用户完整画像和岗位描述，让模型生成逐维度分析和匹配理由。
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
```

### Task 2: 导出新假数据函数

**Files:**
- Modify: `backend/app/services/model_interface.py`

**Interfaces:**
- Consumes: `FAKE_analyze_position_match` from Task 1
- Produces: `analyze_position_match = FAKE_analyze_position_match`

- [ ] **Step 1: 在 model_interface.py 添加导入和导出**

在 `from app.services.fake_data.general_llm import (` 的导入块中添加 `FAKE_analyze_position_match`：

```python
from app.services.fake_data.general_llm import (
    FAKE_extract_from_text,
    FAKE_score_abilities,
    FAKE_infer_soft_labels,
    FAKE_write_recommendation,
    FAKE_polish_report,
    FAKE_analyze_position_match,
)
```

在文件末尾添加导出别名：

```python
analyze_position_match = FAKE_analyze_position_match
```

### Task 3: 新增岗位详情 API 响应模型

**Files:**
- Modify: `backend/app/schemas/recommendation.py`

**Interfaces:**
- Consumes: (无依赖)
- Produces: `PositionDetailResponse`

- [ ] **Step 1: 在 recommendation.py schema 文件末尾添加响应模型**

```python
class DimensionMatch(BaseModel):
    """单维度匹配分析"""
    user_score: int
    required_score: int
    verdict: str  # "match" | "partial" | "mismatch"
    detail: str


class SkillGap(BaseModel):
    """技能差距"""
    skill: str
    importance: str  # "重要" | "加分" | "可选"
    suggestion: str


class StrengthPoint(BaseModel):
    """优势点"""
    skill: str
    level: str


class EducationMatch(BaseModel):
    """学历匹配"""
    user_education: str
    required_education: str
    verdict: str


class MatchAnalysis(BaseModel):
    """完整匹配分析"""
    knowledge_match: DimensionMatch
    tool_match: DimensionMatch
    project_match: DimensionMatch
    overall_match_score: float
    recommendation_reason: str
    skill_gaps: list[SkillGap]
    strength_points: list[StrengthPoint]
    education_match: EducationMatch


class PositionDetailResponse(BaseModel):
    """岗位详情 + 匹配分析 响应"""
    id: int
    title: str
    description: str
    city: str
    industry: str
    salary_range: str
    education_requirement: str
    match_analysis: MatchAnalysis
```

### Task 4: 新增岗位详情 API 接口

**Files:**
- Modify: `backend/app/routers/recommendation.py`

**Interfaces:**
- Consumes: `PositionDetailResponse`, `MatchAnalysis` (schemas from Task 3), `analyze_position_match` (from Task 2), `Position` model, `AbilityPortrait` model
- Produces: `GET /recommendation/positions/{position_id}/detail -> PositionDetailResponse`

- [ ] **Step 1: 在 recommendation.py router 中添加新接口**

在文件末尾（最后一个路由之后）添加：

```python
from app.schemas.recommendation import (
    RecommendRequest,
    PositionItem,
    PositionDetailResponse,
    MatchAnalysis,
    DimensionMatch,
    SkillGap,
    StrengthPoint,
    EducationMatch,
)
from app.services.model_interface import analyze_position_match
from app.models.position import Position
from app.models.ability import AbilityPortrait


@router.get("/positions/{position_id}/detail", response_model=PositionDetailResponse)
def get_position_detail(
    position_id: int,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """获取单个岗位的详细信息及用户匹配分析"""
    # 1. 查岗位
    position = session.get(Position, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 2. 查用户能力画像
    portrait = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == current_user.id)
    ).first()

    # 3. 构造用户画像字典传给假数据函数
    user_portrait = {
        "knowledge_score": portrait.knowledge_score if portrait else 72,
        "tool_score": portrait.tool_score if portrait else 78,
        "project_score": portrait.project_score if portrait else 65,
        "education": portrait.education if portrait else "本科",
    }

    # 4. 调用假数据匹配分析
    match_data = analyze_position_match(
        user_portrait,
        {"title": position.title, "description": position.description or ""},
    )

    # 5. 组装响应
    return {
        "id": position.id,
        "title": position.title,
        "description": position.description or "",
        "city": position.city or "",
        "industry": position.industry or "",
        "salary_range": position.salary_range or "",
        "education_requirement": position.education_requirement or "本科",
        "match_analysis": match_data,
    }
```

注意：需要更新文件顶部的 import，添加 `select` 导入（已存在则跳过）。

### Task 5: 更新前端类型定义

**Files:**
- Modify: `frontend/src/types/position.ts`

**Interfaces:**
- Consumes: (无依赖)
- Produces: `PositionDetail`, `DimensionMatch`, `SkillGap`, `StrengthPoint`, `EducationMatch`, `MatchAnalysis`

- [ ] **Step 1: 重写 position.ts 类型文件**

```typescript
/** 岗位信息 */
export interface Position {
  id: number;
  title: string;
  description: string;
  direction_id: number;
  education_requirement: string;
  salary_range: string;
}

/** 岗位推荐记录（后端返回的字段平铺） */
export interface RecommendationRecord {
  id: number;
  title: string;
  description: string;
  city: string;
  salary_range: string;
  match_score: number;
  recommendation_reason: string;
}

/** 单维度匹配分析 */
export interface DimensionMatch {
  user_score: number;
  required_score: number;
  verdict: "match" | "partial" | "mismatch";
  detail: string;
}

/** 技能差距 */
export interface SkillGap {
  skill: string;
  importance: string;
  suggestion: string;
}

/** 优势点 */
export interface StrengthPoint {
  skill: string;
  level: string;
}

/** 学历匹配 */
export interface EducationMatch {
  user_education: string;
  required_education: string;
  verdict: string;
}

/** 完整匹配分析 */
export interface MatchAnalysis {
  knowledge_match: DimensionMatch;
  tool_match: DimensionMatch;
  project_match: DimensionMatch;
  overall_match_score: number;
  recommendation_reason: string;
  skill_gaps: SkillGap[];
  strength_points: StrengthPoint[];
  education_match: EducationMatch;
}

/** 岗位详情 + 匹配分析 */
export interface PositionDetail {
  id: number;
  title: string;
  description: string;
  city: string;
  industry: string;
  salary_range: string;
  education_requirement: string;
  match_analysis: MatchAnalysis;
}
```

### Task 6: 新增前端 API 调用

**Files:**
- Create: `frontend/src/api/positions.ts`

**Interfaces:**
- Consumes: `PositionDetail` from Task 5
- Produces: `getPositionDetail(positionId: number): Promise<PositionDetail>`

- [ ] **Step 1: 创建 positions.ts API 文件**

```typescript
import client from "./client";
import type { PositionDetail } from "../types";

/** 获取岗位详情及用户匹配分析 */
export function getPositionDetail(positionId: number): Promise<PositionDetail> {
  return client.get(`/recommendation/positions/${positionId}/detail`);
}
```

### Task 7: 重写 DirectionSelect 页面为双栏布局

**Files:**
- Modify: `frontend/src/pages/dashboard/DirectionSelect.tsx`

**Interfaces:**
- Consumes: `getDirectionOptions`, `getRecommendations` (from existing API), `getPositionDetail` (from Task 6), `PositionDetail`, `RecommendationRecord`, `Direction` types
- Produces: 完整的双栏岗位选择交互页面

- [ ] **Step 1: 重写 DirectionSelect.tsx**

完整替换文件内容为：

```tsx
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getDirectionOptions, getRecommendations } from "../../api/recommendations";
import { getPositionDetail } from "../../api/positions";
import type { Direction, RecommendationRecord, PositionDetail } from "../../types";
import { useNavigate } from "react-router-dom";
import {
  Loader2, ArrowRight, ArrowLeft, Target, MapPin,
  CheckCircle2, AlertCircle, TrendingUp, Wrench, BookOpen,
  Building2, Zap, Shield,
} from "lucide-react";

const GRADS = [
  "from-indigo-500/20 via-indigo-500/0", "from-rose-500/20 via-rose-500/0",
  "from-violet-500/20 via-violet-500/0", "from-amber-500/20 via-amber-500/0",
  "from-cyan-500/20 via-cyan-500/0", "from-emerald-500/20 via-emerald-500/0",
];

type Screen = "select" | "positions";

export default function DirectionSelect() {
  const navigate = useNavigate();
  const [screen, setScreen] = useState<Screen>("select");
  const [directions, setDirections] = useState<Direction[]>([]);
  const [selectedDirectionId, setSelectedDirectionId] = useState<number | null>(null);
  const [directionName, setDirectionName] = useState("");
  const [positions, setPositions] = useState<RecommendationRecord[]>([]);
  const [selectedPositionId, setSelectedPositionId] = useState<number | null>(null);
  const [positionDetail, setPositionDetail] = useState<PositionDetail | null>(null);
  const [loadingDirections, setLoadingDirections] = useState(true);
  const [loadingPositions, setLoadingPositions] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getDirectionOptions()
      .then(setDirections)
      .catch(() => setError("加载方向列表失败"))
      .finally(() => setLoadingDirections(false));
  }, []);

  const handleSelectDirection = async (id: number, name: string) => {
    setSelectedDirectionId(id);
    setDirectionName(name);
    setSelectedPositionId(null);
    setPositionDetail(null);
    setLoadingPositions(true);
    setError("");
    try {
      const r = await getRecommendations(id);
      setPositions(r);
      setScreen("positions");
      // 默认选中第一个
      if (r.length > 0) {
        setSelectedPositionId(r[0].id);
        loadPositionDetail(r[0].id);
      }
    } catch {
      setError("加载推荐岗位失败");
    } finally {
      setLoadingPositions(false);
    }
  };

  const loadPositionDetail = async (positionId: number) => {
    setLoadingDetail(true);
    try {
      const detail = await getPositionDetail(positionId);
      setPositionDetail(detail);
    } catch {
      setError("加载岗位详情失败");
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSelectPosition = (positionId: number) => {
    if (positionId === selectedPositionId) return;
    setSelectedPositionId(positionId);
    loadPositionDetail(positionId);
  };

  const handleConfirmPosition = () => {
    if (selectedPositionId) {
      // 将选中的岗位 ID 存入 localStorage 供 Planning 使用
      localStorage.setItem("selected_position_id", String(selectedPositionId));
      navigate("/dashboard/planning");
    }
  };

  const handleBackToDirections = () => {
    setScreen("select");
    setSelectedPositionId(null);
    setPositionDetail(null);
    setPositions([]);
  };

  // === 方向选择界面 ===
  if (screen === "select") {
    if (loadingDirections) {
      return (
        <div className="flex items-center justify-center py-32">
          <Loader2 className="w-6 h-6 text-white/10 animate-spin" />
        </div>
      );
    }

    return (
      <div className="max-w-6xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className="text-3xl font-bold">
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">方向选择</span>
          </h1>
          <p className="text-white/35 mt-2">选择一个你感兴趣的职业发展方向</p>
        </motion.div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {directions.map((d, i) => (
            <motion.button
              key={d.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => handleSelectDirection(d.id, d.name)}
              className={`group relative p-6 rounded-2xl border transition-all duration-300 text-left ${
                selectedDirectionId === d.id
                  ? "bg-indigo-500/[0.06] border-indigo-400/30"
                  : "bg-white/[0.01] border-white/[0.06] hover:border-white/[0.15] hover:bg-white/[0.03]"
              }`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${GRADS[i % GRADS.length]} opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-2xl`}
              />
              <div className="relative z-10">
                <h3 className="text-lg font-semibold text-white mb-2">{d.name}</h3>
                <div className="flex flex-wrap gap-1.5">
                  {d.position_examples.slice(0, 3).map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded-full bg-white/[0.03] text-white/30 text-xs">
                      {p}
                    </span>
                  ))}
                </div>
                {d.position_examples.length > 3 && (
                  <span className="text-white/15 text-xs mt-1 block">
                    +{d.position_examples.length - 3} 更多岗位
                  </span>
                )}
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    );
  }

  // === 岗位双栏展示 ===
  return (
    <div className="max-w-[1400px] mx-auto">
      {/* 顶部导航 */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <button
          onClick={handleBackToDirections}
          className="inline-flex items-center gap-1.5 text-white/20 hover:text-white/45 text-sm mb-3 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> 返回方向列表
        </button>
        <h1 className="text-2xl font-bold">
          <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">
            {directionName} · 推荐岗位
          </span>
        </h1>
        <p className="text-white/30 text-sm mt-1">
          共 {positions.length} 个匹配岗位，点击左侧岗位查看详细匹配分析
        </p>
      </motion.div>

      {error && (
        <div className="mb-6 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-sm">
          {error}
        </div>
      )}

      {loadingPositions ? (
        <div className="flex items-center justify-center py-32">
          <Loader2 className="w-6 h-6 text-white/10 animate-spin" />
        </div>
      ) : positions.length === 0 ? (
        <div className="p-12 text-center text-white/20 text-sm rounded-2xl bg-white/[0.01] border border-white/[0.04]">
          该方向暂无匹配岗位
        </div>
      ) : (
        <div className="flex gap-6">
          {/* ====== 左侧：岗位简要列表 (35%) ====== */}
          <div className="w-[35%] flex-shrink-0 space-y-3">
            <h2 className="text-white/40 text-xs font-semibold uppercase tracking-wider mb-3 px-1">
              推荐岗位列表
            </h2>
            {positions.map((pos, i) => {
              const isSelected = selectedPositionId === pos.id;
              return (
                <motion.button
                  key={pos.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => handleSelectPosition(pos.id)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                    isSelected
                      ? "bg-indigo-500/[0.08] border-indigo-400/30 shadow-[0_0_20px_rgba(99,102,241,0.05)]"
                      : "bg-white/[0.01] border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.02]"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className={`font-semibold text-sm ${isSelected ? "text-white" : "text-white/70"}`}>
                      {pos.title}
                    </h3>
                    <span
                      className={`flex-shrink-0 text-xs font-bold ml-2 ${
                        isSelected
                          ? "bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300"
                          : "text-white/30"
                      }`}
                    >
                      {pos.match_score}%
                    </span>
                  </div>
                  <div className="flex flex-col gap-1 text-xs text-white/25">
                    {pos.city && (
                      <span className="inline-flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> {pos.city}
                      </span>
                    )}
                    {pos.salary_range && (
                      <span className="inline-flex items-center gap-1">
                        <Target className="w-3 h-3" /> {pos.salary_range}
                      </span>
                    )}
                  </div>
                  {/* 所需能力标签 */}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(pos.description || "")
                      .slice(0, 80)
                      .split(/[,，、]/)
                      .slice(0, 3)
                      .map((tag) => {
                        const trimmed = tag.trim();
                        if (!trimmed) return null;
                        return (
                          <span
                            key={trimmed}
                            className="px-1.5 py-0.5 rounded bg-white/[0.03] text-white/20 text-[10px]"
                          >
                            {trimmed.length > 12 ? trimmed.slice(0, 12) + "…" : trimmed}
                          </span>
                        );
                      })}
                  </div>
                </motion.button>
              );
            })}
          </div>

          {/* ====== 右侧：岗位详情 + 匹配分析 (65%) ====== */}
          <div className="flex-1 min-w-0">
            <AnimatePresence mode="wait">
              {loadingDetail ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-center py-32"
                >
                  <Loader2 className="w-6 h-6 text-white/10 animate-spin" />
                </motion.div>
              ) : positionDetail ? (
                <motion.div
                  key={positionDetail.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.25 }}
                  className="space-y-5"
                >
                  {/* 岗位基本信息卡片 */}
                  <div className="p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h2 className="text-xl font-bold text-white">{positionDetail.title}</h2>
                        <div className="flex items-center gap-4 mt-2 text-sm text-white/30">
                          {positionDetail.city && (
                            <span className="inline-flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5" /> {positionDetail.city}
                            </span>
                          )}
                          {positionDetail.salary_range && (
                            <span className="inline-flex items-center gap-1">
                              <Target className="w-3.5 h-3.5" /> {positionDetail.salary_range}
                            </span>
                          )}
                          {positionDetail.industry && (
                            <span className="inline-flex items-center gap-1">
                              <Building2 className="w-3.5 h-3.5" /> {positionDetail.industry}
                            </span>
                          )}
                        </div>
                      </div>
                      {/* 综合匹配度 */}
                      <div className="flex-shrink-0 flex flex-col items-center">
                        <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
                          {positionDetail.match_analysis.overall_match_score}
                        </span>
                        <span className="text-white/20 text-xs">综合匹配度</span>
                      </div>
                    </div>
                    <p className="text-white/35 text-sm leading-relaxed">
                      {positionDetail.description}
                    </p>
                  </div>

                  {/* 三维度匹配对比 */}
                  <div className="p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                    <h3 className="text-white/50 font-semibold text-sm mb-4 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-amber-400/60" /> 能力维度匹配对比
                    </h3>
                    <div className="space-y-4">
                      {[
                        {
                          key: "knowledge_match",
                          label: "知识",
                          icon: BookOpen,
                          data: positionDetail.match_analysis.knowledge_match,
                        },
                        {
                          key: "tool_match",
                          label: "工具",
                          icon: Wrench,
                          data: positionDetail.match_analysis.tool_match,
                        },
                        {
                          key: "project_match",
                          label: "项目",
                          icon: TrendingUp,
                          data: positionDetail.match_analysis.project_match,
                        },
                      ].map(({ key, label, icon: Icon, data }) => (
                        <div key={key} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-white/45 text-sm flex items-center gap-1.5">
                              <Icon className="w-3.5 h-3.5" /> {label}
                            </span>
                            <span
                              className={`text-xs px-2 py-0.5 rounded-full ${
                                data.verdict === "match"
                                  ? "bg-emerald-500/10 text-emerald-400/80"
                                  : data.verdict === "partial"
                                    ? "bg-amber-500/10 text-amber-400/80"
                                    : "bg-rose-500/10 text-rose-400/80"
                              }`}
                            >
                              {data.verdict === "match" ? "✓ 匹配" : data.verdict === "partial" ? "△ 部分匹配" : "✗ 不匹配"}
                            </span>
                          </div>
                          {/* 进度条对比 */}
                          <div className="flex items-center gap-3">
                            <span className="text-white/20 text-xs w-8 text-right">你 {data.user_score}</span>
                            <div className="flex-1 h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                              <div
                                className="h-full rounded-full bg-gradient-to-r from-indigo-400/60 to-indigo-400/30"
                                style={{ width: `${(data.user_score / 100) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-white/20 text-xs w-8 text-right">要求 {data.required_score}</span>
                            <div className="flex-1 h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                              <div
                                className="h-full rounded-full bg-white/[0.15]"
                                style={{ width: `${(data.required_score / 100) * 100}%` }}
                              />
                            </div>
                          </div>
                          <p className="text-white/25 text-xs mt-1">{data.detail}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 学历匹配 */}
                  <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.04] flex items-center gap-3">
                    <Shield className="w-4 h-4 text-emerald-400/60" />
                    <span className="text-white/40 text-sm">学历要求：</span>
                    <span className="text-white/60 text-sm font-medium">
                      {positionDetail.match_analysis.education_match.required_education}
                    </span>
                    <span className="text-white/20 text-sm">· 你的学历：</span>
                    <span className="text-white/60 text-sm font-medium">
                      {positionDetail.match_analysis.education_match.user_education}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400/80 text-xs ml-auto">
                      ✓ 满足
                    </span>
                  </div>

                  {/* 推荐理由 */}
                  <div className="p-5 rounded-2xl bg-indigo-500/[0.03] border border-indigo-500/[0.08]">
                    <h3 className="text-indigo-300/60 font-semibold text-sm mb-2">💡 匹配分析</h3>
                    <p className="text-white/35 text-sm leading-relaxed">
                      {positionDetail.match_analysis.recommendation_reason}
                    </p>
                  </div>

                  {/* 优势 + 差距 两列 */}
                  <div className="grid grid-cols-2 gap-4">
                    {/* 优势 */}
                    <div className="p-4 rounded-2xl bg-emerald-500/[0.02] border border-emerald-500/[0.08]">
                      <h3 className="text-emerald-400/60 font-semibold text-sm mb-3 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" /> 你的优势
                      </h3>
                      <div className="space-y-2">
                        {positionDetail.match_analysis.strength_points.map((sp) => (
                          <div key={sp.skill} className="flex items-center justify-between">
                            <span className="text-white/55 text-sm">{sp.skill}</span>
                            <span className="text-emerald-400/40 text-xs">{sp.level}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    {/* 差距 */}
                    <div className="p-4 rounded-2xl bg-amber-500/[0.02] border border-amber-500/[0.08]">
                      <h3 className="text-amber-400/60 font-semibold text-sm mb-3 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" /> 建议提升
                      </h3>
                      <div className="space-y-3">
                        {positionDetail.match_analysis.skill_gaps.map((gap) => (
                          <div key={gap.skill}>
                            <div className="flex items-center justify-between mb-0.5">
                              <span className="text-white/55 text-sm">{gap.skill}</span>
                              <span className="text-amber-400/40 text-xs">[{gap.importance}]</span>
                            </div>
                            <p className="text-white/20 text-xs">{gap.suggestion}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* 底部操作按钮 */}
                  <div className="flex items-center justify-between pt-4 pb-8">
                    <button
                      onClick={() => {
                        // 选下一个未选过的岗位
                        const currentIdx = positions.findIndex((p) => p.id === selectedPositionId);
                        if (currentIdx < positions.length - 1) {
                          handleSelectPosition(positions[currentIdx + 1].id);
                        }
                      }}
                      disabled={(() => {
                        const currentIdx = positions.findIndex((p) => p.id === selectedPositionId);
                        return currentIdx >= positions.length - 1;
                      })()}
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/[0.03] border border-white/[0.08] text-white/35 text-sm hover:bg-white/[0.06] transition-all disabled:opacity-20 disabled:cursor-not-allowed"
                    >
                      不满意，换一个 <ArrowRight className="w-4 h-4" />
                    </button>
                    <button
                      onClick={handleConfirmPosition}
                      className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 transition-all"
                    >
                      选定此岗位，进入深度规划 <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Task 8: 更新 Planning 页面基于岗位生成

**Files:**
- Modify: `frontend/src/pages/dashboard/Planning.tsx`

**Interfaces:**
- Consumes: `analyzeTrend`, `generatePath`, `regeneratePath` (all updated to require position_id)
- Produces: 基于岗位的深度规划页面

- [ ] **Step 1: 修改 Planning.tsx 的 loadData 和 data 加载逻辑**

关键改动点：

1. 从 localStorage 读取 `selected_position_id`
2. 调用趋势/路径接口时传入 `position_id`
3. 显示"基于岗位：XXX"而不是"基于方向：XXX"

修改内容（精确到改动点）：

在 `useEffect` 中，改为从 localStorage 读取：

```tsx
useEffect(() => {
  getProgress()
    .then((p) => {
      if (p.selected_direction_id) {
        // 从 localStorage 读取用户确认的岗位 ID
        const positionId = localStorage.getItem("selected_position_id");
        loadData(p.selected_direction_id, positionId ? Number(positionId) : undefined);
      } else {
        setError("请先在第三步选择一个职业方向");
        setLoading(false);
      }
    })
    .catch(() => {
      setError("加载进度失败");
      setLoading(false);
    });
}, []);
```

修改 `loadData` 函数签名和实现：

```tsx
const loadData = async (did: number, pid?: number) => {
  setDirectionId(did);
  setPositionId(pid || null);
  setLoading(true);
  setError("");
  try {
    const [t, p] = await Promise.all([
      analyzeTrend(did, pid),
      generatePath(did, pid),
    ]);
    setTrend(t);
    setPath(p);
  } catch {
    setError("加载失败");
  } finally {
    setLoading(false);
  }
};
```

添加 `positionId` 状态和 `positionName` 状态：

```tsx
const [positionId, setPositionId] = useState<number | null>(null);
const [positionName, setPositionName] = useState<string>("");
```

在页面标题下方添加岗位名称显示（从 trend 或 path 数据中获取，或从 localStorage 读取）：

在顶部标题区域，directionName 后面显示岗位名。

修改 `handleRegenerate` 以传入 position_id。

### Task 9: 更新趋势/路径 API 调用（position_id 必传）

**Files:**
- Modify: `frontend/src/api/trends.ts`
- Modify: `frontend/src/api/development.ts`

**Interfaces:**
- Consumes: (无)
- Produces: 更新后的函数签名

- [ ] **Step 1: trends.ts — position_id 改为必传**

```typescript
import client from "./client";
import type { TrendAnalysis } from "../types";

/** 分析选定岗位的行业趋势 */
export function analyzeTrend(directionId: number, positionId: number): Promise<TrendAnalysis> {
  return client.post("/trend/analyze", {
    direction_id: directionId,
    position_id: positionId,
  });
}
```

- [ ] **Step 2: development.ts — position_id 改为必传**

```typescript
import client from "./client";
import type { DevelopmentPath } from "../types";

/** 生成发展路径 */
export function generatePath(directionId: number, positionId: number): Promise<DevelopmentPath> {
  return client.post("/development/generate", {
    direction_id: directionId,
    position_id: positionId,
  });
}

/** 重新生成路径（版本 +1） */
export function regeneratePath(directionId: number, positionId: number): Promise<DevelopmentPath> {
  return client.post("/development/regenerate", {
    direction_id: directionId,
    position_id: positionId,
  });
}
```

---

## 完成检查清单

- [ ] 后端：`FAKE_analyze_position_match` 函数含完整注释（功能+TODO+预期模型+调用位置）
- [ ] 后端：`GET /recommendation/positions/{id}/detail` 返回 200
- [ ] 后端：`model_interface.py` 导出新函数
- [ ] 前端：DirectionSelect 方向选择正常跳转到双栏
- [ ] 前端：左侧岗位列表可点击切换右侧详情
- [ ] 前端：右侧显示完整匹配分析（三维度对比+优势+差距+理由）
- [ ] 前端：可从双栏退回重新选方向
- [ ] 前端：确认岗位后跳转 Planning
- [ ] 前端：Planning 基于岗位生成趋势和路径
- [ ] 全流程：注册→MBTI→能力→选方向→选岗位→规划→报告 无报错
