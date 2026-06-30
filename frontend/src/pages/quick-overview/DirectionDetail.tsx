import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getDirectionDetail } from "../../api/directions";
import type { Direction } from "../../types";
import { ArrowLeft, Briefcase, Cpu, TrendingUp, Loader2 } from "lucide-react";

export default function DirectionDetail() {
  const { directionId } = useParams<{ directionId: string }>();
  const [d, setD] = useState<Direction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!directionId) return;
    getDirectionDetail(Number(directionId)).then(setD).catch(() => setError("加载失败")).finally(() => setLoading(false));
  }, [directionId]);

  if (loading) return (
    <div className="min-h-screen bg-[#030303] flex items-center justify-center">
      <Loader2 className="w-6 h-6 text-white/10 animate-spin" />
    </div>
  );

  if (error || !d) return (
    <div className="min-h-screen bg-[#030303] flex flex-col items-center justify-center gap-4">
      <p className="text-rose-400/80 text-sm">{error || "方向不存在"}</p>
      <Link to="/quick-overview" className="text-white/30 hover:text-white/50 text-sm transition-colors">返回列表</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#030303]">
      <div className="max-w-7xl mx-auto px-6 pt-24 pb-20">
        {/* 返回 + 标题 */}
        <Link to="/quick-overview" className="inline-flex items-center gap-2 text-white/20 hover:text-white/45 transition-colors mb-8 text-sm">
          <ArrowLeft className="w-4 h-4" />返回方向列表
        </Link>

        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold mb-14"
        >
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-white/90 to-indigo-300">{d.name}</span>
        </motion.h1>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10">
          {/* 左：岗位 + 技术 */}
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
              className="p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06]"
            >
              <div className="flex items-center gap-2.5 mb-5">
                <Briefcase className="w-4 h-4 text-indigo-400/60" />
                <h2 className="text-white/70 font-semibold text-sm">岗位举例</h2>
              </div>
              <div className="space-y-1.5">
                {d.position_examples.map((p, i) => (
                  <div key={i} className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-white/[0.02] border border-white/[0.04] text-white/50 text-sm">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/40 flex-shrink-0" />
                    {p}
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}
              className="p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06]"
            >
              <div className="flex items-center gap-2.5 mb-5">
                <Cpu className="w-4 h-4 text-amber-400/60" />
                <h2 className="text-white/70 font-semibold text-sm">所需能力与技术</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {d.required_skills.map((s) => (
                  <span key={s} className="px-3 py-1.5 rounded-lg bg-amber-500/[0.05] border border-amber-500/[0.1] text-amber-300/60 text-sm">
                    {s}
                  </span>
                ))}
              </div>
            </motion.div>
          </div>

          {/* 右：趋势 */}
          <motion.div
            initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="lg:col-span-3 p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06]"
          >
            <div className="flex items-center gap-2.5 mb-5">
              <TrendingUp className="w-4 h-4 text-rose-400/60" />
              <h2 className="text-white/70 font-semibold text-sm">未来发展趋势</h2>
            </div>
            <div className="text-white/40 leading-relaxed text-sm whitespace-pre-line">{d.development_trend}</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
