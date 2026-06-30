import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useProgress } from "../../hooks/useProgress";
import { ArrowRight, Lock, CheckCircle2, Circle } from "lucide-react";
import { cn } from "../../lib/utils";

const STEPS = [
  { step: 1, title: "性格分析", desc: "完成 MBTI 测评，了解性格特质与职业倾向", route: "/dashboard/personality" },
  { step: 2, title: "能力评估", desc: "上传简历或描述经历，获取能力雷达画像", route: "/dashboard/ability" },
  { step: 3, title: "方向选择", desc: "浏览并选择感兴趣的职业发展方向", route: "/dashboard/direction" },
  { step: 4, title: "深度规划", desc: "查看行业趋势分析与发展路径建议", route: "/dashboard/planning" },
  { step: 5, title: "报告生成", desc: "汇总全部数据，生成并导出 PDF 综合报告", route: "/dashboard/report" },
];

const CARD_GRADS = [
  "from-indigo-500/20 via-indigo-500/0",
  "from-rose-500/20 via-rose-500/0",
  "from-violet-500/20 via-violet-500/0",
  "from-amber-500/20 via-amber-500/0",
  "from-cyan-500/20 via-cyan-500/0",
];

export default function Dashboard() {
  const { progress, loading } = useProgress();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 rounded-full border-2 border-white/10 border-t-white/30 animate-spin" />
      </div>
    );
  }

  const flags = [
    progress?.step1_completed, progress?.step2_completed,
    progress?.step3_completed, progress?.step4_completed, progress?.step5_completed,
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.23, 0.86, 0.39, 0.96] }}
        className="mb-10"
      >
        <h1 className="text-3xl font-bold">
          <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">
            我的职业规划
          </span>
        </h1>
        <p className="text-white/35 mt-2">按顺序完成 5 个步骤，获取专属职业发展报告</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {STEPS.map((s, i) => {
          const done = flags[s.step - 1] ?? false;
          const prev = s.step === 1 ? true : (flags[s.step - 2] ?? false);
          const open = prev || (progress?.current_step ?? 1) >= s.step;

          return (
            <motion.div
              key={s.step}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 * i, duration: 0.45, ease: [0.23, 0.86, 0.39, 0.96] }}
            >
              <Link
                to={open ? s.route : "#"}
                className={cn(
                  "group relative block p-6 rounded-2xl border transition-all duration-300 overflow-hidden",
                  done && "bg-emerald-500/[0.03] border-emerald-500/20 hover:border-emerald-500/40",
                  !done && open && "bg-white/[0.01] border-white/[0.06] hover:border-white/[0.15] hover:bg-white/[0.03]",
                  !open && "bg-white/[0.005] border-white/[0.03] opacity-40 cursor-default",
                )}
              >
                {/* 悬停渐变 */}
                {open && (
                  <div className={cn(
                    "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none",
                    CARD_GRADS[i % CARD_GRADS.length],
                  )} />
                )}

                <div className="relative z-10">
                  {/* 步骤号 */}
                  <div className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center mb-4 transition-colors",
                    done && "bg-emerald-500/15 text-emerald-400",
                    !done && open && "bg-white/[0.06] text-white/60",
                    !open && "bg-white/[0.03] text-white/15",
                  )}>
                    {done ? <CheckCircle2 className="w-5 h-5" /> :
                     open ? <span className="text-sm font-bold">{s.step}</span> :
                     <Lock className="w-4 h-4" />}
                  </div>

                  <h3 className={cn("text-lg font-semibold mb-1.5", open ? "text-white" : "text-white/20")}>
                    {s.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-white/25">{s.desc}</p>

                  <div className="mt-4 flex items-center gap-1.5 text-xs">
                    {done ? (
                      <span className="text-emerald-400/60">已完成</span>
                    ) : open ? (
                      <>
                        <span className="text-white/35">开始</span>
                        <ArrowRight className="w-3 h-3 text-white/25" />
                      </>
                    ) : (
                      <span className="text-white/10">需完成上一步</span>
                    )}
                  </div>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
