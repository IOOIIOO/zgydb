import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getDirections } from "../../api/directions";
import type { Direction } from "../../types";
import { ArrowRight, Briefcase, Loader2, Compass } from "lucide-react";

const GRADS = [
  "from-indigo-500/15 via-indigo-500/0",
  "from-rose-500/15 via-rose-500/0",
  "from-violet-500/15 via-violet-500/0",
  "from-amber-500/15 via-amber-500/0",
  "from-cyan-500/15 via-cyan-500/0",
  "from-emerald-500/15 via-emerald-500/0",
];

export default function DirectionList() {
  const [dirs, setDirs] = useState<Direction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDirections().then(setDirs).catch(() => setError("加载失败")).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-[#030303] flex items-center justify-center">
      <Loader2 className="w-8 h-8 text-white/10 animate-spin" />
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#030303] flex items-center justify-center">
      <p className="text-rose-400/80 text-sm">{error}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#030303]">
      <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.23, 0.86, 0.39, 0.96] }}
          className="text-center mb-14"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.08] mb-6">
            <Compass className="w-3.5 h-3.5 text-rose-400/60" />
            <span className="text-xs text-white/40">快速了解</span>
          </div>
          <h1 className="text-3xl font-bold mb-3">
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">探索职业方向</span>
          </h1>
          <p className="text-white/25">了解每个方向的发展前景与所需技能，为未来做出明智选择</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {dirs.map((d, i) => (
            <motion.div
              key={d.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04, duration: 0.4, ease: [0.23, 0.86, 0.39, 0.96] }}
            >
              <Link
                to={`/quick-overview/${d.id}`}
                className="group relative block p-6 rounded-2xl bg-white/[0.015] border border-white/[0.06] hover:border-white/[0.15] transition-all duration-300 overflow-hidden"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${GRADS[i % GRADS.length]} opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none`} />

                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold text-white group-hover:text-white/90 transition-colors">
                      {d.name}
                    </h2>
                    <ArrowRight className="w-4 h-4 text-white/15 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all" />
                  </div>

                  <div className="flex flex-wrap gap-1.5">
                    {d.position_examples.slice(0, 4).map((p) => (
                      <span key={p} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/[0.03] border border-white/[0.05] text-white/30 text-xs">
                        <Briefcase className="w-3 h-3 text-white/15" />
                        {p}
                      </span>
                    ))}
                    {d.position_examples.length > 4 && (
                      <span className="text-white/15 text-xs px-1 self-center">+{d.position_examples.length - 4}</span>
                    )}
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
