import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { analyzeTrend } from "../../api/trends";
import { generatePath, regeneratePath } from "../../api/development";
import { getProgress } from "../../api/progress";
import type { TrendAnalysis, DevelopmentPath } from "../../types";
import { Loader2, TrendingUp, BookOpen, RotateCcw, AlertTriangle, ArrowRight, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

type Tab = "trend" | "path";

export default function Planning() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>("trend");
  const [directionId, setDirectionId] = useState<number | null>(null);
  const [directionName, setDirectionName] = useState<string>("");
  const [positionId, setPositionId] = useState<number | null>(null);
  const [trend, setTrend] = useState<TrendAnalysis | null>(null);
  const [path, setPath] = useState<DevelopmentPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getProgress()
      .then((p) => {
        if (p.selected_direction_id) {
          const pid = localStorage.getItem("selected_position_id");
          loadData(p.selected_direction_id, pid ? Number(pid) : undefined);
        } else {
          setError("请先在第三步选择一个职业方向");
          setLoading(false);
        }
      })
      .catch(() => { setError("加载进度失败"); setLoading(false); });
  }, []);

  const loadData = async (did: number, pid?: number) => {
    setDirectionId(did);
    if (pid) setPositionId(pid);
    setLoading(true); setError("");
    try {
      const [t, p] = await Promise.all([
        analyzeTrend(did, pid || 0),
        generatePath(did, pid || 0),
      ]);
      setTrend(t); setPath(p);
    } catch { setError("加载失败"); }
    finally { setLoading(false); }
  };

  const handleRegenerate = async () => {
    if (!directionId) return;
    setLoading(true);
    try { const p = await regeneratePath(directionId, positionId || 0); setPath(p); }
    catch { setError("重新生成失败"); }
    finally { setLoading(false); }
  };

  if (loading) return <div className="flex items-center justify-center py-32"><Loader2 className="w-6 h-6 text-white/10 animate-spin" /></div>;

  // 没选方向时，显示引导提示
  if (!directionId) {
    return (
      <div className="max-w-5xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold"><span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">深度规划</span></h1>
          <p className="text-white/35 mt-2">行业趋势分析与发展路径建议</p>
        </motion.div>
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <AlertCircle className="w-10 h-10 text-amber-400/40 mb-4" />
          <p className="text-white/30 text-sm mb-4">{error || "请先在第三步选择一个职业方向"}</p>
          <button onClick={() => navigate("/dashboard/direction")}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white/[0.06] border border-white/[0.1] text-white/50 text-sm hover:bg-white/[0.1] transition-all">
            返回方向选择 <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-3xl font-bold"><span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">深度规划</span></h1>
        <p className="text-white/35 mt-2">行业趋势分析与发展路径建议</p>
      </motion.div>

      {error && <div className="mb-6 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-sm">{error}</div>}

      {/* Tab 切换 */}
      <div className="flex gap-1 mb-8 bg-white/[0.03] rounded-xl p-1 w-fit">
        {([["trend","行业趋势"],["path","发展路径"]] as [Tab,string][]).map(([k,label]) => (
          <button key={k} onClick={() => setTab(k)}
            className={`px-5 py-2 rounded-lg text-sm transition-all ${tab === k ? "bg-white/[0.08] text-white/80" : "text-white/25 hover:text-white/45"}`}>
            {k === "trend" ? <><TrendingUp className="w-3.5 h-3.5 inline mr-1.5" />{label}</> : <><BookOpen className="w-3.5 h-3.5 inline mr-1.5" />{label}</>}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {tab === "trend" && trend && (
          <motion.div key="trend" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {[
                { k: "overview", label: "3-5年发展趋势" },
                { k: "tech_impact", label: "技术变革影响" },
                { k: "regional_demand", label: "地域需求差异" },
                { k: "salary_trend", label: "薪资走向" },
                { k: "entry_barrier", label: "入门门槛变化" },
                { k: "personal_analysis", label: "与你相关的分析" },
              ].map(({ k, label }) => (
                <div key={k} className="p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                  <h3 className="text-white/50 font-semibold text-sm mb-2">{label}</h3>
                  <p className="text-white/35 text-sm leading-relaxed">{(trend.trend_data as any)[k]}</p>
                </div>
              ))}
            </div>
            {trend.risk_warnings.length > 0 && (
              <div className="p-5 rounded-2xl bg-amber-500/[0.03] border border-amber-500/[0.1] mb-8">
                <h3 className="text-amber-400/60 text-sm font-semibold mb-2 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />风险提示</h3>
                <ul className="space-y-1">{trend.risk_warnings.map((w,i)=><li key={i} className="text-white/35 text-sm">{w}</li>)}</ul>
              </div>
            )}
          </motion.div>
        )}

        {tab === "path" && path && (
          <motion.div key="path" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex items-center justify-between mb-4">
              <span className="text-white/15 text-xs">版本 {path.version}</span>
              <button onClick={handleRegenerate} className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white/[0.02] border border-white/[0.06] text-white/25 text-xs hover:bg-white/[0.05] transition-colors">
                <RotateCcw className="w-3 h-3" />重新生成
              </button>
            </div>

            {[
              { key: "short_term_path", label: "短期", color: "border-l-emerald-500/30" },
              { key: "mid_term_path", label: "中期", color: "border-l-amber-500/30" },
              { key: "long_term_path", label: "长期", color: "border-l-indigo-500/30" },
            ].map(({ key, label, color }) => {
              const data = (path as any)[key];
              return (
                <div key={key} className={`p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06] border-l-2 ${color} mb-4`}>
                  <h3 className="text-white/50 font-semibold text-sm mb-1">{label} · {data.duration}</h3>
                  <p className="text-white/35 text-sm mb-2">{data.goal}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {(data.skills || []).map((s: string) => <span key={s} className="px-2 py-0.5 rounded bg-white/[0.03] text-white/25 text-xs">{s}</span>)}
                  </div>
                </div>
              );
            })}

            {/* 资源列表 */}
            <div className="mt-8">
              <h3 className="text-white/50 font-semibold text-sm mb-3">学习资源</h3>
              <div className="space-y-2">
                {(path.resource_list || []).map((r: any) => (
                  <div key={r.name} className="p-4 rounded-xl bg-white/[0.015] border border-white/[0.06] flex items-start justify-between">
                    <div>
                      <p className="text-white/55 text-sm">{r.name}</p>
                      <p className="text-white/20 text-xs mt-1">{r.description}</p>
                    </div>
                    <span className="text-white/15 text-xs flex-shrink-0 ml-4">{r.type}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="text-center mt-8 pb-8">
        <button onClick={() => navigate("/dashboard/report")}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 transition-all">
          下一步：报告生成 <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
