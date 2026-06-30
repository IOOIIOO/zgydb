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
        <div className="flex gap-6 h-[calc(100vh-180px)]">
          {/* ====== 左侧：岗位简要列表 (35%) ====== */}
          <div className="w-[35%] flex-shrink-0 space-y-3 overflow-y-auto pr-1">
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
          <div className="flex-1 min-w-0 overflow-y-auto">
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
                  <div className="flex items-center justify-end pt-4 pb-8">
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
