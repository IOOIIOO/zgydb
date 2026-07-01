import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getMbtiQuestions, submitMbtiAnswers, getPersonalityResult } from "../../api/personality";
import type { MbtiQuestion, PersonalityResult } from "../../types";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, RotateCcw, Loader2 } from "lucide-react";

type Mode = "loading" | "answer" | "result";

const INTENSITY: Record<number, string> = { 1: "倾向型", 2: "典型型", 3: "显著型" };

const DIM_META: Record<string, { left: string; right: string; bar: string }> = {
  EI: { left: "外向", right: "内向", bar: "from-sky-400 to-blue-500" },
  SN: { left: "实感", right: "直觉", bar: "from-emerald-400 to-teal-500" },
  TF: { left: "理性", right: "感性", bar: "from-amber-400 to-orange-500" },
  JP: { left: "条理", right: "灵活", bar: "from-violet-400 to-purple-500" },
};

export default function Personality() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>("loading");
  const [questions, setQuestions] = useState<MbtiQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [idx, setIdx] = useState(0);
  const [result, setResult] = useState<PersonalityResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // 始终预加载题目（"重做"按钮需要）
    getMbtiQuestions()
      .then((d) => { setQuestions(d.questions || []); })
      .catch(() => setError("加载题目失败"));

    // 检查已有结果：有→展示结果，无→答题模式
    getPersonalityResult()
      .then((r) => { if (r) { setResult(r); setMode("result"); } else { setMode("answer"); } })
      .catch(() => { setMode("answer"); });
  }, []);

  const pick = (choice: "a" | "b") => {
    const q = questions[idx]; if (!q) return;
    setAnswers((p) => ({ ...p, [q.id]: choice }));
    if (idx < questions.length - 1) setTimeout(() => setIdx((c) => c + 1), 180);
  };

  const submit = async () => {
    setSubmitting(true); setError("");
    try { const r = await submitMbtiAnswers(answers); setResult(r); setMode("result"); }
    catch { setError("提交失败，请重试"); }
    finally { setSubmitting(false); }
  };

  const retry = () => { setAnswers({}); setIdx(0); setResult(null); setMode("answer"); };

  // ---- Loading ----
  if (mode === "loading") return (
    <div className="flex items-center justify-center py-32">
      <Loader2 className="w-6 h-6 text-white/10 animate-spin" />
    </div>
  );

  // ====== 结果模式 ======
  if (mode === "result" && result) {
    const dims = [
      { key: "EI", a: result.ei_score, b: 10 - result.ei_score },
      { key: "SN", a: result.sn_score, b: 10 - result.sn_score },
      { key: "TF", a: result.tf_score, b: 10 - result.tf_score },
      { key: "JP", a: result.jp_score, b: 10 - result.jp_score },
    ];

    return (
      <div className="max-w-5xl mx-auto py-4">
        <p className="text-center text-white/10 text-xs mb-12">测评结果仅供个人参考，不构成心理诊断</p>

        {/* 类型码 — 模糊→清晰 */}
        <motion.div
          initial={{ filter: "blur(16px)", opacity: 0, scale: 0.95 }}
          animate={{ filter: "blur(0px)", opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: [0.23, 0.86, 0.39, 0.96] }}
          className="text-center mb-3"
        >
          <div className="text-[clamp(5rem,10vw,9rem)] font-bold leading-none tracking-tighter bg-clip-text text-transparent bg-gradient-to-b from-white via-white/90 to-white/40 select-none">
            {result.personality_type}
          </div>
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-white/20 text-sm mb-16"
        >
          {INTENSITY[result.intensity_level] || result.intensity_level} · 测评完成
        </motion.p>

        {/* 四维度 */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
          className="grid grid-cols-2 gap-3 mb-12"
        >
          {dims.map((d, i) => {
            const m = DIM_META[d.key];
            const ap = (d.a / 10) * 100;
            return (
              <motion.div
                key={d.key}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + i * 0.07 }}
                className="p-5 rounded-2xl bg-white/[0.015] border border-white/[0.05]"
              >
                <div className="flex justify-between text-xs text-white/20 mb-3">
                  <span>{m.left}</span><span>{m.right}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-white/40 text-sm w-6 text-right font-mono">{d.a}</span>
                  <div className="flex-1 flex gap-1">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${ap}%` }}
                      transition={{ delay: 0.9 + i * 0.07, duration: 0.5, ease: "easeOut" }}
                      className={`h-1.5 rounded-full bg-gradient-to-r ${m.bar}`}
                    />
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${100 - ap}%` }}
                      transition={{ delay: 0.9 + i * 0.07, duration: 0.5, ease: "easeOut" }}
                      className="h-1.5 rounded-full bg-white/[0.06]"
                    />
                  </div>
                  <span className="text-white/40 text-sm w-6 font-mono">{d.b}</span>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* 长处 + 短板 */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}
          className="grid grid-cols-2 gap-8 mb-12"
        >
          <div>
            <h3 className="text-emerald-400/60 text-xs font-semibold tracking-wider uppercase mb-4">长处</h3>
            <ul className="space-y-2">
              {result.strengths.map((s, i) => (
                <li key={i} className="text-white/40 text-sm pl-4 border-l border-emerald-500/20 leading-relaxed">
                  {s.replace(/（[^）]*）$/, "")}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-amber-400/60 text-xs font-semibold tracking-wider uppercase mb-4">需关注</h3>
            <ul className="space-y-2">
              {result.weaknesses.map((w, i) => (
                <li key={i} className="text-white/40 text-sm pl-4 border-l border-amber-500/20 leading-relaxed">
                  {w.replace(/（[^）]*）$/, "")}
                </li>
              ))}
            </ul>
          </div>
        </motion.div>

        {/* 画像 + 方向 */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }}
          className="grid grid-cols-3 gap-8 mb-12"
        >
          <div className="col-span-2">
            <h3 className="text-white/25 text-xs font-semibold tracking-wider uppercase mb-4">综合画像</h3>
            <p className="text-white/35 text-sm leading-relaxed">{result.portrait_description}</p>
          </div>
          <div>
            <h3 className="text-white/25 text-xs font-semibold tracking-wider uppercase mb-4">建议方向</h3>
            <div className="flex flex-wrap gap-2">
              {result.direction_tendencies.map((d) => (
                <span key={d} className="px-3 py-1.5 rounded-full bg-white/[0.02] border border-white/[0.06] text-white/35 text-xs hover:border-white/[0.12] hover:text-white/55 transition-colors cursor-default">
                  {d}
                </span>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }} className="flex items-center justify-center gap-4 pb-8">
          <button onClick={retry}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white/[0.02] border border-white/[0.06] text-white/25 text-sm hover:bg-white/[0.05] hover:text-white/45 transition-all">
            <RotateCcw className="w-3.5 h-3.5" />重新测评
          </button>
          <button onClick={() => navigate("/dashboard/ability")}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 transition-all">
            下一步：能力评估 <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    );
  }

  // ====== 答题模式 ======
  const q = questions[idx];
  const pct = questions.length ? (idx / questions.length) * 100 : 0;

  return (
    <div className="max-w-2xl mx-auto py-4">
      <div className="flex items-center justify-between mb-12 text-xs text-white/12">
        <span>MBTI 性格测评</span><span>{idx + 1} / {questions.length}</span>
      </div>

      {/* 细线进度 */}
      <div className="h-px bg-white/[0.04] mb-16">
        <motion.div
          className="h-px bg-gradient-to-r from-indigo-400/60 via-rose-400/40 to-transparent"
          animate={{ width: `${pct}%` }} transition={{ duration: 0.3 }}
        />
      </div>

      {error && (
        <div className="mb-8 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-xs text-center">{error}</div>
      )}

      <AnimatePresence mode="wait">
        {q && (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.3, ease: [0.23, 0.86, 0.39, 0.96] }}
            className="mb-16"
          >
            <h2 className="text-xl text-white/70 leading-relaxed text-center mb-12 px-4">{q.text}</h2>

            <div className="grid grid-cols-2 gap-4">
              <button onClick={() => pick("a")}
                className={`group relative p-6 rounded-2xl border transition-all duration-300 text-left ${answers[q.id] === "a" ? "bg-indigo-500/[0.06] border-indigo-400/30" : "bg-white/[0.01] border-white/[0.05] hover:border-white/[0.12] hover:bg-white/[0.02]"}`}>
                <div className="text-[10px] text-white/12 mb-3 tracking-widest">选项 A</div>
                <p className={`text-sm leading-relaxed transition-colors ${answers[q.id] === "a" ? "text-white/80" : "text-white/35 group-hover:text-white/55"}`}>{q.option_a}</p>
              </button>
              <button onClick={() => pick("b")}
                className={`group relative p-6 rounded-2xl border transition-all duration-300 text-left ${answers[q.id] === "b" ? "bg-rose-500/[0.06] border-rose-400/30" : "bg-white/[0.01] border-white/[0.05] hover:border-white/[0.12] hover:bg-white/[0.02]"}`}>
                <div className="text-[10px] text-white/12 mb-3 tracking-widest">选项 B</div>
                <p className={`text-sm leading-relaxed transition-colors ${answers[q.id] === "b" ? "text-white/80" : "text-white/35 group-hover:text-white/55"}`}>{q.option_b}</p>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 底部导航 */}
      <div className="flex items-center justify-center gap-8">
        <button onClick={() => setIdx(Math.max(0, idx - 1))} disabled={idx === 0}
          className="inline-flex items-center gap-1.5 text-white/12 text-sm hover:text-white/30 transition-colors disabled:opacity-0">
          <ArrowLeft className="w-4 h-4" />上一题
        </button>

        <div className="flex gap-1.5">
          {Array.from({ length: 10 }).map((_, i) => {
            const g = idx > 0 ? Math.floor(idx / (questions.length / 10)) : 0;
            return <div key={i} className={`w-1 h-1 rounded-full transition-all duration-500 ${i <= g ? "bg-white/25" : "bg-white/[0.04]"}`} />;
          })}
        </div>

        {idx < questions.length - 1 ? (
          <button onClick={() => setIdx(idx + 1)}
            className="inline-flex items-center gap-1.5 text-white/15 text-sm hover:text-white/35 transition-colors">
            下一题<ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button onClick={submit}
            disabled={submitting || Object.keys(answers).length < 20}
            className="px-6 py-2 rounded-full bg-white text-[#030303] text-sm font-semibold hover:bg-white/90 transition-all disabled:opacity-20 disabled:cursor-not-allowed">
            {submitting ? "分析中..." : "查看结果"}
          </button>
        )}
      </div>
    </div>
  );
}
